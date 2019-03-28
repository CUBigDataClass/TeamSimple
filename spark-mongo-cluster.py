
# coding: utf-8

# In[1]:


from pyspark.sql.functions import udf, col,split
from pyspark.ml.clustering import KMeans
import json
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers


# In[2]:


from pyspark.sql import SparkSession
my_spark = SparkSession.builder.appName("myApp").config("spark.mongodb.input.uri", "mongodb://127.0.0.1/mydatabase.tweets_test")     .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/mydatabase.tweets_test")     .config("spark.io.compression.codec", "snappy").getOrCreate() #this line's config is for solving lz4 error
dataFrame=my_spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
dataFrame.printSchema()


# In[3]:


#split = udf(lambda x: x.split(','))
#df.withColumn("user_location", split_udf(col("user_location"))).show()
#df=dataFrame.withColumn("user_location",
   # split(col("user_location"), ",\s*").cast("array<float>").alias("user_location")
#)
#df_loc = df.select('user_location')


# In[4]:


from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
assembler = VectorAssembler(
    inputCols=['loc_lat','loc_long'],
    outputCol='features')
trainingData = assembler.transform(dataFrame)
#trainingData.show()


# In[5]:


kmeans = KMeans(k=3,seed=1)
model = kmeans.fit(trainingData)
# Shows the result.
centers = model.clusterCenters()
print("Cluster Centers: ")
for center in centers:
    print(center)


# In[6]:


cluster_ind = model.transform(trainingData)
dataToKibana = cluster_ind.toPandas().to_dict('record')
for item in dataToKibana:
    item['created_at'] =item['created_at'][:10]+'T'+item['created_at'][11:]+'Z'
    
for item in dataToKibana:
    item['loc_lat'] =round(item['loc_lat'],2)
    item['loc_long'] =round(item['loc_long'],2)


# In[9]:

#transport data to elasticsearch
es = Elasticsearch(hosts='http://localhost',port=9200)
actions = []
mappings = {
    "mappings":{
        "tweet": {
            "properties": {
                "text": { "type": "text"  },
                "timestamp": { "type": "date" },
                "location": {"type": "geo_point"},
                "prediction": {"type": "integer"}
                }
            }
    }
}
es.indices.create(index="test", body=mappings)
for msg in dataToKibana:
    print(msg["text"])
    print("-------------")
    action = {
            "index": "loc6",
            "type": "tweet",
            "source": {
                'text' : msg["text"],
                'timestamp': msg["created_at"],
                'location': {"lat": msg["loc_lat"],"lon": msg["loc_long"]},
                'prediction': msg["prediction"]
                }
            }
    actions.append(json.dumps(action))
helpers.bulk(es, actions, index='test', doc_type='tweet')
    

