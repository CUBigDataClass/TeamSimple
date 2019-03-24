import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy import StreamListener
import json
import sys
import webbrowser
import codecs
import csv
import time
from kafka import SimpleProducer, KafkaClient
from pandas.io.json import json_normalize

class tweetlistener(StreamListener):

	def __init__(self, api):
		self.api = api
		super(tweepy.StreamListener, self).__init__()
		client = KafkaClient("localhost:9092")
		#print(client)

		#https://kafka-python.readthedocs.io/en/1.0.1/apidoc/SimpleProducer.html
		self.producer = SimpleProducer(client, async = True, batch_send_every_n = 1000, batch_send_every_t = 10)
		print("after init producer")

	#printout data
	def on_status(self, status):
		global counter, total_tweet_count, outfile, search_words_list, indiv 

		counter += 1
		print(counter)
		#if counter >= total_tweet_count:
			#search_words_list.pop(0)
			#outfile.close()
			#search_tweets()

		print("--------NEW TWEET ARRIVED---------")
		print("Tweet Text: %s" %status.text)
		outfile.write(status.text)
		outfile.write(str("\n"))
		print("Author's screen name: %s" %status.author.screen_name)
		print("Time of creation: %s" %status.created_at)
		print("Source of tweet: %s" %status.source)

		#send data using kafka producer to kafka topic
		msg = status.text.encode("utf-8")
		try:
			self.producer.send_messages('kafkatwitterstream',msg)
		except Exception as e:
			print(e)
			return False
		return True


	def on_error(self,status):
		print("Too soon reconnected. Will terminate the program")
		print(status)
		sys.exit()
		print("End of steam")

	
def main():
	global total_tweet_count, outfile, search_words_list, auth

	#search_words = str(raw_input("Enter the word to search: "))
	#total_tweet_count = int(raw_input("No of tweets to be pulled for the search word: "))
	search_words = "hello"
	#total_tweet_count = 10

	#print(search_words)

	search_words_list = search_words.split(",")

	#print(search_words_list)

	search_tweets()


def search_tweets():
	global search_words_list, counter, auth, indiv, outfile, file, access_key

	config = {}
	exec(compile(open("config1.py", "rb").read(), "config1.py", 'exec'), config)
	consumer_key = config["consumer_key"]
	consumer_secret = config["consumer_secret"]
	access_token = config["access_key"]
	access_secret = config["access_secret"]
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)

	for indiv in search_words_list:
		print("Search word - " + indiv + " -is being processed")
		counter = 0
		file = "/Users/hanxu/Desktop/TeamSimple/tweettext_" + str(indiv) + ".txt"
		outfile = codecs.open(file, 'w', "utf-8")
		twitterStream = Stream(auth, tweetlistener(api)) 
		#one_list = []
		#one_list.append(indiv)
		#print(one_list)
		twitterStream.filter(track=[str(indiv)])

	sys.exit()

main()





