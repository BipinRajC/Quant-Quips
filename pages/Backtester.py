import matplotlib
matplotlib.use('agg')
import streamlit as st
import pandas as pd
import backtrader as bt
import yfinance as yf
import inspect

# Strategies
st.set_page_config(page_title="Backtester", page_icon="chart_with_upwards_trend", layout='wide')
class MovingAverageCrossover(bt.Strategy):
    params = (
        ('short_period', 10),
        ('long_period', 50),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        if self.crossover > 0:
            self.buy()
        elif self.crossover < 0:
            self.sell()

class RSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('overbought', 70),
        ('oversold', 30),
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.rsi_period)

    def next(self):
        if self.rsi < self.params.oversold:
            self.buy()
        elif self.rsi > self.params.overbought:
            self.sell()

class BollingerBandsStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2),
    )

    def __init__(self):
        self.bollinger = bt.indicators.BollingerBands(self.data.close, period=self.params.period, devfactor=self.params.devfactor)

    def next(self):
        if self.data.close < self.bollinger.lines.bot:
            self.buy()
        elif self.data.close > self.bollinger.lines.top:
            self.sell()

class MACDStrategy(bt.Strategy):
    params = (
        ('fast_ema', 12),
        ('slow_ema', 26),
        ('signal', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close, 
                                       period_me1=self.params.fast_ema, 
                                       period_me2=self.params.slow_ema, 
                                       period_signal=self.params.signal)

    def next(self):
        if self.macd.macd > self.macd.signal:
            self.buy()
        elif self.macd.macd < self.macd.signal:
            self.sell()

def initialize_session():
    if 'strategies' not in st.session_state:
        st.session_state['strategies'] = [MovingAverageCrossover, RSIStrategy, BollingerBandsStrategy, MACDStrategy]
    if 'data' not in st.session_state:
        st.session_state['data'] = None
    if 'results' not in st.session_state:
        st.session_state['results'] = []
    if 'new_strategy_code' not in st.session_state:
        st.session_state['new_strategy_code'] = ""
    if 'strategies_to_run' not in st.session_state:
        st.session_state['strategies_to_run'] = [strat.__name__ for strat in st.session_state['strategies']]

initialize_session()

def run_strategy(strategy, data_feed, initial_cash, commission):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy)
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    
    starting_value = cerebro.broker.getvalue()
    cerebro.run()
    figure = cerebro.plot(dpi=1000)[0][0]
    ending_value = cerebro.broker.getvalue()

    return {
        'Strategy': strategy.__name__,
        'Starting Value': starting_value,
        'Ending Value': ending_value
    }, {'figure':figure,
        'name':strategy.__name__}

st.title('Backtester')

st.write('Upload a CSV file with historical data or type a ticker symbol to backtest the strategies.')
st.write('The CSV file should have the following columns: Date, Open, High, Low, Close, Volume')

st.session_state['ticker'] = st.text_input('Ticker Symbol', st.session_state.get('ticker', ''))
st.session_state['start_date'] = st.date_input('Start Date', pd.to_datetime('2021-01-01'))
st.session_state['end_date'] = st.date_input('End Date', pd.to_datetime('2021-12-31'))

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

initial_cash = st.number_input('Initial Cash', value=10000)
commission = st.number_input('Broker Commission', value=0.001)

strategies_to_run = st.multiselect('Select Strategies to Run', [strat.__name__ for strat in st.session_state['strategies']], default=st.session_state['strategies_to_run'])

st.session_state['new_strategy_code'] = st.text_area("Paste your strategy class code here", st.session_state['new_strategy_code'], height=300)

if st.button("Upload Strategy"):
    try:
        exec(st.session_state['new_strategy_code'], globals())
        # Find the newly uploaded class by finding the last class defined
        new_classes = [cls for cls in globals().values() if inspect.isclass(cls) and issubclass(cls, bt.Strategy) and cls.__module__ == '__main__']
        if not new_classes:
            st.warning("Please paste a valid Backtrader strategy class for testing.")
        else:
            new_strategy_class = new_classes[-1]
            if new_strategy_class not in st.session_state['strategies']:
                st.session_state['strategies'].append(new_strategy_class)
                st.session_state['strategies_to_run'].append(new_strategy_class.__name__)
                st.success(f"Uploaded strategy: {new_strategy_class.__name__}")
            else:
                st.warning("This strategy is already uploaded.")
    except Exception as e:
        st.warning(f"An error occurred: {e}")

if st.button("Run Backtest"):
    if not uploaded_file and not st.session_state['ticker']:
        st.warning("Please provide a ticker symbol or upload a CSV file with historical data.")
    else:
        if uploaded_file:
            st.session_state['data'] = pd.read_csv(uploaded_file, index_col='Date', parse_dates=True)
        else:
            st.session_state['data'] = yf.download(st.session_state['ticker'], start=st.session_state['start_date'], end=st.session_state['end_date'])

        if st.session_state['data'] is not None and not st.session_state['data'].empty:
            data_feed = bt.feeds.PandasData(dataname=st.session_state['data'])

            st.session_state['results'] = []
            st.session_state['fig'] = []
            for strategy_name in strategies_to_run:
                strategy_class = next(strat for strat in st.session_state['strategies'] if strat.__name__ == strategy_name)
                result, figure = run_strategy(strategy_class, data_feed, initial_cash, commission)
                st.session_state['results'].append(result)
                st.session_state['fig'].append(figure)

            results_df = pd.DataFrame(st.session_state['results'])
            
            st.table(results_df)
            col1,col2 = st.columns(2)
            with col1:
                for i in range(0,2):
                    with st.container(height=500):
                        st.subheader(st.session_state['fig'][i]['name'])
                        st.pyplot(st.session_state['fig'][i]['figure'])
            with col2:
                for i in range(2,4):
                    with st.container(height=500):
                        st.subheader(st.session_state['fig'][i]['name'])
                        st.pyplot(st.session_state['fig'][i]['figure'])
        else:
            st.warning("No data available to run the backtest.")
