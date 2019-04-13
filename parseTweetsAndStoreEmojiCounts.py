# coding: utf-8

import threading, logging, time, json,pymongo
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient
import json


from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from emoji_filter import *



def update_emoji_counts_using_tweets(tweets_collection, tweets_with_sentiment_collection, emoji_collection, number_of_tweets_we_want):

	# How many emoji we want to grab from source collection.
	number_of_tweets_parsed = 0

	# Loop each tweet from source collection.
	preindex = 0;
	for tweets in tweets_collection.find():
		number_of_tweets_parsed +=1

		# Delete current tweet from source collection.
		#tweets_collection.delete_one(tweets)

		# Make sure we do not parse tweets that we already saw.
		current_index = int('0x'+str(tweets['_id'])[-6:],16)
		if(current_index < preindex):
			break
		preindex = current_index


		# Get emojis from current tweet.
		emojis = extract_emojis(tweets['text'])
		

		# Break current loop round if there is no emomji in curernt tweet
		if(len(emojis))==0:
			continue



		''' ----------  Get sentiment for current tweet and store into a new collection ----------'''

		emojis_str = ''.join(emojis)
		scores = sentiment_analyzer_scores(emojis_str)
		sentiment = max(scores, key=scores.get)
		print(emojis_str, sentiment)
		tweets['emojis'] = emojis_str
		tweets['sentiment'] = sentiment
		tweets.pop('_id', None)

		# Append emojis str and sentiment result to current entry and store it to a new dic
		tweets_with_sentiment_collection.insert_one(tweets)



		''' ----------  Count emojis summary and store them into a new collection ----------'''

		for emoji in emojis:
			emoji = emoji.strip() #remove spaces. unlikely....

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
			




		# How many tweets we want to grab from source collection.
		if number_of_tweets_parsed > number_of_tweets_we_want:
			break



# Calculate sentiment score
def sentiment_analyzer_scores(sentence):
    
    score = analyser.polarity_scores(sentence)
    return score




# Create database conncetion.
print("Creating mogo connection...")
client = MongoClient('localhost', 27017)
mydb = client['mydatabase']

# Source collection to read from.
tweets_collection = mydb['tweets_test']

# Collection to store emoji counts.
tweets_with_sentiment_collection = mydb['tweets_with_sentiment_test']
emoji_collection = mydb['emojis_test']

# Initialize sentimental.
analyser = SentimentIntensityAnalyzer()






# Start the infinite loop....
n = 2
while(n>1):

	n = 1
	# How many emoji we want to grab from source collection each round.
	NUMBER_OF_EMOJI_WE_WANT = 100

	# Grab tweets from tweets_collection and store emoji counts into emoji_collection.
	update_emoji_counts_using_tweets(tweets_collection, tweets_with_sentiment_collection, emoji_collection, NUMBER_OF_EMOJI_WE_WANT)

	time.sleep(1)
















