# Main file for Finnhub API & Kafka integration
import os
import ast
import json
import websocket
from utils.functions import *


# proper class that ingests upcoming messages from Finnhub websocket into Kafka
class FinnhubProducer:
    def __init__(self):
        print("Environment:")
        for k, v in os.environ.items():
            print(f"{k}={v}")

        self.finnhub_client = load_client(os.environ["FINNHUB_API_TOKEN"])
        self.producer = load_producer(
            f"{os.environ['KAFKA_SERVER']}:{os.environ['KAFKA_PORT']}"
        )
        self.avro_schema = load_avro_schema(
            "/home/bigdata/TradingData-Dashboard/websocketCollector/src/schemas/trades.avsc"
        )
        self.tickers = ast.literal_eval(os.environ["FINNHUB_STOCKS_TICKERS"])
        self.validate = os.environ["FINNHUB_VALIDATE_TICKERS"]
        self.count = 0

        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f'wss://ws.finnhub.io?token={os.environ["FINNHUB_API_TOKEN"]}',
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_message(self, ws, message):
        message = json.loads(message)
        avro_message = avro_encode(
            {"data": message["data"], "type": message["type"]}, self.avro_schema
        )
        print(f"Data: {message['data']}, Type: {message['type']}")
        self.producer.send(os.environ["KAFKA_TOPIC_NAME"], avro_message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        for ticker in self.tickers:
            form = "{" + f'"type":"subscribe","symbol":"{ticker}"' + "}"
            if self.validate == "1":
                if ticker_validator(self.finnhub_client, ticker) == True:
                    self.ws.send(form)
                    print(f"Subscription for {ticker} succeeded")
                else:
                    print(f"Subscription for {ticker} failed - ticker not found")
            else:
                self.ws.send(form)


if __name__ == "__main__":
    FinnhubProducer()
