import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy import StreamListener
import json
import sys
import webbrowser
import codecs
import csv
import datetime
import kafka
from kafka import SimpleProducer, KafkaClient
from pandas.io.json import json_normalize

def main():
	global outfile, search_words_list, auth

	#search_words = str(raw_input("Enter the word to search: "))
	#total_tweet_count = int(raw_input("No of tweets to be pulled for the search word: "))
	search_words = "and"
	#total_tweet_count = 2

	print(search_words)

	search_words_list = search_words.split(",")

	print(search_words_list)

	kafka = KafkaClient("localhost:9092")
	producer = SimpleProducer(kafka)

	search_tweets(producer)

def search_tweets(producer):
	global search_words_list, auth, indiv, outfile, file
	config = {}
	exec(compile(open("config.py", "rb").read(), "config.py", 'exec'), config)
	consumer_key = config["consumer_key"]
	consumer_secret = config["consumer_secret"]
	access_token = config["access_key"]
	access_secret = config["access_secret"]
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)

	for indiv in search_words_list:
		print("--------Search word - " + indiv + " -is being processed------------")
		file = "/Users/hanxu/Desktop/TeamSimple/tweetcount_" + str(indiv) + ".txt"
		outfile = codecs.open(file, 'w', "utf-8")
		currentTime = str(datetime.datetime.utcnow().date())
		print(currentTime)
		for t in tweepy.Cursor(api.search, q = str(indiv), include_entities=True, since = currentTime).items(10000):
			#print(t)
			shouldContinue = True
			tweetTime = t.created_at # get the current time of the tweet
			now = datetime.datetime.utcnow()
			interval = now - tweetTime # subtract tweetTime from currentTime
			print(now)
			print(tweetTime)
			print(interval)
			print(interval.seconds)
			if interval.seconds <= 20: #get interval in seconds and use your time constraint in seconds (mine is 1hr and 5 mins = 3900secs)
				print(t.text)
				print(t.created_at)
				outfile.write(t.text)
				outfile.write(str(t.created_at))
				outfile.write(str("\n"))
				try:
					producer.send_messages('kafkatwitterstream_' + str(indiv),t.text.encode("utf-8"))
				except Exception as e:
					print(e)
					break
			else:
				shouldContinue = False
				print(t.text)
				print(t.created_at)
				outfile.write(t.text)
				outfile.write(str(t.created_at))
				outfile.write(str("\n"))
				try:
					producer.send_messages('kafkatwitterstream_'+ str(indiv),t.text.encode("utf-8"))
				except Exception as e:
					print(e)
					break

			#print('\n')

			if not shouldContinue: # check if tweet is still within time range. Tweet returned are ordered according to recent already.
				print('exiting the loop')
				break

	sys.exit()

main()






