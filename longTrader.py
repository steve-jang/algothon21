import talib
import pandas as pd
from datetime import date, timedelta
from optimal_sma import get_all_optimal_sma_periods

BUY_LIMIT = 10000
BUY_PERCENTAGE = 0.8

# Best strategies found for each of the first 50 instruments,
# using another algorithm
instrument_strategies = [None for _ in range(50)]

# Instruments where RSI strategy proved effective
for i in [1, 3, 9, 11, 13, 14, 16, 17, 19, 21, 23, 24, 27, 29, 30, 31, 35, 42, 44, 47]:
    instrument_strategies[i] = {"strategy": "RSI"}

# Instruments where SMA strategy with optimised short and long moving
# average periods proved effective
instrument_strategies[0] = {"strategy": "SMA", "short": 10, "long": 60}
instrument_strategies[5] = {"strategy": "SMA", "short": 10, "long": 50}
instrument_strategies[6] = {"strategy": "SMA", "short": 50, "long": 160}
instrument_strategies[7] = {"strategy": "SMA", "short": 10, "long": 20}
instrument_strategies[8] = {"strategy": "SMA", "short": 10, "long": 100}
instrument_strategies[12] = {"strategy": "SMA", "short": 30, "long": 120}
instrument_strategies[15] = {"strategy": "SMA", "short": 20, "long": 50}
instrument_strategies[18] = {"strategy": "SMA", "short": 10, "long": 30}
instrument_strategies[19] = {"strategy": "SMA", "short": 30, "long": 170}
instrument_strategies[22] = {"strategy": "SMA", "short": 10, "long": 30}
instrument_strategies[23] = {"strategy": "SMA", "short": 50, "long": 230}
instrument_strategies[25] = {"strategy": "SMA", "short": 10, "long": 20}
instrument_strategies[26] = {"strategy": "SMA", "short": 20, "long": 60}
instrument_strategies[28] = {"strategy": "SMA", "short": 40, "long": 140}
instrument_strategies[32] = {"strategy": "SMA", "short": 10, "long": 60}
instrument_strategies[33] = {"strategy": "SMA", "short": 30, "long": 140}
instrument_strategies[34] = {"strategy": "SMA", "short": 30, "long": 160}
instrument_strategies[39] = {"strategy": "SMA", "short": 50, "long": 160}
instrument_strategies[40] = {"strategy": "SMA", "short": 10, "long": 130}
instrument_strategies[41] = {"strategy": "SMA", "short": 20, "long": 70}
instrument_strategies[43] = {"strategy": "SMA", "short": 30, "long": 60}
instrument_strategies[45] = {"strategy": "SMA", "short": 50, "long": 140}
instrument_strategies[48] = {"strategy": "SMA", "short": 10, "long": 60}


def get_new_position(index, prices_so_far, current_pos):
    strategy = instrument_strategies[index]

    if strategy == None:
        # No optimal strategy found, don't change current position
        return current_pos

    new_signal = get_new_signal(strategy, prices_so_far)
    new_pos = current_pos
    current_price = prices_so_far[-1]

    if current_pos == 0:
        if new_signal == 1:
            # Buy
            new_pos = int(BUY_LIMIT * BUY_PERCENTAGE / prices_so_far[-1])
    else:
        if new_signal == -1:
            # Sell all
            new_pos = 0

    return new_pos


def get_new_signal(strategy, instrument_prices):
    prices = pd.Series(instrument_prices)
    strategy_type = strategy["strategy"]

    if strategy_type == "RSI":
        inst1_rsi = talib.RSI(prices).to_frame()

        # Create the same DataFrame structure as RSI
        signal = inst1_rsi.copy()
        signal[inst1_rsi.isnull()] = 0

        # Construct the signal
        # long signal
        signal[inst1_rsi < 30] = 1

        # short signal
        signal[inst1_rsi > 70] = -1

        # hold signal
        signal[(inst1_rsi <= 70) & (inst1_rsi >= 30)] = 0
    elif strategy_type == "SMA":
        # Generate signals corresponding to crossover of moving averages
        short_period = strategy["short"]
        long_period = strategy["long"]
        SMA_short = talib.SMA(prices, timeperiod=short_period).to_frame()
        SMA_long = talib.SMA(prices, timeperiod=long_period).to_frame()

        signal = SMA_long.copy()
        signal[SMA_long.isnull()] = 0
        signal[SMA_short > SMA_long] = 1
        signal[SMA_short < SMA_long] = -1

    return signal[0].iloc[-1]

