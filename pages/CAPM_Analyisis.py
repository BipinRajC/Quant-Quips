import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import plotly.graph_objects as go
import numpy as np
import groq
import os
import json

# Streamlit page configuration
st.set_page_config(page_title="CAPM", page_icon="chart_with_upwards_trend", layout='wide')

# Load API keys from config.json
working_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(working_dir, "config.json")

with open(config_file_path, 'r') as config_file:
    config_data = json.load(config_file)

GROQ_API_KEY = config_data["GROQ_API_KEY"]

# Initialize Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

def get_groq_response(question, context):
    if context is None:
        context = []
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": {"Question": question, "Context": context}}
        ]
    )
    return response.choices[0].message.content.strip()

def plot_capm_chart(us_beta_df, us_return_df, india_beta_df, india_return_df):
    fig = go.Figure()

    # Plot US stocks
    fig.add_trace(go.Scatter(
        x=us_beta_df['Beta Value'],
        y=us_return_df['Return Value'],
        mode='markers',
        name='US Stocks',
        text=us_return_df['Stock'],
        hovertemplate='%{text}<br>Beta: %{x}<br>Expected Return: %{y}%'
    ))

    # Plot India stocks
    fig.add_trace(go.Scatter(
        x=india_beta_df['Beta Value'],
        y=india_return_df['Return Value'],
        mode='markers',
        name='India Stocks',
        text=india_return_df['Stock'],
        hovertemplate='%{text}<br>Beta: %{x}<br>Expected Return: %{y}%'
    ))

    fig.update_layout(
        width=800,
        height=600,
        xaxis_title='Beta',
        yaxis_title='Expected Return',
        title='CAPM Analysis',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )

    return fig

def daily_return(df):
    df_daily_return = df.copy()
    for i in df.columns[1:]:
        df_daily_return[i] = df[i].pct_change() * 100
    df_daily_return.iloc[0] = 0
    return df_daily_return

def beta_calculation(stocks_daily_return, stock, base_index):
    rm = stocks_daily_return[base_index].mean() * 252
    b, a = np.polyfit(stocks_daily_return[base_index], stocks_daily_return[stock], 1)
    return b, a

st.title("Capital Asset Pricing Model")
st.caption("The Capital Asset Pricing Model (CAPM) is a formula that helps investors calculate how much risk they're taking when they invest in a stock, based on the risk-free rate, the equity risk premium, and the stock's beta. It is a finance model that establishes a linear relationship between the required return on an investment and risk.")

# Getting input from the user
col1, col2 = st.columns([1, 1])
with col1:
    stocks_list = st.multiselect(
        "Choose Stocks by ticker",
        ('AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'TSLA', 'META', 'GOOG', 'BRK', 'UNH', 'XOM', 'JNJ', 'JPM', 'V', 'LLY', 'AVGO', 'PG', 'MA', 'HD', 'MRK', 'CVX', 'PEP', 'COST', 'ABBV', 'KO', 'ADBE', 'WMT', 'MCD', 'CSCO', 'PFE', 'CRM', 'TMO', 'BAC', 'NFLX', 'ACN', 'A', 'DE', 'GS', 'ELV', 'LMT', 'AXP', 'BLK', 'SYK', 'BKNG', 'MDLZ', 'ADI', 'TJX', 'GILD', 'MMC', 'ADP', 'VRTX', 'AMT', 'C', 'CVS', 'LRCX', 'SCHW', 'CI', 'MO', 'ZTS', 'TMUS', 'ETN', 'CB', 'FI',
         'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'LT.NS', 'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'AXISBANK.NS', 'ITC.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'SUNPHARMA.NS', 'TATASTEEL.NS', 'ULTRACEMCO.NS', 'M&M.NS', 'WIPRO.NS'),
        ['GOOGL', 'AAPL', 'MSFT', 'TATASTEEL.NS', 'ULTRACEMCO.NS', 'WIPRO.NS'])
with col2:
    year_list = st.number_input("Number of Years", 1, 25, 10)

try:
    end_date = datetime.date.today()
    start_date = datetime.date(datetime.date.today().year - year_list, datetime.date.today().month, datetime.date.today().day)

    # Get the US and India stocks
    us_stocks = [stock for stock in stocks_list if not stock.endswith('.NS')]
    india_stocks = [stock for stock in stocks_list if stock.endswith('.NS')]

    # Fetch data for US and India stocks separately
    us_df = pd.DataFrame()
    for stock in us_stocks:
        try:
            data = yf.download(stock, period=f'{year_list}y')
            us_df[f'{stock}'] = data['Close']
        except Exception as e:
            st.write(f"Error fetching data for {stock}: {e}")

    india_df = pd.DataFrame()
    for stock in india_stocks:
        try:
            data = yf.download(stock, period=f'{year_list}y')
            india_df[f'{stock}'] = data['Close']
        except Exception as e:
            st.write(f"Error fetching data for {stock}: {e}")

    # Add S&P 500 and Nifty 50 data to the respective DataFrames
    try:
        sp500_data = yf.download('^GSPC', period=f'{year_list}y')
        us_df['sp500'] = sp500_data['Close']
    except Exception as e:
        st.write(f"Error fetching S&P 500 data: {e}")

    try:
        nifty50_data = yf.download('^NSEI', period=f'{year_list}y')
        india_df['NIFTY 50'] = nifty50_data['Close']
    except Exception as e:
        st.write(f"Error fetching Nifty 50 data: {e}")

    # Handle missing values
    us_df = us_df.dropna(subset=[col for col in us_df.columns if col != 'Date'])
    india_df = india_df.dropna(subset=[col for col in india_df.columns if col != 'Date'])

    # Process the data and calculate CAPM
    us_stocks_daily_return = daily_return(us_df)
    india_stocks_daily_return = daily_return(india_df)

    us_beta = {}
    us_alpha = {}
    for i in us_stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b, a = beta_calculation(us_stocks_daily_return, i, 'sp500')
            us_beta[i] = b
            us_alpha[i] = a

    india_beta = {}
    india_alpha = {}
    for i in india_stocks_daily_return.columns:
        if i != 'Date' and i != 'NIFTY 50':
            b, a = beta_calculation(india_stocks_daily_return, i, 'NIFTY 50')
            india_beta[i] = b
            india_alpha[i] = a

    us_beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    us_beta_df['Stock'] = us_beta.keys()
    us_beta_df['Beta Value'] = [str(round(i, 2)) for i in us_beta.values()]

    india_beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    india_beta_df['Stock'] = india_beta.keys()
    india_beta_df['Beta Value'] = [str(round(i, 2)) for i in india_beta.values()]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Calculated Beta Value (US Stocks)')
        st.caption("market risk is considered as 1")
        st.dataframe(us_beta_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown('### Calculated Beta Value (India Stocks)')
        st.caption("market risk is considered as 1")
        st.dataframe(india_beta_df, use_container_width=True, hide_index=True)

    us_rf = 0
    us_rm = us_stocks_daily_return['sp500'].mean() * 252

    india_rf = 0
    india_rm = india_stocks_daily_return['NIFTY 50'].mean() * 252

    us_return_df = pd.DataFrame()
    us_return_value = []
    for stock, value in us_beta.items():
        us_return_value.append(str(round(us_rf + (value * (us_rm - us_rf)), 2)))
    us_return_df['Stock'] = us_stocks
    us_return_df['Return Value'] = us_return_value

    india_return_df = pd.DataFrame()
    india_return_value = []
    for stock, value in india_beta.items():
        india_return_value.append(str(round(india_rf + (value * (india_rm - india_rf)), 2)))
    india_return_df['Stock'] = india_stocks
    india_return_df['Return Value'] = india_return_value

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Calculated Return using CAPM (US Stocks)')
        st.caption("the risk-free rate + the beta (or risk) of the investment * the expected return on the market - the risk free rate")
        st.dataframe(us_return_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown('### Calculated Return using CAPM (India Stocks)')
        st.caption("the risk-free rate + the beta (or risk) of the investment * the expected return on the market - the risk free rate")
        st.dataframe(india_return_df, use_container_width=True, hide_index=True)

    capm_chart = plot_capm_chart(us_beta_df, us_return_df, india_beta_df, india_return_df)
    st.plotly_chart(capm_chart, use_container_width=True)

    # Explanation of CAPM analysis
    st.subheader("Insights from the CAPM Analysis")
    st.write("The Capital Asset Pricing Model (CAPM) helps us understand the relationship between the expected return of a stock and its risk. The key metrics from the CAPM analysis are:")
    st.write("1. **Beta (β)**: This represents the systematic risk of the stock compared to the market. A beta greater than 1 indicates the stock is more volatile than the market, while a beta less than 1 indicates the stock is less volatile than the market.")
    st.write("2. **Expected Return**: The CAPM formula calculates the expected return of a stock based on its beta and the expected return of the market. This is the minimum return an investor should expect to receive for taking on the risk of the stock.")

    st.write("---")
    st.write("**US Stocks:**")
    for i, stock in enumerate(us_stocks):
        st.write(f"**{stock}**:")
        st.write(f"- Beta (β): {us_beta_df.loc[us_beta_df['Stock'] == stock, 'Beta Value'].values[0]}")
        st.write(f"- Expected Return: {us_return_df.loc[us_return_df['Stock'] == stock, 'Return Value'].values[0]}%")

        if float(us_beta_df.loc[us_beta_df['Stock'] == stock, 'Beta Value'].values[0]) > 1:
            st.write("This stock is more volatile than the market, so it has a higher risk and higher expected return.")
        else:
            st.write("This stock is less volatile than the market, so it has a lower risk and lower expected return.")

        st.write("---")

    st.write("**India Stocks:**")
    for i, stock in enumerate(india_stocks):
        st.write(f"**{stock}**:")
        st.write(f"- Beta (β): {india_beta_df.loc[india_beta_df['Stock'] == stock, 'Beta Value'].values[0]}")
        st.write(f"- Expected Return: {india_return_df.loc[india_return_df['Stock'] == stock, 'Return Value'].values[0]}%")

        if float(india_beta_df.loc[india_beta_df['Stock']== stock, 'Beta Value'].values[0]) > 1:
            st.write("This stock is more volatile than the market, so it has a higher risk and higher expected return.")
        else:
            st.write("This stock is less volatile than the market, so it has a lower risk and lower expected return.")

        st.write("---")

 

except Exception as e:
    st.write(f"An error occurred: {e}")
    st.write("Please select at least 1 stock and ensure the data is available.")