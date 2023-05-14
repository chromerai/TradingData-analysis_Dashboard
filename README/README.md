# Real Time Stream Processing and Analysis of Trading Data
CSGY-6513 Big Data Spring 2023, Final Project (Group 3)
## Introduction
## Group Members
## Screenshots
## Setup Instructions

First begin by cloning the repository using the following command to ensure all submodules are fetched correctly.
```
git clone --recurse-submodules git@github.com:ayush1399/TradingData-Dashboard.git
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
```
cd stream-processor
docker compose up --build -d
```

```
cd collector
pip install requirements.txt
source src/exp.sh
python3 src/producer.py
```

```
docker-compose up -d 
docker cp cassandra.properties <container>:/opt/presto-server/etc/catalog/cassandra.properties
docker exec -it <container> sh -c "ls /opt/presto-server/etc/catalog"

docker exec -it <container> /bin/bash
presto-cli
show catalogs;

docker restart <container>
```

```
cd superset
docker-compose -f docker-compose-non-dev.yml pull
docker-compose -f docker-compose-non-dev.yml up
```