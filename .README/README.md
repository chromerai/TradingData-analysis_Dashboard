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

```
cd collector

pip install requirements.txt

source src/exp.sh

python3 src/producer.py
```

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