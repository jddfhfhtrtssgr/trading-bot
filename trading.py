import os
import time
import pandas as pd
import ta
from binance.client import Client

# Initialize Binance client with API key
binance = Client(api_key=os.environ['BINANCE_API_KEY'],
                 api_secret=os.environ['BINANCE_API_SECRET'])

# Define the asset to trade and interval
symbol = "BTCUSDT"
interval = Client.KLINE_INTERVAL_1HOUR

# Get historical price data
klines = binance.fetch_historical_klines(symbol, interval, "1 month ago UTC")
df = pd.DataFrame(klines, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])
df[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]].astype(float)
df["Date"] = pd.to_datetime(df["Close time"], unit='ms')
df = df.set_index("Date")

# Calculate technical indicators
df = ta.add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume")

# Generate trading signals
df['Signal'] = 0
df.loc[df["rsi"] > 70, 'Signal'] = -1
df.loc[df["rsi"] < 30, 'Signal'] = 1

# Execute trades
for i, row in df.iterrows():
    if row['Signal'] == 1:
        binance.order_market_buy(symbol=symbol, quantity=1)
    elif row['Signal'] == -1:
        binance.order_market_sell(symbol=symbol, quantity=1)
    time.sleep(60)
