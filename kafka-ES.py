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
consumer.subscribe('kafkatwitterstream')

print(consumer)
	
es = Elasticsearch(hosts='http://localhost',port=9200)
actions = []

for msg in consumer:
	print(msg.value)
	action = {
		"_index": "tweepyes",
		"_source": {
			'text' : msg
			}
		}
	actions.append(action)
    
helpers.bulk(es, actions)
 

