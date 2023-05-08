# TradingData-Dashboard


```
cd kafka
docker compose up --build -d
```

```
docker exec -it <container> /bin/bash
kafka-topics --bootstrap-server broker:29092 --list
kafka-topics --bootstrap-server broker:29092 --create --if-not-exists --topic market --replication-factor 1 --partitions 1
```

```
cd cassandra
docker compose up --build -d
docker cp scripts/cassandra-setup.cql <container>:./
docker exec -it <container> /bin/bash
cqlsh -u cassandra -p cassandra -f ./cassandra-setup.cql
```

```
cd StreamProcessor
docker compose up --build -d
```

```
cd websocketCollector
pip install requirements.txt
source src/exp.sh
python3 src/FinnhubProducer.py
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