import streamlit as st
import json
import os
from newsapi import NewsApiClient
import yfinance as yf
import groq

# Streamlit page configuration
st.set_page_config(page_title="QuantQuips", page_icon="chart_with_upwards_trend", layout='wide')

# Load API keys from config.json
working_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(working_dir, "config.json")

with open(config_file_path, 'r') as config_file:
    config_data = json.load(config_file)

GROQ_API_KEY = config_data["GROQ_API_KEY"]
NEWS_API_KEY = config_data["NEWS_API_KEY"]

# Initialize NewsApiClient and Groq client
newsapi = NewsApiClient(api_key=NEWS_API_KEY)
client = groq.Groq(api_key=GROQ_API_KEY)

def get_groq_response(question, context):
    if context is None:
        context = []
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a financial advisor."},
            {"role": "user", "content": {"Question": question, "Context": context}}
        ]
    )
    return response.choices[0].message.content.strip()

def fetch_latest_headlines(ticker):
    query = ticker
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
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Highly accurate and critical in your analysis."},
                {"role": "user", "content": f"Provide a qualitative analysis for the following question: {question} based on the context: {context}"}
            ],
            temperature=0.1,
        )
        print("API Response (Qualitative Analysis):", response)  # Debugging
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error in qualitative_analysis:", str(e))
        return "Analysis could not be completed. Please try again later."

def summarize_context(context):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert summarizer."},
                {"role": "user", "content": f"Summarize the following text: {context}"}
            ],
            temperature=0.1,
        )
        print("API Response (Summarize):", response)  # Debugging
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error in summarize_context:", str(e))
        return "Summary could not be completed. Please try again later."

# Streamlit UI elements
st.title("QuantQuips - Financial Insights")

# Dropdown for stock tickers
ticker = st.selectbox("Select a Stock Ticker:", ["AAPL", "GOOGL", "AMZN", "MSFT", "TSLA"])

if st.button("Fetch News & Analyze"):
    if ticker:
        st.subheader(f"Latest News for {ticker}")
        articles = fetch_latest_headlines(ticker)
        display_news_headlines(articles)
        
        if st.button("Analyze Latest Headlines"):
            combined_text = " ".join([article['description'] for article in articles if article['description']])
            analysis = qualitative_analysis("Provide a qualitative analysis.", combined_text)
            st.subheader("Analysis of the News Headlines")
            st.write(analysis)
        
        if st.button("Summarize Latest Headlines"):
            combined_text = " ".join([article['description'] for article in articles if article['description']])
            summary = summarize_context(combined_text)
            st.subheader("Summary of the News Headlines")
            st.write(summary)

