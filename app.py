import streamlit as st
import json
import os
from newsapi import NewsApiClient
from openai import OpenAI
import requests
import yfinance as yf
import matplotlib.pyplot as plt
st.set_page_config(page_title="QuantQuips", page_icon="chart_with_upwards_trend", layout='wide')
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/pages/config.json"))
OPENAI_API_KEY = config_data["OPENAI_API_KEY"]
NEWS_API_KEY = config_data["NEWS_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)


def get_openai_response(question):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a financial advisor."},
        {"role": "user", "content": question}
    ])
    return response.choices[0].message.content.strip()

def get_news_data(query):
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    all_articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy')
    return all_articles['articles']

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return hist

def qualitative_analysis(question):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a financial analyst."},
        {"role": "user", "content": f"Provide a qualitative analysis for the following question: {question}"}
    ])
    return response.choices[0].message.content.strip()

def summarize_text(text):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert summarizer."},
        {"role": "user", "content": f"Summarize the following text: {text}"}
    ])
    return response.choices[0].message.content.strip()

def analyze_sentiment(text):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert in sentiment analysis."},
        {"role": "user", "content": f"Analyze the sentiment of the following text: {text}"}
    ])
    return response.choices[0].message.content.strip()

def extract_keywords(text):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert in keyword extraction."},
        {"role": "user", "content": f"Extract the main keywords from the following text: {text}"}
    ])
    return response.choices[0].message.content.strip()



st.title("Smart Financial Advisor")
st.write("Ask me any finance-related question!")

question = st.text_input("Enter your question:")
ticker = st.text_input("Enter a stock ticker (e.g., AAPL):")

if st.button("Get Advice"):
    with st.spinner("Gathering information..."):
        openai_response = get_openai_response(question)
        qualitative_analysis_result = qualitative_analysis(question)
        news_data = get_news_data(question)

        if ticker:
            stock_data = get_stock_data(ticker)
            stock_summary = f"Showing stock data for {ticker.upper()}"
        else:
            stock_data = None
            stock_summary = "No stock ticker provided."

        if news_data:
            top_article = news_data[0]
            article_title = top_article['title']
            article_description = top_article['description']
            article_content = top_article['content']

            article_summary = summarize_text(article_content)
            article_sentiment = analyze_sentiment(article_content)
            article_keywords = extract_keywords(article_content)
        else:
            article_title = article_description = article_content = ""
            article_summary = article_sentiment = article_keywords = "No news articles found."

    st.subheader("OpenAI Response:")
    st.write(openai_response)

    st.subheader("Qualitative Analysis:")
    st.write(qualitative_analysis_result)

    st.subheader("News Analysis:")
    st.write(f"**Title:** {article_title}")
    st.write(f"**Description:** {article_description}")
    st.write(f"**Content:** {article_content}")
    st.write(f"**Summary:** {article_summary}")
    st.write(f"**Sentiment:** {article_sentiment}")
    st.write(f"**Keywords:** {article_keywords}")

    st.subheader("Stock Data Analysis:")
    st.write(stock_summary)
    if stock_data is not None:
        st.line_chart(stock_data['Close'])

        plt.figure(figsize=(10, 5))
        plt.plot(stock_data.index, stock_data['Close'])
        plt.title(f"{ticker.upper()} Stock Price (Last 1 Year)")
        plt.xlabel("Date")
        plt.ylabel("Close Price (USD)")
        plt.grid(True)
        st.pyplot(plt)






st.write(" \"This is not a financial advice. Please consult with a financial advisor before making any investment decisions. This is just a demonstration of how Artifical intelligence helps in making investment decisions.")