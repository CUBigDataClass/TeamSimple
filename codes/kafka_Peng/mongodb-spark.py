from pyspark.sql import SparkSession

if __name__ == "__main__":

    spark = SparkSession.builder.appName("Python Spark SQL basic example").getOrCreate()

    logger = spark._jvm.org.apache.log4j
    logger.LogManager.getRootLogger().setLevel(logger.Level.FATAL)

    # Save some data
    characters = spark.createDataFrame([("Bilbo Baggins",  50), ("Gandalf", 1000), ("Thorin", 195), ("Balin", 178), ("Kili", 77), ("Dwalin", 169), ("Oin", 167), ("Gloin", 158), ("Fili", 82), ("Bombur", None)], ["name", "age"])
    characters.write.format("com.mongodb.spark.sql").mode("overwrite").save()

    # print the schema
    print("Schema:")
    characters.printSchema()

    # read from MongoDB collection
    df = spark.read.format("com.mongodb.spark.sql").load()

    # SQL
    df.registerTempTable("temp")
    centenarians = spark.sql("SELECT name, age FROM temp WHERE age >= 100")
    print("Centenarians:")
    centenarians.show()