from pyspark.sql import SparkSession
import time
while True:
	my_spark = SparkSession \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/mydatabase.sentiment_text") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/mydatabase.sentiment_text") \
    .config("spark.io.compression.codec", "snappy").getOrCreate() #this line's config is for solving lz4 error
    df=my_spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
    sentCount = df.groupBy("sentimentScoreText").count().sort('count',ascending=False)
    sentCount.write.format("com.mongodb.spark.sql.DefaultSource").mode("overwrite").option("database",
    	"mydatabase").option("collection", "text_sentiment_count").save()

    time.sleep(10)