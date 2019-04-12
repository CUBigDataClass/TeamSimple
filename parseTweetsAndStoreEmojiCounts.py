# coding: utf-8

import threading, logging, time, json,pymongo
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient
import json


from emoji_filter import *



def update_emoji_counts_using_tweets(tweets_collection, emoji_collection, number_of_emojis_we_want):

	# How many emoji we want to grab from source collection.
	number_of_emoji_parsed = 0

	# Loop each tweet from source collection.
	for tweets in tweets_collection.find():

		# Delete current tweet from source collection.
		tweets_collection.delete_one(tweets)

		# Get emojis from current tweet.
		emojis = extract_emojis(tweets['text'])
		for emoji in emojis:
			emoji = emoji.strip()
			number_of_emoji_parsed += 1

			# Look for current emoji in target collection.
			result = emoji_collection.find_one({'emoji':emoji})
			
			# First time see this emoji. Initialize it and set count to 1.
			if result == None:
				print("Initializing "+emoji)
				emoji_collection.insert_one({'emoji':emoji, 'count':1})
			
			# Emoji already exists in collection. Increment count by 1.
			else:
				print("Updating "+emoji)
				emoji_collection.update_one(result, {"$set":{'count':int(result['count'])+1}})
		
		# How many emoji we want to grab from source collection.
		if number_of_emoji_parsed > number_of_emojis_we_want:
			break




# Create database conncetion.
print("Creating mogo connection...")
client = MongoClient('localhost', 27017)
mydb = client['mydatabase']

# Source collection to read from.
tweets_collection = mydb['tweets_test']

# Collection to store emoji counts.
emoji_collection = mydb['emojis_test']




# Start the infinite loop....
while(True):

	# How many emoji we want to grab from source collection each round.
	NUMBER_OF_EMOJI_WE_WANT = 50

	# Grab tweets from tweets_collection and store emoji counts into emoji_collection.
	update_emoji_counts_using_tweets(tweets_collection, emoji_collection, NUMBER_OF_EMOJI_WE_WANT)

	time.sleep(5)











