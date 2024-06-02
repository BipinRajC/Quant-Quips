import streamlit as st 
import backtrader as bt




import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Data Board", page_icon="chart_with_upwards_trend", layout='wide')

def fetch_realtime_stock_data(ticker_symbol, period, interval):
    current_time = datetime.now().time()
    try:
        stock_data = yf.download(ticker_symbol, period=period, interval=interval)
    except Exception as e:
        if "15m data not available" in str(e):
            st.warning(f"15-minute data not available for the specified period. Fetching hourly data instead.")
            stock_data = yf.download(ticker_symbol, period=period, interval="1h")
        else:
            raise
    return stock_data

default_period = "1d"
default_interval = "1m"

nse_ticker_symbol = "^NSEI"
sensex_ticker_symbol = "^BSESN"

def calculate_percentage_change(stock_data):
    return (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0] * 100

nse_stock_data = fetch_realtime_stock_data(nse_ticker_symbol, default_period, default_interval)
sensex_stock_data = fetch_realtime_stock_data(sensex_ticker_symbol, default_period, default_interval)

nse_percentage_change = calculate_percentage_change(nse_stock_data)
sensex_percentage_change = calculate_percentage_change(sensex_stock_data)

overall_market_condition = 'Bullish' if nse_percentage_change > 0 and sensex_percentage_change > 0 else 'Bearish'

def plot_chart(stock_data, title, subheader):
    fig = px.line(stock_data, x=stock_data.index, y="Close", title=title)
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Closing Price')
    st.subheader(subheader)
    if overall_market_condition == 'Bullish':
        fig.update_traces(line_color='light-blue')
    else:
        fig.update_traces(line_color='red')
    st.plotly_chart(fig, use_container_width=True, width=1200)
    st.subheader(f"Latest Data for {title}")
    st.write(stock_data.tail())

st.subheader(f"Overall Market Condition: {overall_market_condition}")

if nse_stock_data is not None and sensex_stock_data is not None:
    col1, col2 = st.columns(2)

    with col1:
        plot_chart(nse_stock_data, "Real-time Nifty Chart", "Real-time Nifty Chart:")

    with col2:
        plot_chart(sensex_stock_data, "Real-time Sensex Chart", "Real-time Sensex Chart:")
else:
    st.warning("Nifty or Sensex market is closed. Real-time data is available only during market hours.")

st.write("Auto-refreshing every 1 minute.")

ticker_needed = st.selectbox("Select a stock ticker", ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA","NVDA"], index=None)

if not ticker_needed:
    with st.spinner("Enter a stock ticker to fetch data"):
        ticker_needed = st.text_input("Enter a stock ticker")
        

try:
    ticker_needed = yf.Ticker(ticker_needed)
    ticker_info = ticker_needed.info
    hist = ticker_needed.history(period="1y")
    st.write("Meta Information:", ticker_info)
    st.write("Historical Data:", hist)
except Exception as e:
    st.error(f"Failed to fetch data for {ticker_needed}. Error: {e}")

st.write("Financial Statements and Holder Information can be accessed via the Ticker object methods.")
