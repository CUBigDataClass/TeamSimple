
# coding: utf-8

# In[58]:


from pyspark.sql.functions import udf, col,split
from pyspark.ml.clustering import KMeans
import json
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import threading, logging, time, json,pymongo
from pymongo import MongoClient
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from textblob import TextBlob
from emoji_filter import *
import sys
import shutil
import nltk
from pyspark import SparkConf, SparkContext


# In[56]:


def update_sentimentAndEmoji_counts_using_tweets(tweets_collection, tweets_with_sentiment_collection, emoji_collection, numberOfTweetsToParse):
    # How many emoji we want to grab from source collection.
    sentAnalyzer = SentimentIntensityAnalyzer()
    number_of_tweets_parsed = 0
    # Loop each tweet from source collection.
    highest_previous_primary_key = 0
    for document in tweets_collection.find():
        # get the current primary key, and if it's greater than the previous one, we print the results and increment the variable to that value
        current_primary_key = int('0x'+str(document['_id'])[-6:],16)
        if current_primary_key > highest_previous_primary_key:
            #get text sentiment score
            tweet = document["text"]
            text = re.sub(r"http\S+", "", tweet)
            if text == '':
                tweets_collection.update({"_id": document["_id"]}, {"$set": {"sentiment_score_text": 0}})
                continue            
            blob = TextBlob(text)
            sentScore_list = []
            for sentence in blob.sentences:
                sentScore_list.append(sentence.sentiment.polarity)
            sent_score = sum(sentScore_list)/len(sentScore_list)
            tweets_collection.update({"_id": document["_id"]}, {"$set": {"sentiment_score_text": sent_score}})
        
            # Get emojis from current tweet.
            emojis = extract_emojis(document['text'])
            # Break current loop round if there is no emomji in curernt tweet
            if(len(emojis))==0:
                continue
            ''' ----------  Get sentiment for current tweet and store into a new collection ----------'''
            emojis_str = ''.join(emojis)
            scores = sentAnalyzer.polarity_scores(emojis_str)
            del scores['compound']
            sentiment = max(scores, key=scores.get)
            print(emojis_str, sentiment)
            document['emojis'] = emojis_str
            document['sentiment_score_text'] = sent_score
            document['sentiment_emoji'] = sentiment
            document.pop('_id', None)
            # Append emojis str and sentiment result to current entry and store it to a new dic
            tweets_with_sentiment_collection.insert_one(document)    

            ''' ----------  Count emojis summary and store them into a new collection ----------'''
            for emoji in emojis:
                emoji = emoji.strip() #remove spaces. unlikely....
                # Look for current emoji in target collection.
                result = emoji_collection.find_one({'emoji':emoji}) 
                # First time see this emoji. Initialize it and set count to 1.
                if result == None:
                    #print("Initializing "+emoji)
                    emoji_collection.insert_one({'emoji':emoji, 'count':1})    
                # Emoji already exists in collection. Increment count by 1.
                else:
                    #print("Updating "+emoji)
                    emoji_collection.update_one(result, {"$set":{'count':int(result['count'])+1}})
            # How many tweets we want to grab from source collection.
            #if number_of_tweets_parsed > numberOfTweetsToParse:
            #    break
            number_of_tweets_parsed +=1
        highest_previous_primary_key = current_primary_key


# In[57]:


# Create database conncetion.
print("Creating mongo connection...")
client = MongoClient('localhost', 27017)
mydb = client['mydatabase']
# Source collection to read from.
tweets_collection = mydb['tweets_test']
# Collection to store sentiment and emoji count
tweets_with_sentiment_collection = mydb['tweets_with_sentiment_test']
emoji_collection = mydb['emojis_test']
# Start the infinite loop....
while(True):
    # How many emoji we want to grab from source collection each round. only for testing
    #numberOfTweetsToParse = 500
    # Grab tweets from tweets_collection and store emoji counts into emoji_collection.
    update_sentimentAndEmoji_counts_using_tweets(tweets_collection, tweets_with_sentiment_collection, emoji_collection,numberOfTweetsToParse)
    time.sleep(1)


# In[ ]:


highest_previous_primary_key = 0
scores = []
while True:
    cursor = mycollection.find()
    count = 0
    for document in cursor:
        # get the current primary key, and if it's greater than the previous one
        # we print the results and increment the variable to that value
        current_primary_key = int('0x'+str(document['_id'])[-6:],16)
        if current_primary_key > highest_previous_primary_key:
            #do your work only on newly incoming rows
            tweet = document["text"]
            text = re.sub(r"http\S+", "", tweet)
            if text == '':
                mycollection.update({"_id": document["_id"]}, {"$set": {"sentiment_score_text": 0}})
                continue            
            blob = TextBlob(text)
            score = []
            for sentence in blob.sentences:
                score.append(sentence.sentiment.polarity)
            sent_score = sum(score)/len(score)
            #scores.append(sent_score)
            mycollection.update({"_id": document["_id"]}, {"$set": {"sentiment_score_text": sent_score}})
            #count += 1
        highest_previous_primary_key = current_primary_key
    #print(count)
    time.sleep(3)


# In[2]:


from pyspark.sql import SparkSession
my_spark = SparkSession     .builder     .appName("myApp")     .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/mydatabase.tweets_test")     .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/mydatabase.tweets_test")     .config("spark.io.compression.codec", "snappy").getOrCreate() #this line's config is for solving lz4 error
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
es.indices.create(index="loc11", body=mappings)
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
helpers.bulk(es, actions, index='loc11', doc_type='tweet')
    

