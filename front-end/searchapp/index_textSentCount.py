from elasticsearch import Elasticsearch, helpers

from data import all_products, ProductData

from pymongo import MongoClient


def main():
    # Connect to localhost:9200 by default.
    client = MongoClient(port=27017)
    db = client["mydatabase"]
    highest_previous_primary_key = 1
    highest_previous_primary_key2 = 1

    mycol = db['text_sentiment_count']

    es = Elasticsearch()

    es.indices.delete(index="textSentCount", ignore=404)
    es.indices.create(
        index="textSentCount",
        body={
            'mappings': {
                "sentCount": {
                    'properties': {
                        'sentmentLabel': {'type': 'text'},
                        'countSent': {'type': 'int'}
                    }
                },
            },
            'settings': {
                'analysis': {
                    'analyzer': {
                        'custom_english_analyzer': {
                            'type': 'english',
                            'stopwords': ['made', '_english_']
                        }
                    }
                }
            }
        },
    )


    count = 0
    count2 = 0
    while True:
        cursor = mycol.find({})
        for msg in cursor:
        #print(msg)
            count += 1
            current_primary_key = int(str(msg['_id'])[-6:],16)
            if current_primary_key > highest_previous_primary_key:
                action = {
                    "index": "textSentCount",
                    "type": "sentCount",
                    'sentmentLabel' : msg["sentimentScoreText"],
                    'countSent': msg["count"],
                }
                es.create(index = "textSentCount", doc_type = "sentCount", id = count, body = action)
                #print(msg["created_at"])
                highest_previous_primary_key = current_primary_key

if __name__ == '__main__':
    main()
