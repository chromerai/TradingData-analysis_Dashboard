import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


cluster = Cluster(
    contact_points=["127.0.0.1"],
    auth_provider=PlainTextAuthProvider(username="cassandra", password="cassandra"),
)

session = cluster.connect()
session.set_keyspace("market")
session.row_factory = pandas_factory
session.default_fetch_size = 10000000  # needed for large queries, otherwise driver will do pagination. Default is 50000.


def fetch_ticker(ticker):
    rows = session.execute(f"""SELECT * FROM msc WHERE symbol={ticker};""")
    df = rows._current_rows
    return df


def line_plot(pdf, ticker):
    plt.figure(figsize=(10, 5))
    plt.plot(pdf["timestamp"], pdf["actual"], label="Actual")
    plt.plot(pdf["timestamp"], pdf["gbm"], label="Predicted")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(f"{ticker} Price Over Time")
    plt.legend()
    plt.show()


def histogram(pdf, ticker):
    plt.figure(figsize=(10, 5))
    plt.hist(pdf["gbm"], bins=30)
    plt.xlabel("Price")
    plt.ylabel("Frequency")
    plt.title(f"Distribution of Predicted Prices for {ticker}")
    plt.show()


def density_plot(pdf, ticker):
    pdf["gbm"].plot(kind="density")
    plt.xlabel("Price")
    plt.title(f"Density of Predicted {ticker} Prices")
    plt.show()


def generate_plots_for_ticker(ticker):
    df = fetch_ticker(ticker)
    line_plot(df, ticker)
    histogram(df, ticker)
    density_plot(df, ticker)


TICKERS = [
    "AAPL",
    "AMZN",
    "MSFT",
    "BINANCE:ETHUSDT",
    "BINANCE:BTCUSDT",
    "BINANCE:XRPUSDT",
    "BINANCE:DOGEUSDT",
]

if __name__ == "__main__":
    for ticker in TICKERS:
        generate_plots_for_ticker(ticker)
