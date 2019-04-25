import findspark
from pyspark.sql.functions import udf
from pyspark.sql import SparkSession
import re


findspark.init()
conf = SparkConf()
conf.setAppName("SentimentAnalysis")
sc = SparkContext(conf=conf)
pos = sc.textFile("pos.txt")
neg = sc.textFile("neg.txt")
pos_sp = pos.flatMap(lambda line: line.split("\n")).collect()
neg_sp = neg.flatMap(lambda line: line.split("\n")).collect()


def getSentiment(s):
	words = s.split(' ')
	count_pos = 0
	count_neg = 0
	for word in words:
		if word in pos_sp:
			count_pos += 1
		elif word in neg_sp:
			count_neg += 1
	score = (count_pos - count_neg)/len(words)
	if score>0:
		return "pos"
	elif score<0:
		return "neg"
	else:
		return "neu"
while True:
    my_spark = SparkSession \
        .builder \
        .appName("myApp") \
        .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/mydatabase.tweets_test") \
        .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/mydatabase.tweets_test") \
        .config("spark.io.compression.codec", "snappy").getOrCreate() #this line's config is for solving lz4 error
    df=my_spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
    udf_myFunction = udf(getSentiment, StringType()) # if the function returns an int
    df.withColumn("textSentimentSpark", udf_myFunction("text")) #"_3" being the column name of the column you want to consider
    df.write.format("com.mongodb.spark.sql.DefaultSource").mode("overwrite").option("database","mydatabase").option("collection", "sentiment_text").save()
    time.sleep(10)