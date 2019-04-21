from elasticsearch import Elasticsearch, helpers

from data import all_products, ProductData

from pymongo import MongoClient


def main():
    # Connect to localhost:9200 by default.
    client = MongoClient(port=27017)
    db = client["mydatabase"]
    highest_previous_primary_key = 1
    highest_previous_primary_key2 = 1
    mycol = db['tweets_text_sentiment']
    emoji_sentiment = db['tweets_emoji_sentiment']
    es = Elasticsearch()

    es.indices.delete(index="emojitweets6", ignore=404)
    es.indices.create(
        index="emojitweets6",
        body={
            'mappings': {
                "tweetEmoji": {
                    'properties': {
                        'timestamp': {'type': 'date'},
                        'emoji' : { 
                            'type': 'text',
                            'fields': {
                                'raw':{
                                    'type': 'keyword'
                                }
                            }
                        },
                        'country': {'type': 'text'},
                        'emojiSent': {
                            'type': 'text',
                            'fields': {
                                'raw':{
                                    'type': 'keyword'
                                }
                            }
                        }
                    }
                }
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

    count2 = 0
    while True:

        #emoji collection
        cursor2 = emoji_sentiment.find({})
        for msg in cursor2:
            count2 += 1
            current_primary_key2 = int(str(msg['_id'])[-6:],16)
            if current_primary_key2 > highest_previous_primary_key2:
                action2 = {
                    "index": "emojitweets6",
                    "type": "tweetEmoji",
                    'timestamp': msg["created_at"],
                    'emoji': msg['emoji'],
                    'country': msg["country"],
                    'emojiSent': msg['sentimentEmoji']
                }
                es.create(index = "emojitweets6", doc_type = "tweetEmoji", id = count2, body = action2)
                #print(msg["created_at"])
                highest_previous_primary_key2 = current_primary_key2


if __name__ == '__main__':
    main()
