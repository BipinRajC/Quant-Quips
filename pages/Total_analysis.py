import streamlit as st
import json
import os
from newsapi import NewsApiClient
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import groq
st.set_page_config(page_title="QuantQuips", page_icon="chart_with_upwards_trend", layout='wide')
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]
NEWS_API_KEY = config_data["NEWS_API_KEY"]
JINA_API_KEY = config_data["JINA_API_KEY"]

client = groq.Groq(api_key=GROQ_API_KEY)

def get_groq_response(question,context):
    if context is None:
        context = []
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a financial advisor."},
            {"role": "user", "content":{"Question": question, "Context": context}}
        ]
    )
    return response.choices[0].message.content.strip()

def get_news_data(url:str):
    url = "https://r.jina.ai/"+url
    headers = {
    "Authorization": "Bearer " + JINA_API_KEY,
    "Accept": "application/json",
    }
    response = requests.get(url,headers=headers)
    
    return response.json()


def get_stock_data(ticker:str):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return hist

def qualitative_analysis(question:str,context:str):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a financial analyst. Highly accurate and critical in your analysis."},
            {"role": "user", "content": f"Provide a qualitative analysis for the following question: {question} based on the context: {context}"}
        ],
        temperature=0.1,
        
    )
    return response.choices[0].message.content.strip()

def summarize_context(context:str):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are an expert summarizer."},
            {"role": "user", "content": f"Summarize the following text: {context}"}
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()
