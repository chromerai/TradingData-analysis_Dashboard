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
    fig, ax = plt.subplot()
    # plt.figure(figsize=(10, 5))
    ax.plot(pdf["timestamp"], pdf["actual"], label="Actual")
    ax.plot(pdf["timestamp"], pdf["gbm"], label="Predicted")
    ax.xlabel("Date")
    ax.ylabel("Price")
    ax.title(f"{ticker} Price Over Time")
    ax.legend()
    ax.show()
    st.pyplot(fig)

def histogram(pdf, ticker):
    fig, ax = plt.subplot()
#    plt.figure(figsize=(10, 5))
    ax.hist(pdf["gbm"], bins=30)
    ax.xlabel("Price")
    ax.ylabel("Frequency")
    ax.title(f"Distribution of Predicted Prices for {ticker}")
    ax.show()
    st.pyplot(fig)

def density_plot(pdf, ticker):
    fig, ax = pdf["gbm"].plot(kind="density")
    ax.xlabel("Price")
    ax.title(f"Density of Predicted {ticker} Prices")
    ax.show()
    st.pyplot(fig)


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

for ticker in TICKERS:
	st.title(f'GBM Analysis Visualization - {ticker}')
        generate_plots_for_ticker(ticker)
