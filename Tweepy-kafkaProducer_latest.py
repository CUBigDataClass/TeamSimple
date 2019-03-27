
# coding: utf-8

# # Ingesting realtime tweets using Apache Kafka, Tweepy and Python
# 
# ### Purpose:
# - main data source for the lambda architecture pipeline
# - uses twitter streaming API to simulate new events coming in every minute
# - Kafka Producer sends the tweets as records to the Kafka Broker
# 
# ### Contents: 
# - [Twitter setup](#1)
# - [Defining the Kafka producer](#2)
# - [Producing and sending records to the Kafka Broker](#3)
# - [Deployment](#4)

# ### Required libraries

# In[8]:


import tweepy
import time
from kafka import KafkaConsumer, KafkaProducer
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="my-application")


# <a id="1"></a>
# ### Twitter setup
# - getting the API object using authorization information
# - you can find more details on how to get the authorization here:
# https://developer.twitter.com/en/docs/basics/authentication/overview

# In[9]:


# twitter setup
ACCESS_TOKEN = '799844067701977088-qrHMnTaYFUcqBbeG5yT3G8GTieLJt6N'
ACCESS_SECRET = 'kRtA7MsTjvAqmft9BdtE7z2FtAouYsOY8OlAvByIy5m1l'
CONSUMER_KEY = 'yZUmKJQxfGmpLtvVTmGTHPKiD'
CONSUMER_SECRET = '1bwO3JIc664KkObN5LJYVpALDi63NBExoLSKsaMrJ7KPYKYiXM'
# Setup tweepy to authenticate with Twitter credentials:
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
# Creating the API object by passing in auth information
api = tweepy.API(auth) 


# <a id="2"></a>
# ### Defining the Kafka producer
# - specify the Kafka Broker
# - specify the topic name
# - optional: specify partitioning strategy

# In[10]:


producer = KafkaProducer(bootstrap_servers='localhost:9092')
topic_name = 'tweepy-kafka-test1'


# <a id="3"></a>
# ### Producing and sending records to the Kafka Broker
# - querying the Twitter API Object
# - extracting relevant information from the response
# - formatting and sending the data to proper topic on the Kafka Broker

# In[11]:


import json
def get_twitter_data():
    res = api.search("and")#,geocode = ["105,30.132633,150mi"])
    j=0
    for i in res:
        location = geolocator.geocode(str(i.user.location)) 
        if i.user.location != "" and location != None:
            record = '{'
            record += "\"created_at\":" +  json.dumps(str(i.created_at))
            record += ','
            record += "\"text\":" +  json.dumps(str(i.text))
            record += ','
            #record += "\"user_id\":" +  json.dumps(str(i.user.id_str))
            #record += ','
            #record += "\"user_timezone\":" +  json.dumps(str(i.user.time_zone))
            #record += ','
            #record += "\"user_location\":" +  json.dumps(str(location.latitude)+','+ str(location.longitude))
            #record += ','
            record += "\"loc_lat\":" + json.dumps(location.latitude)
            record += ','
            record += "\"loc_long\":" + json.dumps(location.longitude)
            #record += ','
            #record += "\"followers_count\":" +  json.dumps(str(i.user.followers_count))
            #record += ','
            #record += "\"language\":" + json.dumps(str(i.lang))
            record += '}'
            producer.send(topic_name, str.encode(record))
            #print(record)


# In[12]:


#get_twitter_data()


# <a id="4"></a>
# ### Deployment 
# - perform the task every couple of minutes and wait in between

# In[13]:


def periodic_work(interval):
    while True:
        get_twitter_data()
        #interval should be an integer, the number of seconds to wait
        time.sleep(interval)


# In[14]:


periodic_work(60 * 0.1)  # get data every couple of minutes

