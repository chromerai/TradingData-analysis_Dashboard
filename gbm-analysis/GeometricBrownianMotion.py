from datetime import datetime

from pyspark.sql.types import IntegerType
from pyspark.sql import SparkSession
from pyspark.sql.functions import log, lag, stddev, mean, col, from_unixtime, unix_timestamp, sum
from pyspark.sql.window import Window
import numpy as np

from pyspark import SparkContext, SparkConf
cf = SparkConf()
cf.set("spark.submit.deployMode","client")
sc = SparkContext.getOrCreate(cf)


# create a spark session
spark = SparkSession.builder\
                    .appName('GBM')\
                    .master('spark://localhost:7077')\
                    .getOrCreate()

filters = 'WHERE symbol = APPL'
df = spark.read \
       .format("org.apache.spark.sql.cassandra") \
       .option('spark.cassandra.connection.host', "localhost") \
       .option('spark.cassandra.connection.port', "9042") \
       .option("user", "cassandra") \
       .option("password", "cassandra") \
       .option("keyspace", "market") \
       .option("table", "trades") \
       .load()

df = df.withColumn("price_volume_multiply", col("price")*col("volume"))

df = df.withColumn("trade_timestamp_unix", unix_timestamp("trade_timestamp"))
# convert timestamp to seconds
df = df.withColumn('Timestamp',(((col('trade_timestamp_unix') / 1000).cast(IntegerType())*1000).cast('timestamp')))
# truncate timestamp to second-level granularity
df = df.withColumn('Timestamp', from_unixtime(unix_timestamp('Timestamp'), 'yyyy-MM-dd HH:mm:ss'))
# calculate volume * price
df = df.withColumn('Volume_Price', col('volume') * col('price'))
# group by timestamp and calculate volume-adjusted price average
df = df.groupBy('symbol','Timestamp').agg((sum('Volume_Price') / sum('volume')).alias('VAPR'))

df = df.orderBy( 'Timestamp')

TICKERS = [
        'AAPL',
        'AMZN',
        'MSFT',
        'BINANCE:ETHUSDT',
        'BINANCE:BTCUSDT',
        'BINANCE:XRPUSDT',
        'BINANCE:DOGEUSDT'
]

window = Window.orderBy('Timestamp')

for ticker in TICKERS:
	sdf = df.filter(df.symbol == ticker)

	# calculate the daily return
	sdf = sdf.withColumn('Prev_VAPR', lag('VAPR').over(window))
	sdf = sdf.withColumn('Return', log(sdf['VAPR'] / sdf['Prev_VAPR']))

	# calculate mean and standard deviation of the returns
	mean_return = sdf.agg(mean('Return')).first()[0]
	stddev_return = sdf.agg(stddev('Return')).first()[0]
	stddev_return = sdf.agg(stddev('Return')).first()[0]

	trading_interval = 3

	# GBM formula
	sdf = sdf.withColumn('gbm', sdf['VAPR'] * np.exp((mean_return - 0.5 * stddev_return ** 2) * trading_interval + stddev_return * np.sqrt(trading_interval) * np.random.normal()))

	sdf = sdf.withColumnRenamed('Timestamp', 'timestamp')
	sdf = sdf.withColumnRenamed('VAPR', 'actual')
	sdf = sdf.select('timestamp','gbm','symbol', 'actual')

	# df_1.show(5)
	if ticker == 'APPL':
		sdf.write \
    			.format('org.apache.spark.sql.cassandra') \
    			.mode('overwrite') \
    			.option('confirm.truncate', True) \
    			.option('keyspace', 'market') \
    			.option('table', 'msc') \
    			.save()
	else:
		sdf.write \
			.format('org.apache.spark.sql.cassandra') \
			.mode('append') \
			.option('keyspace', 'market') \
			.option('table', 'msc') \
			.save()
