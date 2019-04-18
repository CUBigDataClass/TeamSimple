import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from pymongo import MongoClient

client = MongoClient(port=27017)
db = client["mydatabase"]
highest_previous_primary_key = 1
mycol = db['tweets_test']


es = Elasticsearch(hosts='http://localhost',port=9200)
mappings = {
    "mappings":{
        "tweet": {
            "properties": {
                "text": { "type": "text"  },
                "timestamp": { "type": "date" },
                }
            }
    }
}
es.indices.create(index="test_mongo12", body=mappings)

#actions = []
count = 0
while True:
    cursor = mycol.find({})
    for msg in cursor:
        #print(msg)
        count+= 1
        current_primary_key = int(str(msg['_id'])[-6:],16)
        if current_primary_key > highest_previous_primary_key:
            action = {
                "index": "test_mongo12",
                "type": "tweet",
                "source": {
                    'text' : msg["text"],
                    'timestamp': msg["created_at"],
                    }
            }
            es.create(index = "test_mongo12", doc_type = "tweet", id = count, body = action)
            #print(current_primary_key)
            highest_previous_primary_key = current_primary_key
		#actions.append(json.dumps(action))
		#print(json.dumps(action))
		#if len(actions) >= 500:
			#print(msg.value)
			#helpers.bulk(es, actions, index='test', doc_type='tweet')
			#actions = []