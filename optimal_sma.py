# File for finding the best moving average periods for SMA strategy,
# to be used for the first 50 instruments


import talib
import numpy as np
import pandas as pd


COMMISSION = 0.005


prices = pd.read_csv("./prices250.txt", delimiter="\s+", header=None)
prices = prices.values.T


def get_signal(s, l, instrument_prices):
    prices = pd.Series(instrument_prices)

    # Generate signals corresponding to crossover of moving averages
    SMA_short = talib.SMA(prices, timeperiod=s).to_frame()
    SMA_long = talib.SMA(prices, timeperiod=l).to_frame()

    signal = SMA_long.copy()
    signal[SMA_long.isnull()] = 0
    signal[SMA_short > SMA_long] = 1
    signal[SMA_short < SMA_long] = -1

    return signal[0].iloc[-1]


for i in range(50):
    best_s_l = None
    best_profit = -0.10
    for s in [10, 20, 30, 40, 50]:
        for l in range(2 * s, 251, 10):
            total_value = 8000
            cash = 8000
            assets = 0
            current_pos = 0

            for day in range(250):
                prices_so_far = prices[i][:day + 1]
                signal = get_signal(s, l, prices_so_far)
                assets = current_pos * prices_so_far[-1]

                if current_pos == 0:
                    if signal == 1:
                        # Buy
                        new_pos = int(8000 / prices_so_far[-1])
                        cash -= (1 + COMMISSION) * new_pos * prices_so_far[-1]
                        assets += new_pos * prices_so_far[-1]
                        current_pos = new_pos
                else:
                    if signal == -1:
                        # Sell all
                        cash += (1 - COMMISSION) * current_pos * prices_so_far[-1]
                        assets = 0
                        current_pos = 0

                total_value = cash + assets

            profit = (total_value - 8000) / 8000

            if profit > best_profit:
                best_profit = profit
                best_s_l = {"short": s, "long": l}

    if best_s_l != None:
        print(f"(Instrument {i}) best periods: {best_s_l['short']}/"
              f"{best_s_l['long']}, best profit: {round(best_profit * 100, 2)}%")


