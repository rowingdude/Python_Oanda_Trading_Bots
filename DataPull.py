import requests
import json
import csv
import pandas as pd
from datetime import datetime

ACCESS_TOKEN = 'YOUR API TOKEN HERE'
ACCOUNT_ID = 'YOUR ACCOUNT ID HERE'
INSTRUMENT = 'EUR_USD'
FILENAME = 'oanda_data.csv'

def get_historical_data(count=5000, granularity='M5', to=None):
    """
    Fetch historical data from OANDA API
    """
    url = f"https://api-fxtrade.oanda.com/v3/instruments/{INSTRUMENT}/candles"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }

    params = {
        'count': count,
        'granularity': granularity,
        'price': 'BA',  # Bid and Ask prices
        'to': to
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error making request: {response.status_code}")
        return None

    return response.json()


def write_to_csv(data, filename=FILENAME):
    """
    Write data to a CSV file
    """
    fieldnames = ['time', 'volume', 'bid_open', 'bid_high', 'bid_low', 'bid_close', 'ask_open', 'ask_high', 'ask_low', 'ask_close']
    
    # Check if file already exists
    try:
        with open(filename, 'r') as csvfile:
            pass
    except FileNotFoundError:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    # Append new data
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for candle in data['candles']:
            row = {
                'time': candle['time'],
                'volume': candle['volume'],
                'bid_open': candle['bid']['o'],
                'bid_high': candle['bid']['h'],
                'bid_low': candle['bid']['l'],
                'bid_close': candle['bid']['c'],
                'ask_open': candle['ask']['o'],
                'ask_high': candle['ask']['h'],
                'ask_low': candle['ask']['l'],
                'ask_close': candle['ask']['c']
            }
            writer.writerow(row)


def get_earliest_timestamp(filename=FILENAME):
    """
    Get the earliest timestamp from the CSV file
    """
    try:
        df = pd.read_csv(filename)
        df['time'] = pd.to_datetime(df['time'])
        earliest_time = df['time'].min()
        return earliest_time.isoformat()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None


def main():
    while True:
        earliest_time = get_earliest_timestamp()
        data = get_historical_data(to=earliest_time)

        if data is not None and data['candles']:
            write_to_csv(data)
        else:
            break  # Stop if no more data


if __name__ == "__main__":
    main()
