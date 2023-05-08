FROM cassandra:3.11.3
COPY ./scripts/cassandra-setup.cql /cassandra-setup.cql
RUN echo loading cassandra keyspace && cqlsh cassandra:9042 -u cassandra -p cassandra -f /cassandra-setup.cql