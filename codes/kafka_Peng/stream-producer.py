#!/usr/bin/env python3
import os
import sys

import json
import argparse

import kafka
import twitter

# Allows importing the config.py file even if ran from other directories
_here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_here)

import config

parser = argparse.ArgumentParser(description='Twitter stream reader - Kafka producer')
parser.add_argument('-l', '--limit', default=20, type=int, help='Limit the amount of tweets that will be read. 0 to disable; defaults to %(default)d.')
parser.add_argument('-t', '--track', default='python', help='Comma-separated list of keywords to track. Defaults to "%(default)s"')
parser.add_argument('-s', '--sample', action='store_true', help="Use Twitter's sample messages instead of filtering by keywords")


if __name__ == '__main__':
	args = parser.parse_args()

	twitter_api = twitter.Api(**config.TWITTER_API_CONFIGURATION)

	kafka_producer = kafka.KafkaProducer(
		value_serializer=lambda d: json.dumps(d, separators=(',',':')).encode('utf-8'),
		**config.KAFKA_CONNECT_OPTIONS
	)

	if args.sample:
		tweet_stream = twitter_api.GetStreamSample()
	else:
		track_targets = [x.strip() for x in args.track.split(',')]
		tweet_stream = twitter_api.GetStreamFilter(track=track_targets, languages=['en'])

	messages_written = 0
	for message in tweet_stream:
		# Skip non-message updates (limits, deletes)
		if 'text' not in message:
			continue

		kafka_producer.send(config.KAFKA_TOPIC, message)
		messages_written += 1

		print('#{0:03d}: [{1[id]}] {1[user][screen_name]} {1[text]!r}'.format(messages_written, message))
		if args.limit and messages_written >= args.limit:
			break

	kafka_producer.flush()