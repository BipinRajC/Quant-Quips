import backtrader as bt
import yfinance as yf
from datetime import datetime

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

def run_strategy(strategy, data_feed):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy)
    cerebro.broker.set_cash(10000)
    cerebro.broker.setcommission(commission=0.001)
    
    print(f'\nRunning {strategy.__name__} strategy')
    
    print('--------------------------------------------------')
    print("Starting Portfolio Cash: %.2f" % cerebro.broker.getcash())
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print("Final Portfolio Cash: %.2f" % cerebro.broker.getcash())
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.plot()

# Download data from Yahoo Finance
data = yf.download('AAPL', start='2015-01-01', end='2020-12-31')

# Convert the data to a format compatible with Backtrader
data_feed = bt.feeds.PandasData(dataname=data)

# Run each strategy
strategies = [MovingAverageCrossover, RSIStrategy, BollingerBandsStrategy, MACDStrategy]
for strategy in strategies:
    run_strategy(strategy, data_feed)
