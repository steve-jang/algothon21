import pandas as pd
from matplotlib import pyplot as plt

prices_file = "./prices250.txt"
df = pd.read_csv(prices_file, delimiter="\s+", header=None)
prices = df.values.T

# Summary of Strategy:
# The super volatile instruments indexed from 50 onwards all behave in a
# way such that whenever a "significant" dip in price occurs, a significant
# spike follows. Hence, we take the following steps:
#  - Find the expected value of the relative decrease in price during dips
#  - If the current day is during a significant price dip (say by at least
#  - 1 SD) then buy
#  - Wait a few days until the price spikes up significantly (which also has
#    to be more than the amount of money corresponding to the loss due to
#    commission), then sell all

### Constants
# Percent of $10K bought at a dip
BUY_PERCENTAGE = 0.8
BUY_LIMIT = 10000
COMMISSION = 0.005

# Price dip threshold - defines when a dip occurs/finishes
# E.g. a price dip starts if the price drops by more than 3%, ends
# if it rises by more than 3%
DIP_START = 0.98
DIP_END = 1.02
DIP_THRESHOLD = 0.995

# Days to look back to see if current day is in a dip
LOOK_BACK_DAYS = 8

# Dip durations to look back to decide if current day is in dip
LOOK_BACK_DIPS = 2

# Min relative gain for selling
SELL_THRESHOLD = 0.03

# Min drop for selling at a loss
LOSS_THRESHOLD = 0.96

# Min relative drop for buying
BUY_THRESHOLD = 0.97


# List to store most recent buy price of instruments
buy_prices = [-1 for _ in range(100)]


# Find various statistics of price dips and spikes of the instrument with given
# price history, and return it as a dict of the form
# { mean_dip, mean_dip_duration }, where
# - mean_dip is the mean relative decrease in price between the
#   start of the dip and the bottom of the dip (as a percentage),
# - mean_dip_duration is the average duration in days between dips,
def price_dip_stats(instrument_prices):
    # Store as positive values
    price_dips = []
    price_dip_days = []

    prev_price = 0
    dip_start = 0
    dip_end = 0
    dip_end_index = 0
    for i, p in enumerate(instrument_prices):
        if i == 0:
            # Initial prices
            prev_price = p
            dip_start = p
            dip_end = p
            dip_end_index = i
            continue

        if dip_end / dip_start <= DIP_START and p / dip_end >= DIP_END:
            # Price rose sufficiently since lowest point in dip and price
            # dropped sufficiently between start and bottom of dip - this is
            # the end of dip, may be a start of a new dip
            price_dips.append(dip_end / dip_start)
            dip_start = p
            dip_end = p
            price_dip_days.append(dip_end_index)
            dip_end_index = i
        elif p / dip_start >= DIP_THRESHOLD:
            # Price rose sufficiently back to the price at start of dip,
            # without dipping sufficiently - this dip does not count, start
            # a new dip
            dip_start = p
            dip_end = p
            dip_end_index = i

        if p < dip_end:
            # Price dropped from previously thought end of dip - update
            dip_end = p
            dip_end_index = i

    # Find expected (average) of price dip
    if len(price_dips) == 0:
        return {
            "mean_dip": None,
            "mean_dip_duration": None,
        }

    mean_dip = sum(price_dips) / len(price_dips)

    # Find mean duration in days between dips
    duration = (price_dip_days[-1] - price_dip_days[0]) / len(price_dip_days)

    return {
        "mean_dip": mean_dip,
        "mean_dip_duration": duration,
    }


# Return new position of instrument, given the price history of the
# instrument and the current position.
def get_new_position(index, prices_so_far, current_pos):
    global buy_prices
    current_price = prices_so_far[-1]
    buy_price = buy_prices[index]

    # Need to determine selling/buying - for the super volatile instruments,
    # when selling happens, all holdings of the instrument are sold
    new_pos = current_pos
    if current_pos == 0:
        # Potential buy
        if in_dip(prices_so_far):
            # Buy in the dip
            new_pos = int(BUY_PERCENTAGE * BUY_LIMIT / current_price)
            buy_prices[index] = current_price
    else:
        # Potential sell
        # Calculate total commission if selling took place
        commission = (COMMISSION * current_pos *
                      (buy_price + current_price))
        relative_gain = ((current_price - buy_price) * current_pos -
                         commission) / (buy_price * current_pos)

        if relative_gain >= SELL_THRESHOLD:
            # Sell all
            new_pos = 0
        elif current_price / buy_price <= LOSS_THRESHOLD:
            # Sell all, bought at wrong time, so minimise loss
            new_pos = 0

    return new_pos


# Return true if in a dip, compared to a range of days in the past, false
# otherwise.
def in_dip(prices_so_far):
    current_price = prices_so_far[-1]
    dip_stats = price_dip_stats(prices_so_far)
    mean_dip = dip_stats["mean_dip"]
    duration = dip_stats["mean_dip_duration"]

    if duration == None:
        duration = LOOK_BACK_DAYS
    else:
        duration = round(LOOK_BACK_DIPS * duration)

    for i in range(duration):
        day = len(prices_so_far) - 2 - i
        if day < 0:
            break

        if mean_dip != None:
            if current_price / prices_so_far[day] <= mean_dip:
                return True
        elif current_price / prices_so_far[day] <= BUY_THRESHOLD:
            return True

    return False

