import time
from oandapyV20 import API
from oandapyV20.endpoints.pricing import PricingStream
import numpy as np

# Constants
API_KEY = "your_api_key"
ACCOUNT_ID = "your_account_id"
INSTRUMENT = "EUR_USD"
PERIODS = [5, 10, 20, 50, 100]  # Rainbow EMA periods
TIMEFRAME = 1/3  # 1/3 second

# Connect to Oanda API
api = API(access_token=API_KEY)
def place_order(order_type, units, instrument, reduce_percentage=0):
    reduced_units = int(units * (1 - reduce_percentage))
    order_data = {
        'order': {
            'type': order_type,
            'units': str(reduced_units),
            'instrument': instrument,
            'timeInForce': 'FOK',  # Fill or Kill
            'positionFill': 'DEFAULT'
        }
    }

    order = OrderCreate(account_id, data=order_data)
    try:
        api.request(order)
    except V20Error as e:
        print(f"Error placing order: {e}")

def place_buy_order(units, instrument='EUR_USD', reduce_percentage=0):
    place_order('MARKET', units, instrument, reduce_percentage)

def place_sell_order(units, instrument='EUR_USD', reduce_percentage=0):
    place_order('MARKET', -units, instrument, reduce_percentage)

def reduce_position(current_position, reduce_percentage, instrument='EUR_USD'):
    order_type = 'MARKET'
    if current_position > 0:
        place_sell_order(current_position, instrument, reduce_percentage)
    elif current_position < 0:
        place_buy_order(-current_position, instrument, reduce_percentage)

# Function to calculate EMA
def calculate_ema(prices, period):
    ema = np.zeros_like(prices)
    ema[:period] = np.mean(prices[:period])
    multiplier = 2 / (period + 1)
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
    return ema

# Function to get price data
def get_price_data():
    response = api.request(PricingStream(ACCOUNT_ID, params={"instruments": INSTRUMENT}))
    for price_data in response:
        if price_data["type"] == "PRICE":
            return float(price_data["bids"][0]["price"])

# Main trading loop
def trading_loop():
    current_position = 0
    prices = []
    while True:
        current_price = get_price_data()
        prices.append(current_price)
        if len(prices) >= max(PERIODS):
            emas = [calculate_ema(np.array(prices[-period:]), period) for period in PERIODS]

            short_ema_above_50 = all([emas[i][-1] > emas[3][-1] for i in range(3)])
            short_ema_above_100 = all([emas[i][-1] > emas[4][-1] for i in range(3)])
            short_ema_below_50 = all([emas[i][-1] < emas[3][-1] for i in range(3)])
            short_ema_below_100 = all([emas[i][-1] < emas[4][-1] for i in range(3)])

            reduce_position_flag = short_ema_above_50 or short_ema_below_50
            reverse_position_flag = short_ema_above_100 or short_ema_below_100
            buy_flag = short_ema_above_50 and short_ema_above_100
            sell_flag = short_ema_below_50 and short_ema_below_100

            # Rule 2: Reduce position if all short-term EMAs cross the 50-day EMA
            current_position = (1 - reduce_position_flag * 0.5) * current_position
            reduce_position(reduce_position_flag * 0.5 * current_position)

            # Rule 3: Reverse position if all short-term EMAs cross the 100-day EMA
            current_position *= (1 - 2 * reverse_position_flag)
            reverse_position(reverse_position_flag * current_position)

            # Rule 4: Buy long or sell short based on the position of short-term EMAs
            place_buy_order(buy_flag * abs(current_position))
            current_position += buy_flag * abs(current_position)
            place_sell_order(sell_flag * abs(current_position))
            current_position -= sell_flag * abs(current_position)

        time.sleep(TIMEFRAME)

# User control loop
while True:
    user_input = input("Enter 'start' to start trading, 'stop' to stop, or 'pause' to pause: ").lower()
    if user_input == 'start':
        trading_loop()
    elif user_input == 'stop':
        break
    elif user_input == 'pause':
        time.sleep(TIMEFRAME)
