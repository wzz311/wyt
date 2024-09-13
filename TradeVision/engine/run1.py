import math
from global_parameters import *
import pandas as pd


class engine():
    def __init__(self):
        self.entry_type = "stop"
        self.exit_type = "stop"
        self.risk_min = 1
        self.initial_capital = 500000
        self.commission_rate = 0.0001
        self.slippage = 4
        self.symbol = None
        self.symbols = None

    def backtest(self, df):
        ce = self.initial_capital
        result = []
        start = 0
        end = 0
        entry = 0
        exit = 0
        position = 0

        for bar in df.itertuples(index=False, name="Row"):
            if position == 0:
                if bar.LES:
                    buy = bar.open if bar.open >= bar.LE else (bar.LE if bar.high >= bar.LE else 0)
                    if buy:
                        start = bar.date
                        entry = math.ceil(buy / slippage[self.symbol]) * slippage[self.symbol]
                        position = 1
                if bar.SES:
                    sellshort = bar.open if bar.open <= bar.SE else (bar.SE if bar.low <= bar.SE else 0)
                    if sellshort:
                        start = bar.date
                        entry = math.floor(sellshort / slippage[self.symbol]) * slippage[self.symbol]
                        position = -1
            elif position == 1:
                if bar.LXS:
                    sell = bar.open if bar.open <= bar.LX else (bar.LX if bar.low <= bar.LX else 0)
                    if sell:
                        end = bar.date
                        exit = math.floor(sell / slippage[self.symbol]) * slippage[self.symbol]

                        result.append(
                            [start, end, self.symbol, entry, exit, position])
                        position = 0
            elif position == -1:
                if bar.SXS:
                    buytocover = bar.open if bar.open >= bar.SX else (bar.SX if bar.high >= bar.SX else 0)
                    if buytocover:
                        end = bar.date
                        exit = math.floor(buytocover / slippage[self.symbol]) * slippage[self.symbol]

                        result.append(
                            [start, end, self.symbol, entry, exit, position])
                        position = 0

        df = pd.DataFrame(result, columns=['start', 'end', 'symbol', 'entry', 'exit', "position"])
        return df
