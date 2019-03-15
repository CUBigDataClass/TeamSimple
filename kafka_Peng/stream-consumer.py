#!/usr/bin/env python3
import os
import sys

import time
import json
import argparse
import datetime

import kafka
import elasticsearch
from elasticsearch import helpers

# Allows importing the config.py file even if ran from other directories
_here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_here)

import config
from twitter_kafka_crawler import db, models

# For converting datetimes into seconds since epoch
UTC_EPOCH = datetime.datetime.utcfromtimestamp(0)
UTC_EPOCH_AWARE = UTC_EPOCH.replace(tzinfo=datetime.timezone.utc)

parser = argparse.ArgumentParser(description='Twitter stream reader - Kafka consumer')
parser.add_argument('-s', '--batch-size', default=50, type=int, help='How many tweets to process in one go. Defaults to %(default)d.')
parser.add_argument('-t', '--batch-timeout', default=2.5, metavar='SECONDS', type=float, help='Maximum amount of time to wait for the batch to fill up. Defaults to %(default).1f seconds.')
parser.add_argument('-c', '--consumer-timeout', default=0.5, metavar='SECONDS', type=float, help='Kafka consumer timeout. Defaults to %(default).1f seconds.')
parser.add_argument('-b', '--from-beginning', action='store_true', help='Seek to topic beginning instead of continuing')


def _parse_timestamp(timestamp):
	''' Parses Twitter's created_at timestamps '''
	return datetime.datetime.strptime(timestamp, '%a %b %d %H:%M:%S %z %Y')


def _parse_user(user_dict):
	''' Gets an existing User out of a user_dict, or creates one '''
	user = models.User.query.get(user_dict['id'])
	if not user:
		user = models.User(
			id=user_dict['id'],
			name=user_dict['name'],
			screen_name=user_dict['screen_name'],
			description=user_dict['description'],
			created_time=_parse_timestamp(user_dict['created_at'])
		)
	return user


def process_messages(messages, es_client):
	''' Processes a bunch of messages by extracting relevant tweet-info,
		saving that to the database and indexing them in ES as well '''
	if not messages:
		return

	es_batch = []

	for message in messages:
		tweet_dict = message.value

		tweet = models.Tweet.query.get(tweet_dict['id'])

		# Skip already processed (in-database) tweets
		if tweet:
			continue

		# Get the full tweet
		if tweet_dict['truncated']:
			tweet_text = tweet_dict['extended_tweet']['full_text']
		else:
			tweet_text = tweet_dict['text']

		tweet_user = _parse_user(tweet_dict['user'])
		tweet = models.Tweet(
			id=tweet_dict['id'],
			user=tweet_user,
			text=tweet_text,
			created_time=_parse_timestamp(tweet_dict['created_at'])
		)
		db.session.add(tweet)

		es_batch.append({
			'_id' : tweet.id,
			'_type' : 'tweet',
			'_index' : config.ELASTICSEARCH_INDEX,
			'_source' : {
				'user_id' : tweet_user.id,
				'user_name' : tweet_user.name,
				'user_screen_name' : tweet_user.screen_name,
				'text' : tweet.text,
				# Datetime to milliseconds since epoch
				'created_time' : int( (tweet.created_time - UTC_EPOCH_AWARE).total_seconds() * 1000),
			}
		})

	db.session.commit()

	elasticsearch.helpers.bulk(es_client, es_batch)
	es_client.indices.refresh(index=config.ELASTICSEARCH_INDEX)


if __name__ == '__main__':
	args = parser.parse_args()

	es_client = elasticsearch.Elasticsearch(hosts=config.ELASTICSEARCH_HOSTS)

	kafka_consumer = kafka.KafkaConsumer(
		# config.KAFKA_TOPIC,
	    client_id="tweet-client-1",
	    group_id="tweet-group",

		value_deserializer=lambda b: json.loads(b.decode('utf-8')),
		consumer_timeout_ms=500,
		**config.KAFKA_CONNECT_OPTIONS
	)

	# Assing topics to Kafka consumer
	topic_partitions = [
		kafka.TopicPartition(config.KAFKA_TOPIC, partition)
		for partition in kafka_consumer.partitions_for_topic(config.KAFKA_TOPIC)
	]
	print('Assigning self to topic partitions:', topic_partitions)
	kafka_consumer.assign(topic_partitions)

	if args.from_beginning:
		kafka_consumer.seek_to_beginning()

	batch = []
	batch_deadline = time.time() + args.batch_timeout

	def _process_batch():
		process_messages(batch, es_client)
		print('Processed', len(batch), 'messages from offset', batch[0].offset)
		batch.clear()
		batch_deadline = time.time() + args.batch_timeout


	while True:
		# Try to fill the batch...
		for message in kafka_consumer:
			batch.append(message)
			if len(batch) >= args.batch_size:
				_process_batch()

		# ...but process incomplete chunks if we don't get messages for a while
		# (StopIteration due to consumer_timeout_ms)
		if batch and time.time() >= batch_deadline:
			_process_batch()