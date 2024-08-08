import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import datetime
import plotly.express as px
import numpy as np

#function to plot interactive plotly chart
def plot_chart(df):
    figure = px.line()
    for i in df.columns[1:]:
        figure.add_scatter(x=df['Date'], y=df[i], name=i)
        figure.update_layout(width=450, margin=dict(l=20, r=20, t=50, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    return figure

#function to normalize the prices based on the initial price
def normalize(df_2):
    df = df_2.copy()
    for i in df.columns[1:]:
        df[i] = df[i] / df[i][0]
    return df

#function to calculate daily returns
def daily_return(df):
    df_daily_return = df.copy()
    for i in df.columns[1:]:
        for j in range(1, len(df)):
            df_daily_return[i][j] = ((df[i][j] - df[i][j-1]) / df[i][j-1]) * 100
    df_daily_return[i][0] = 0
    return df_daily_return

#function to calculate beta
def beta_calculation(stocks_daily_return, stock):
    rm = stocks_daily_return['sp500'].mean() * 252
    b, a = np.polyfit(stocks_daily_return['sp500'], stocks_daily_return[stock], 1)
    return b, a

st.set_page_config(page_title="CAPM", page_icon="chart_with_upwards_trend", layout='wide')
st.title("Capital Asset Pricing Model")
st.caption("The Capital Asset Pricing Model(CAPM) is a formula that helps investors calculate how much risk they're taking when they invest in a stock, based on the risk-free rate, the equity risk premium, and the stock's beta. It is a finance model that establishes a linear relationship between the required return on an investment and risk.")

#getting input from user
col1, col2 = st.columns([1,1])
with col1:
    stocks_list = st.multiselect(
        "Choose Stocks by ticker",
        ('AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'TSLA', 'META', 'GOOG', 'BRK', 'UNH', 'XOM', 'JNJ', 'JPM', 'V', 'LLY', 'AVGO', 'PG', 'MA', 'HD', 'MRK', 'CVX', 'PEP', 'COST', 'ABBV', 'KO', 'ADBE', 'WMT', 'MCD', 'CSCO', 'PFE', 'CRM', 'TMO', 'BAC', 'NFLX', 'ACN', 'A','DE', 'GS', 'ELV', 'LMT', 'AXP', 'BLK', 'SYK', 'BKNG', 'MDLZ', 'ADI', 'TJX', 'GILD', 'MMC', 'ADP', 'VRTX', 'AMT', 'C', 'CVS', 'LRCX', 'SCHW', 'CI', 'MO', 'ZTS', 'TMUS', 'ETN', 'CB', 'FI',
         'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'LT.NS', 'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'AXISBANK.NS', 'ITC.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'SUNPHARMA.NS', 'TATASTEEL.NS', 'ULTRACEMCO.NS', 'M&M.NS', 'WIPRO.NS'), 
        ['GOOGL', 'AAPL', 'MSFT', 'AMZN'])
with col2:
    year_list = st.number_input("Number of Years", 1, 10)

#downloading data for SP500
try:
    end_date = datetime.date.today()
    start_date = datetime.date(datetime.date.today().year - year_list, datetime.date.today().month, datetime.date.today().day)
    SP500 = web.DataReader(['sp500'], 'fred', start_date, end_date)

    stocks_df = pd.DataFrame()

    for stocks in stocks_list:
        data = yf.download(stocks, period=f'{year_list}y')
        stocks_df[f'{stocks}'] = data['Close']

    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)
    SP500.columns = ['Date', 'sp500']

    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    # Handle NaN values
    stocks_df.ffill(inplace=True)  # Forward fill
    stocks_df.dropna(inplace=True) # Drop remaining NaN values

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('### Dataframe Head')
        st.dataframe(stocks_df.head(7), use_container_width=True)
    with col2:
        st.markdown('### Dataframe Tail')
        st.dataframe(stocks_df.tail(7), use_container_width=True)

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('### Price of All the Charts')
        st.caption("initial stock prices")
        st.plotly_chart(plot_chart(stocks_df))
    with col2:
        st.markdown('### Price of All the Charts (After Normalizing)')
        st.caption("prices being normalized over initial stock prices")
        st.plotly_chart(plot_chart(normalize(stocks_df)))

    stocks_daily_return = daily_return(stocks_df)

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b, a = beta_calculation(stocks_daily_return, i)
            beta[i] = b
            alpha[i] = a

    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i, 2)) for i in beta.values()]
        
    with col1:
        st.markdown('### Calculated Beta Value')
        st.caption("market risk is considered as 1")
        st.dataframe(beta_df, use_container_width=True, hide_index=True)

    rf = 0
    #252 is the number of active trading days
    rm = stocks_daily_return['sp500'].mean() * 252

    return_df = pd.DataFrame()
    return_value = []
    for stock, value in beta.items():
        return_value.append(str(round(rf + (value * (rm - rf)), 2)))
    return_df['Stock'] = stocks_list

    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.caption("the risk-free rate + the beta (or risk) of the investment * the expected return on the market - the risk free rate")
        st.dataframe(return_df, use_container_width=True, hide_index=True)
except Exception as e:
    st.write(f"An error occurred: {e}")
    st.write("Please select at least 1 stock")
