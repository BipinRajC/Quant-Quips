import streamlit as st 
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px
st.set_page_config(page_title="Data Board", page_icon="chart_with_upwards_trend", layout='wide')

# Function to fetch real-time stock data during market hours
def fetch_realtime_stock_data(ticker_symbol, period, interval):
    current_time = datetime.now().time()
    
    try:
            stock_data = yf.download(ticker_symbol, period=period, interval=interval)
    except Exception as e:
            # Retry with a different interval if the initial request fails
            if "15m data not available" in str(e):
                st.warning(f"15-minute data not available for the specified period. Fetching hourly data instead.")
                stock_data = yf.download(ticker_symbol, period=period, interval="1h")
            else:
                raise
    return stock_data
    

# Default values for period and interval
default_period = "1d"
default_interval = "1m"

# Fetch and display real-time stock data for NSE
nse_ticker_symbol = "^NSEI"
nse_stock_data = fetch_realtime_stock_data(nse_ticker_symbol, default_period, default_interval)

# Fetch and display real-time stock data for Sensex
sensex_ticker_symbol = "^BSESN"
sensex_stock_data = fetch_realtime_stock_data(sensex_ticker_symbol, default_period, default_interval)

# Calculate the percentage change for NSE
nse_percentage_change = (nse_stock_data['Close'].iloc[-1] - nse_stock_data['Close'].iloc[0]) / nse_stock_data['Close'].iloc[0] * 100

# Calculate the percentage change for Sensex
sensex_percentage_change = (sensex_stock_data['Close'].iloc[-1] - sensex_stock_data['Close'].iloc[0]) / sensex_stock_data['Close'].iloc[0] * 100

# Determine overall market condition
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
    st.write(stock_data.tail())  # Display the last rows of the DataFrame


# Display overall market condition and real-time stock charts
st.subheader(f"Overall Market Condition: {overall_market_condition}")

    # Display NSE and Sensex charts side by side with larger width
if nse_stock_data is not None and sensex_stock_data is not None:
    col1, col2 = st.columns(2)

    with col1:
        plot_chart(nse_stock_data, "Real-time Nifty Chart", "Real-time Nifty Chart:")

    with col2:
        plot_chart(sensex_stock_data, "Real-time Sensex Chart", "Real-time Sensex Chart:")
else:
    st.warning("Nifty or Sensex market is closed. Real-time data is available only during market hours.")
st.write("Auto-refreshing every 1 minute.")

ticker_needed = st.selectbox("Select a stock ticker", ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA","NVDA"])  
ticker_needed=st.text_input("Enter a stock ticker")


ticker_needed = yf.Ticker(ticker_needed)
ticker_info = ticker_needed.info
ticker_needed.info

# get historical market data
hist = ticker_needed.history(period="1mo")

# show meta information about the history (requires history() to be called first)
ticker_needed.history_metadata

# show actions (dividends, splits, capital gains)
ticker_needed.actions
ticker_needed.dividends
ticker_needed.splits
ticker_needed.capital_gains  # only for mutual funds & etfs

# show share count
ticker_needed.get_shares_full(start="2022-01-01", end=None)

# show financials:
# - income statement
ticker_needed.income_stmt
ticker_needed.quarterly_income_stmt
# - balance sheet
ticker_needed.balance_sheet
ticker_needed.quarterly_balance_sheet
# - cash flow statement
ticker_needed.cashflow
ticker_needed.quarterly_cashflow
# see `Ticker.get_income_stmt()` for more options

# show holders
ticker_needed.major_holders
ticker_needed.institutional_holders
ticker_needed.mutualfund_holders
ticker_needed.insider_transactions
ticker_needed.insider_purchases
ticker_needed.insider_roster_holders

# show recommendations
ticker_needed.recommendations
ticker_needed.recommendations_summary
ticker_needed.upgrades_downgrades