# coding: utf-8
#from pyspark.sql.functions import udf, col,split
#from pyspark.ml.clustering import KMeans
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
#from pyspark import SparkConf, SparkContext

def update_sentimentAndEmoji_counts_using_tweets(tweets_collection, tweets_with_sentiment_collection, emoji_collection, numberOfTweetsToParse):
    # How many emoji we want to grab from source collection.
    sentAnalyzer = SentimentIntensityAnalyzer()
    number_of_tweets_parsed = 0
    highest_previous_primary_key = 0
    # Loop each tweet from source collection.
    while(True):
        for document in tweets_collection.find():
            # get the current primary key, and if it's greater than the previous one, we print the results and increment the variable to that value
            current_primary_key = int('0x'+str(document['_id'])[-6:],16)
            if current_primary_key > highest_previous_primary_key:
                #get text sentiment score
                new_document = document
                tweet = document["text"]
                text = re.sub(r"http\S+", "", tweet)
                if text == '':
                    continue            
                blob = TextBlob(text)
                sentScore_list = []
                for sentence in blob.sentences:
                    sentScore_list.append(sentence.sentiment.polarity)
                if len(sentScore_list) == 0:
                    sent_score = 0
                else:
                    sent_score = sum(sentScore_list)/len(sentScore_list)
                if sent_score > 0:
                    sent_text = 'pos'
                elif sent_score < 0:
                    sent_text = 'neg'
                else:
                    sent_text = 'neu'
                new_document.pop('_id', None)
                new_document['sentimentScoreText'] = sent_text
                tweets_with_sentiment_collection.insert_one(new_document)
    
            
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
                #print(emojis_str, sentiment)
                document['emoji'] = emojis_str
                #document['sentimentScoreText'] = sent_score
                document['sentimentEmoji'] = sentiment
                document.pop('_id', None)
                document.pop('text', None)
                # Append emojis str and sentiment result to current entry and store it to a new dic
                emoji_collection.insert_one(document)    

                ''' ----------  Count emojis summary and store them into a new collection ----------'''
                # for emoji in emojis:
                #     emoji = emoji.strip() #remove spaces. unlikely....
                #     # Look for current emoji in target collection.
                #     result = emoji_collection.find_one({'emoji':emoji}) 
                #     # First time see this emoji. Initialize it and set count to 1.
                #     if result == None:
                #         #print("Initializing "+emoji)
                #         emoji_collection.insert_one({'emoji':emoji, 'count':1})    
                #     # Emoji already exists in collection. Increment count by 1.
                #     else:
                #         #print("Updating "+emoji)
                #         emoji_collection.update_one(result, {"$set":{'count':int(result['count'])+1}})
                # How many tweets we want to grab from source collection.
                #if number_of_tweets_parsed > numberOfTweetsToParse:
                #    break
                number_of_tweets_parsed +=1
            highest_previous_primary_key = current_primary_key
        time.sleep(2)

# Create database conncetion.
print("Creating mongo connection...")
client = MongoClient('localhost', 27017)
mydb = client['mydatabase']
# Source collection to read from.
tweets_collection = mydb['tweets_test']

tweets_with_sentiment_collection = mydb['tweets_text_sentiment']
# Collection to store sentiment and emoji count
emoji_collection = mydb['tweets_emoji_sentiment']
# How many emoji we want to grab from source collection each round. only for testing
numberOfTweetsToParse = 500
# Grab tweets from tweets_collection and store emoji counts into emoji_collection.
update_sentimentAndEmoji_counts_using_tweets(tweets_collection, tweets_with_sentiment_collection, emoji_collection,numberOfTweetsToParse)
