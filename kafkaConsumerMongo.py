
# coding: utf-8

# In[4]:


import threading, logging, time, json,pymongo
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient
import json


# In[5]:


client = MongoClient('localhost', 27017)
mydb = client['mydatabase']
mycollection = mydb['tweets_test']
consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                         auto_offset_reset='earliest',
                         group_id='mongo'
                        )
consumer.subscribe('tweepy-kafka-test1')


# In[6]:


for msg in consumer:
    #print(msg.value)
    byteText = msg.value   
    text = str(byteText,"utf-8")
    #text = json
    data_to_insert = json.loads(text, strict=False)
    x = mycollection.insert_one(data_to_insert)

