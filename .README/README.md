# Real Time Stream Processing and Analysis of Trading Data
**CSGY-6513 Big Data Spring 2023, Final Project (Group 3)**

* Superset Dashboard with live data stream can be accessed at the following link: http://155.138.134.6:8088/superset/dashboard/11/
    * User: demo
    * Password: bigdatafinalproject
* The Streamlit dashboard with the Monte Carlo based Geometric Brownian motion analysis of trade data can be accessed at the following link: http://155.138.134.6/streamlit
## Metrics
* 10 records per second fetched from the websocket connection
* 100 kb/sec of data being passed through the pipeline for visualization
* 360 mb/hr of data being passed through the pipeline
---
**NOTE**: *above metrics are valid for pipeline being run for 7 tickers - AAPL, AMZN, MSFT, BINANCE:ETHUSDT, BINANCE:BTCUSDT, BINANCE:XRPUSDT, BINANCE:DOGEUSDT*
## Project Description
This project consists of a real-time data processing pipeline that is structured into the following main layers:

1. **Data ingestion layer:** This is the first layer of the pipeline, where real-time stock market data is fetched. A Python application is used for this purpose. The application connects to Finnhub.io websocket and retrieves real-time data. This data is then encoded into Avro format as per the specifications in the schemas/trades.avsc file. The encoded data is then published to a Kafka broker for further processing.
2. **Message broker layer:** Kafka serves as the message broker in this pipeline. It receives messages from the FinnhubProducer application and queues them for consumption by the stream processing layer. The Kafka broker runs in a docker-container called kafka-service. This is orchestrated using docker compose. It also contains a Kafdrop service as a sidecar ambassador container to provide a graphical interface for Kafka. A Zookeeper pod is also launched before Kafka to manage its metadata.
3. **Stream processing layer:** This layer is responsible for processing the real-time data. It utilizes a Spark cluster that is deployed on docker and orchestrated using dockre compose. A Scala application, StreamProcessor, is submitted to the Spark cluster. This application retrieves messages from the Kafka broker, transforms them using Spark Structured Streaming, and then loads the transformed data into Cassandra tables. The first Spark query, which transforms the raw trade data into a feasible format, runs continuously. The second query, which performs aggregations on the data, runs with a trigger interval of 5 seconds.
4. **Serving database layer:** This is the final layer of the pipeline, where the processed data is stored and persisted for further analysis or serving. The data is stored in a Cassandra database.
5. **Analysis layer:** This layer is dedicated to performing advanced analytics on the processed data stored in the Cassandra database. Specifically, a Geometric Brownian Motion (GBM) analysis is performed on the stock price data. The GBM model is a popular model used in financial mathematics to model stock prices because it can accommodate the statistical features of price changes, i.e., the log-normal distribution of prices and the geometric Brownian motion with constant drift and volatility.
The GBM analysis is run every hour on the latest data in the database. The analysis is performed using PySpark, leveraging its ability to handle large datasets and perform complex computations efficiently.
The results of the GBM analysis are stored back into the Cassandra databas for record-keeping and further analysis.
6. **SQL Query Interface Layer (Presto):** This layer serves as the bridge between our NoSQL Cassandra database and the visualization tool Apache Superset, which is primarily designed to work with SQL-based data sources. Presto is a high-performance, distributed SQL query engine that allows querying data where it lives, including Cassandra, making it an excellent choice for this role.
Presto provides a SQL interface for interacting with data stored in Cassandra. This means that Apache Superset can use SQL queries to extract the data it needs for visualization, even though the data is stored in a NoSQL database. Presto abstracts the complexities of dealing with a NoSQL database and provides a unified SQL interface for data analysis and extraction.
7. **Trade Visualization Layer (Apache Superset):** The final layer of this pipeline is dedicated to data visualization. Apache Superset is used to create comprehensive dashboards for visualizing and exploring processed real time trade data.
Apache Superset, connected to our data sources through Presto, is a powerful BI tool that allows us to visualize real-time trade data, and aggregated trade data.
Users can interact with the Apache Superset dashboards to drill down into the data, apply filters, and perform exploratory data analysis with ease. This layer provides an intuitive and interactive interface for users to understand and derive insights from the trade data processed and analyzed in the earlier stages of the pipeline.
8. **GBM Visualization Layer (Streamlit):** This layer is dedicated to visualizing the Geometric Brownian Motion (GBM) analysis results. It uses Streamlit, a Python library that makes it easy to create custom web apps for machine learning and data science. This GBM Visualization Layer adds another dimension to the pipeline by offering an interactive way to explore the GBM analysis results. It allows users to understand the effect of different parameters on the GBM model and the resulting prediction, which can lead to more informed decision-making.
    1. *Line Plot*: The line plot showing actual and predicted stock prices over time gives an idea of the trend in the stock price. This plot can be used to compare the predicted GBM path against the actual stock price. It provides a way to assess the model's performance and the direction of the stock price over time. If the two lines closely follow each other, the model might be performing well, but if they diverge significantly, the model might not be capturing some aspects of the price movement.
    2. *Histogram*: The histogram showing the distribution of the predicted stock prices provides insight into the frequency of different predicted price levels. From this plot, you can infer the most likely price range that the stock might fall into, as per the GBM model. The range with the highest frequency can be considered as the most probable range of stock prices.
    3. *Density Plot*: The density plot is another way of visualizing the distribution of the predicted stock prices. It shows the probability density of the different price levels. Peaks in the density plot indicate price levels with higher probability. This plot can help infer the most probable price level as per the GBM model.

## Group Members
* Ayushman Singh (as16513)
* Kaustubh Mishra (km5939)
* Jayvardhan Singh (js12919)
* Aman Mittal (am11982)
* Shekhar Pandey (cp3793)

## Screenshots
### Superset Dashboard
[Superset Dashboard Screenshot](./.README/SupersetScreencap.jpg)
### Streamlit Dashboard


## Setup Instructions
NOTE - The below commands were tested and verified on Debian 11 Bullseye system. Setting up the pipeline on a Mac or Windows machine may require changes to the configuration (host network bridging is only supported by docker in linux, and the services in the pipeline utilize it to communicate with each other).

----
First begin by cloning the repository using the following command to ensure all submodules are fetched correctly.
```
git clone --recurse-submodules git@github.com:ayush1399/TradingData-Dashboard.git
```
If you don't have docker set up on your system, you can do so by:
```
sudo apt-get update

sudo apt-get install ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Setting up Kafka
```
cd kafka

docker compose up --build -d
```

```
docker exec -it <container> /bin/bash

kafka-topics --bootstrap-server broker:29092 --list

kafka-topics --bootstrap-server broker:29092 --create --if-not-exists --topic market --replication-factor 1 --partitions 1
```

### Setting up the Cassandra Cluster
```
cd cassandra

docker compose up --build -d

docker cp scripts/cassandra-setup.cql <container>:./

docker exec -it <container> /bin/bash

cqlsh -u cassandra -p cassandra -f ./cassandra-setup.cql
```

### Setting up the spark cluster and stream-processor
If you don't have maven installed on your system, you can do so by the next block of commands.
```
sudo apt-get update

sudo apt-get install maven
```

Once maven is installed, proceed with the following commands:
```
mvn dependency:copy-dependencies

cd stream-processor

docker compose up --build -d
```

### Setting up the Collector process to ingest data from Finnhub
```
cd collector

pipenv shell

pipenv install

source src/exp.sh
```
Finally it was set up as a systemd service that runs every hour. The exec command for the systemd service is `python3 src/producer.py`. The systemd service file also needs to be configured with the env vars in exp.sh.

### Setting up Presto
```
docker-compose up -d 

docker cp cassandra.properties <container>:/opt/presto-server/etc/catalog/cassandra.properties

docker exec -it <container> sh -c "ls /opt/presto-server/etc/catalog"

docker exec -it <container> /bin/bash

presto-cli

show catalogs;
```
If cassandra does not show up as a catalog after running the show catalogs command, run the next set of commands.
```
docker restart <container>

docker exec -it <container> /bin/bash

presto-cli

show catalogs;
```

### Setting up Superset
```
cd superset

docker-compose -f docker-compose-non-dev.yml pull

docker-compose -f docker-compose-non-dev.yml up
```

### Setting up the Monte Carlo Geometric Brownian Motion analysis
```
cd gbm-analysis

pipenv shell

pipenv install
```
Finally it was set up as a systemd service that runs every hour. The exec command for the service is:

```
spark-submit --jars '~/TradingData-Dashboard/gbm-analysis/spark-cassandra-connector-assembly_2.12-3.3.0.jar,~/TradingData-Dashboard/gbm-analysis/jnr-posix-3.1.16.jar' GeometricBrownianMotion.py
```

### Setting up the Streamlit dashboard
```
cd streamlit

pipenv shell

pipenv install
```

Finally it was set up a systemd service that respawns on error. The exec command for the service is: `streamlit run portfolio.py`
