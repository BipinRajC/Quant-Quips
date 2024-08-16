import streamlit as st
import json
import os
from newsapi import NewsApiClient
import groq

# Streamlit page configuration
st.set_page_config(page_title="QuantQuips", page_icon="chart_with_upwards_trend", layout='wide')

# Load API keys from secrets.toml
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

# Initialize NewsApiClient and Groq client
newsapi = NewsApiClient(api_key=NEWS_API_KEY)
client = groq.Groq(api_key=GROQ_API_KEY)

def get_groq_response(question, context):
    if context is None:
        context = []
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a financial advisor."},
            {"role": "user", "content": {"Question": question, "Context": context}}
        ]
    )
    return response.choices[0].message.content.strip()

def fetch_latest_headlines(query):
    all_articles = newsapi.get_everything(q=query, language='en', sort_by='publishedAt')
    return all_articles['articles'][:5]

def display_news_headlines(articles):
    for article in articles:
        st.write(f"### {article['title']}")
        st.write(article['description'])
        st.write(f"[Read more]({article['url']})")
        st.write("---")

def qualitative_analysis(question, context):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Highly accurate and critical in your analysis."},
                {"role": "user", "content": f"Provide a qualitative analysis in pure markdown for the following question: {question} based on the context: {context}"}
            ],
            temperature=0.1,
        )
        #print("API Response (Qualitative Analysis):", response)  # Debugging
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error in qualitative_analysis:", str(e))
        return "Analysis could not be completed. Please try again later."

def summarize_context(context):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert summarizer."},
                {"role": "user", "content": f"Summarize the following text and return in markdown: {context}"}
            ],
            temperature=0.1,
        )
        #print("API Response (Summarize):", response)  # Debugging
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error in summarize_context:", str(e))
        return "Summary could not be completed. Please try again later."

# Streamlit UI elements
st.title("QuantQuips - Financial Insights")

# Text input for the news topic
news_topic = st.text_input("Enter a topic to get the latest financial news:")

if 'articles' not in st.session_state:
    st.session_state.articles = []

if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

if 'summary' not in st.session_state:
    st.session_state.summary = ""

if st.button("Fetch News & Analyze"):
    if news_topic:
        st.session_state.articles = fetch_latest_headlines(news_topic)
        st.subheader(f"Latest News for {news_topic}")
        display_news_headlines(st.session_state.articles)
        
if st.button("Analyze Latest Headlines"):
    if st.session_state.articles:
        combined_text = " ".join([article['description'] for article in st.session_state.articles if article['description']])
        st.session_state.analysis = qualitative_analysis("Provide a qualitative analysis.", combined_text)
        st.subheader("Analysis of the News Headlines")
        st.markdown(st.session_state.analysis)
    else:
        st.warning("Please fetch the latest news first.")

if st.button("Summarize Latest Headlines"):
    if st.session_state.articles:
        combined_text = " ".join([article['description'] for article in st.session_state.articles if article['description']])
        st.session_state.summary = summarize_context(combined_text)
        st.subheader("Summary of the News Headlines")
        st.markdown(st.session_state.summary)
    else:
        st.warning("Please fetch the latest news first.")