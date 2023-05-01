import pyodbc
import pandas as pd
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles
import time

# Oanda API settings
api_key = 'your_api_key_here'
api = API(access_token=api_key)

# SQL server connection settings
server = 'your_server_name'
database = 'your_database_name'
username = 'your_username'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'
cnxn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Function to fetch historical data from Oanda
def fetch_historical_data(instrument, granularity, count):
    params = {
        'granularity': granularity,
        'count': count,
    }
    candles = InstrumentsCandles(instrument, params)
    api.request(candles)
    data = candles.response['candles']
    
    records = []
    for candle in data:
        records.append((candle['time'], candle['volume'], candle['mid']['o'], candle['mid']['h'], candle['mid']['l'], candle['mid']['c']))
    
    return records

# Function to store historical data in a SQL table
def store_historical_data(connection, table_name, data):
    cursor = connection.cursor()
    for record in data:
        cursor.execute(f'''
            IF NOT EXISTS (SELECT * FROM {table_name} WHERE Time=?)
                INSERT INTO {table_name} (Time, Volume, Open, High, Low, Close)
                VALUES (?, ?, ?, ?, ?, ?)
        ''', record, *record)
    connection.commit()
# Function to update historical data hourly
def update_historical_data_hourly(instrument, granularity, count):
    connection = pyodbc.connect(cnxn_str)
    
    # Create the "Historical_Price_Data" table if it doesn't exist
    cursor = connection.cursor()
    cursor.execute(f'''
        IF OBJECT_ID('dbo.{table_name}', 'U') IS NULL
            CREATE TABLE {table_name} (
                Time NVARCHAR(50) PRIMARY KEY,
                Volume INT,
                Open FLOAT,
                High FLOAT,
                Low FLOAT,
                Close FLOAT
            );
    ''')
    connection.commit()

while True:
        historical_data = fetch_historical_data(instrument, granularity, count)
        store_historical_data(connection, table_name, historical_data)
        print(f'Historical data updated at {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}')
        time.sleep(3600)  # Sleep for an hour

# Main settings
instrument = 'EUR_USD'
granularity = 'M5'
count = 5000
table_name = 'Historical_Price_Data'

# Start updating historical data hourly
update_historical_data_hourly(instrument, granularity, count)
