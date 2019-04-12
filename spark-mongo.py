import pymongo_spark
pymongo_spark.activate()
# create rdd for the mongodb collection
rdd = sc.mongoRDD('mongodb://localhost:27017/mydatabase.tweets_test')
print(rdd.first())
print(rdd.count())


pyspark --conf "spark.mongodb.input.uri=mongodb://127.0.0.1:27017/mydatabase.tweets_test?readPreference=primaryPreferred" \
              --conf "spark.mongodb.output.uri=mongodb://127.0.0.1:27017/mydatabase.tweets_test" \
              --packages org.mongodb.spark:mongo-spark-connector_2.11:2.4.0