FROM confluentinc/cp-kafka:7.3.2
RUN kafka-topics --bootstrap-server broker:29092 --list
RUN kafka-topics --bootstrap-server broker:29092 --create --if-not-exists --topic market --replication-factor 1 --partitions 1