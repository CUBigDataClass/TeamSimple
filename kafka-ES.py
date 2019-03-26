import os
import sys

import time
import json
import argparse
import datetime

import kafka
from kafka import KafkaConsumer
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers

consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
						auto_offset_reset='earliest',
						group_id='es')
consumer.subscribe('es_test')

#print(consumer)
	
es = Elasticsearch(hosts='http://localhost',port=9200)
print(es)
actions = []

while True:
	for msg in consumer:
		#print(msg.value)
		action = {
			"index": "es_test",
			"type": "tweet",
			"source": {
				'text' : msg.value.decode('utf-8')
				}
			}
		actions.append(json.dumps(action))
		#print(json.dumps(action))
		if len(actions) >= 500:
			print(msg.value)
			helpers.bulk(es, actions, index='es_test', doc_type='tweet')
			actions = []
 

