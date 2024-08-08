import streamlit as st
import pandas as pd
import backtrader as bt
import yfinance as yf
import inspect

# Define Strategies (reuse from backtest_page.py or import them)
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

# Initialize session state variables
def initialize_optimize_session():
    if 'strategies' not in st.session_state:
        st.session_state['strategies'] = [MovingAverageCrossover]
    if 'data' not in st.session_state:
        st.session_state['data'] = None
    if 'optimize_results' not in st.session_state:
        st.session_state['optimize_results'] = []

initialize_optimize_session()

def optimize_strategy(strategy, data_feed, initial_cash, commission, opt_params):
    cerebro = bt.Cerebro(optreturn=False)
    cerebro.adddata(data_feed)
    cerebro.optstrategy(strategy, **opt_params)
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    
    results = cerebro.run()
    
    return results

st.title('Optimizer')

st.write('Upload a CSV file with historical data or type a ticker symbol to optimize the strategies.')
st.write('The CSV file should have the following columns: Date, Open, High, Low, Close, Volume')

st.session_state['ticker'] = st.text_input('Ticker Symbol', st.session_state.get('ticker'))
st.session_state['start_date'] = st.date_input('Start Date', pd.to_datetime('2021-01-01'))
st.session_state['end_date'] = st.date_input('End Date', pd.to_datetime('2021-12-31'))

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

initial_cash = st.number_input('Initial Cash', value=10000)
commission = st.number_input('Broker Commission', value=0.001)

strategy_to_optimize = st.selectbox('Select Strategy to Optimize', [strat.__name__ for strat in st.session_state['strategies']])

# Define optimization parameters
st.write('Set Optimization Parameters:')
short_period = st.slider('Short Period', min_value=5, max_value=50, value=(10, 30))
long_period = st.slider('Long Period', min_value=20, max_value=100, value=(50, 70))

opt_params = {
    'short_period': range(short_period[0], short_period[1] + 1),
    'long_period': range(long_period[0], long_period[1] + 1)
}

if st.button("Run Optimization"):
    if not uploaded_file and not st.session_state['ticker']:
        st.warning("Please provide a ticker symbol or upload a CSV file with historical data.")
    else:
        if uploaded_file:
            st.session_state['data'] = pd.read_csv(uploaded_file, index_col='Date', parse_dates=True)
        else:
            st.session_state['data'] = yf.download(st.session_state['ticker'], start=st.session_state['start_date'], end=st.session_state['end_date'])

        if st.session_state['data'] is not None and not st.session_state['data'].empty:
            data_feed = bt.feeds.PandasData(dataname=st.session_state['data'])

            strategy_class = next(strat for strat in st.session_state['strategies'] if strat.__name__ == strategy_to_optimize)
            optimize_results = optimize_strategy(strategy_class, data_feed, initial_cash, commission, opt_params)

            # Process and display optimization results
            st.session_state['optimize_results'] = []
            for res in optimize_results:
                for strategy in res:
                    st.session_state['optimize_results'].append({
                        'Short Period': strategy.params.short_period,
                        'Long Period': strategy.params.long_period,
                        'Ending Value': strategy.broker.getvalue()
                    })

            results_df = pd.DataFrame(st.session_state['optimize_results'])
            st.write(results_df)
            st.line_chart(results_df.set_index(['Short Period', 'Long Period'])['Ending Value'])
        else:
            st.warning("No data available to run the optimization.")

