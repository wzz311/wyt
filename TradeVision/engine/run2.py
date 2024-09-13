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
        self.slippage_multiple = 4
        self.symbols = None

    def backtest(self, df):
        ce = self.initial_capital
        result = []
        start = {symbol: None for symbol in self.symbols}
        end = {symbol: None for symbol in self.symbols}
        entry = {symbol: None for symbol in self.symbols}
        exit = {symbol: None for symbol in self.symbols}
        position = {symbol: 0 for symbol in self.symbols}
        pnl = {symbol: 0 for symbol in self.symbols}
        PNL = {symbol: 0 for symbol in self.symbols}
        shares = {symbol: 0 for symbol in self.symbols}

        for bar in df.itertuples(index=False, name="Row"):
            _s = bar.symbol
            if position[_s] == 0 and bar.lead == 1:
                if bar.LES:
                    buy = bar.open if bar.open >= bar.LE else (bar.LE if bar.high >= bar.LE else 0)
                    if buy:
                        start[_s] = bar.date
                        entry[_s] = math.ceil(buy / slippage[_s[:2]]) * slippage[_s[:2]]
                        position[_s] = 1
                        shares[_s] = round(ce * 0.01 / (bar.LE - bar.LX) / pointvalue[_s[:2]])

                if bar.SES:
                    sellshort = bar.open if bar.open <= bar.SE else (bar.SE if bar.low <= bar.SE else 0)
                    if sellshort:
                        start[_s] = bar.date
                        entry[_s] = math.floor(sellshort / slippage[_s[:2]]) * slippage[_s[:2]]
                        position[_s] = -1
                        shares[_s] = round(ce * 0.01 / (bar.SX - bar.SE) / pointvalue[_s[:2]])

            elif position[_s] == 1:
                if bar.LXS:
                    sell = bar.open if bar.open <= bar.LX else (bar.LX if bar.low <= bar.LX else 0)
                    if sell:
                        end[_s] = bar.date
                        exit[_s] = math.floor(sell / slippage[_s[:2]]) * slippage[_s[:2]]
                        pnl[_s] = exit[_s] - entry[_s]
                        PNL[_s] = (pnl[_s] - slippage[_s[:2]] * self.slippage_multiple - (
                                exit[_s] + entry[_s]) * self.commission_rate) * pointvalue[_s[:2]] * shares[_s]
                        ce += PNL[_s]

                        result.append(
                            [start[_s], end[_s], _s, entry[_s], exit[_s], position[_s], shares[_s],
                             pnl[_s], PNL[_s], ce])
                        position[bar.symbol] = 0

            elif position[bar.symbol] == -1:
                if bar.SXS:
                    buytocover = bar.open if bar.open >= bar.SX else (bar.SX if bar.high >= bar.SX else 0)
                    if buytocover:
                        end[_s] = bar.date
                        exit[_s] = math.floor(buytocover / slippage[_s[:2]]) * slippage[_s[:2]]
                        pnl[_s] = entry[_s] - exit[_s]
                        PNL[_s] = (pnl[_s] - slippage[_s[:2]] * self.slippage_multiple - (
                                exit[_s] + entry[_s]) * self.commission_rate) * pointvalue[_s[:2]] * shares[_s]
                        ce += PNL[_s]

                        result.append(
                            [start[_s], end[_s], _s, entry[_s], exit[_s], position[_s], shares[_s],
                             pnl[_s], PNL[_s], ce])
                        position[bar.symbol] = 0

        df = pd.DataFrame(result, columns=['start', 'end', 'symbol', 'entry', 'exit', "position", "shares",
                                           "pnl", "PNL", "ce"])
        return df
