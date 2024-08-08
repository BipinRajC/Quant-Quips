import streamlit as st
import os
import json
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from groq import Groq
# Set page config
st.set_page_config(page_title="QuantQuips", page_icon="chart_with_upwards_trend", layout='wide')

# Load config
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def get_stock_data(ticker):
    """Fetch stock data and company info."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    company_info = stock.info
    return hist, company_info

def calculate_ratios(stock_data, company_info):
    """Calculate key financial ratios."""
    ratios = {}
    ratios['Price/Earnings'] = company_info.get('currentPrice', 0) / company_info.get('trailingEps', 0)
    ratios['Price/Book'] = company_info.get('currentPrice', 0) / company_info.get('bookValue', 0)
    ratios['Dividend Yield'] = company_info.get('dividendYield', 0)
    if company_info.get('totalDebt', 0) and company_info.get('totalEquity', 0):
        ratios['Debt/Equity'] = company_info['totalDebt'] / company_info['totalEquity']
    else:
        ratios['Debt/Equity'] = 'N/A'
    ratios['Current Ratio'] = company_info.get('currentRatio', 0)
    ratios['Return on Equity'] = company_info.get('returnOnEquity', 0)
    return ratios

def analyze_ratios_with_groq(ratios):
    """Use Groq AI to analyze financial ratios and provide insights."""
    # Construct the prompt for Groq
    query = f"""
    Analyze the following financial ratios and provide insights:
    - Price/Earnings: {ratios['Price/Earnings']:.2f}
    - Price/Book: {ratios['Price/Book']:.2f}
    - Dividend Yield: {ratios['Dividend Yield']:.2%}
    - Debt/Equity: {ratios['Debt/Equity']}
    - Current Ratio: {ratios['Current Ratio']:.2f}
    - Return on Equity: {ratios['Return on Equity']:.2%}
    """

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",  # Adjust model name as per your availability
        messages=[
            {"role": "system", "content": "You are a financial analyst.Eloquent and insightful analysis is expected. Will state facts only and will provide highly accurate opinions."},
            {"role": "user", "content": query}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("Smart Financial Analyst")
st.write("Enter a stock ticker for in-depth analysis with AI-generated insights.")

ticker = st.text_input("Enter a stock ticker (e.g., AAPL):")

if st.button("Get Advice"):
    with st.spinner("Gathering information..."):
        if ticker:
            # Get stock data and company info
            stock_data, company_info = get_stock_data(ticker)
            company_overview = {
                'companyName': company_info.get('longName', ''),
                'industry': company_info.get('industry', ''),
                'sector': company_info.get('sector', ''),
                'fullTimeEmployees': company_info.get('fullTimeEmployees', 0),
                'website': company_info.get('website', ''),
                'city': company_info.get('city', ''),
                'country': company_info.get('country', ''),
                'description': company_info.get('longBusinessSummary', '')
            }
            ratios = calculate_ratios(stock_data, company_info)

            # Display company overview
            st.subheader(f"Company Overview: {company_overview['companyName']}")
            st.write(f"**Industry:** {company_overview['industry']}")
            st.write(f"**Sector:** {company_overview['sector']}")
            st.write(f"**Employees:** {company_overview['fullTimeEmployees']}")
            st.write(f"**Website:** {company_overview['website']}")
            st.write(f"**Location:** {company_overview['city']}, {company_overview['country']}")
            st.write(f"**Description:** {company_overview['description']}")

            # Display financial ratios
            st.subheader("Financial Ratios")
            for key, value in ratios.items():
                st.write(f"**{key}:** {value if isinstance(value, str) else f'{value:.2f}'}")

            # Analyze ratios using Groq AI
            st.subheader("AI-Generated Insights")
            ai_analysis = analyze_ratios_with_groq(ratios)
            st.write(ai_analysis)

            # Plot stock price history
            st.subheader("Stock Price History")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price'))
            fig.update_layout(title=f"{ticker.upper()} Stock Price (Last 5 Years)", xaxis_title="Date", yaxis_title="Price (USD)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Please enter a stock ticker to get started.")

st.write(" \"This is not financial advice. Please consult with a financial advisor before making any investment decisions. This is just a demonstration of how Artificial Intelligence can assist in investment research and analysis.\"")
