from elasticsearch import Elasticsearch, helpers

from data import all_products, ProductData

from pymongo import MongoClient


def main():
    # Connect to localhost:9200 by default.
    client = MongoClient(port=27017)
    db = client["mydatabase"]
    highest_previous_primary_key = 1
    highest_previous_primary_key2 = 1
    mycol1 = db['tweets_test']
    mycol = db['tweets_text_sentiment']
    emoji_sentiment = db['tweets_emoji_sentiment']

    es = Elasticsearch()

    es.indices.delete(index="new_tweets4", ignore=404)
    es.indices.create(
        index="new_tweets4",
        body={
            'mappings': {
                "tweet": {
                    'properties': {
                        'text': {'type': 'text'},
                        'timestamp': {'type': 'date'},
                        'country': {'type': 'text'},
                        'textSentScore': {
                            'type': 'text',
                            'fields': {
                                'raw':{
                                    'type': 'keyword'
                                }
                            }
                        },
                        'location':{'type': "geo_point" }
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

    # es.indices.delete(index="emojitweets1", ignore=404)
    # es.indices.create(
    #     index="emojitweets1",
    #     body={
    #         'mappings': {
    #             "tweetEmoji": {
    #                 'properties': {
    #                     'timestamp': {'type': 'date'},
    #                     'emoji' : {'type': 'text'},
    #                     'country': {'type': 'text'},
    #                     'emojiSent': {'type': 'text'}
    #                 }
    #             }
    #         },
    #         'settings': {
    #             'analysis': {
    #                 'analyzer': {
    #                     'custom_english_analyzer': {
    #                         'type': 'english',
    #                         'stopwords': ['made', '_english_']
    #                     }
    #                 }
    #             }
    #         }
    #     },
    # )

    count = 0
    count2 = 0
    while True:
        cursor = mycol.find({}, no_cursor_timeout=True)
        for msg in cursor:
        #print(msg)
            count += 1
            current_primary_key = int(str(msg['_id'])[-6:],16)
            if current_primary_key > highest_previous_primary_key:
                action = {
                    "index": "new_tweets4",
                    "type": "tweet",
                    'text' : msg["text"],
                    'timestamp': msg["created_at"],
                    'country': msg["country"],
                    'textSentScore': msg['sentimentScoreText'],
                    'location': msg['location']
                }
                es.create(index = "new_tweets4", doc_type = "tweet", id = count, body = action)
                #print(msg["created_at"])
                highest_previous_primary_key = current_primary_key

        #emoji collection

        # cursor2 = emoji_sentiment.find({})
        # for msg in cursor2:
        #     count2 += 1
        #     current_primary_key2 = int(str(msg['_id'])[-6:],16)
        #     if current_primary_key2 > highest_previous_primary_key2:
        #         action2 = {
        #             "index": "emojitweets1",
        #             "type": "tweetEmoji",
        #             'timestamp': msg["created_at"],
        #             'emoji': msg['emoji'],
        #             'country': msg["country"],
        #             'emojiSent': msg['sentimentEmoji']
        #         }
        #         es.create(index = "emojitweets1", doc_type = "tweetEmoji", id = count2, body = action2)
        #         #print(msg["created_at"])
        #         highest_previous_primary_key2 = current_primary_key2



'''
    products = all_products()
    bulk_index_products(es, products)
def bulk_index_products(es, products):
    def format_bulk_action(product: ProductData):
        return {
            '_op_type': 'create',
            '_index': total,
            '_type': tweet,
            '_id': product.id,
            '_source': {
                'text': product.name,
                'timestamp': product.image,
                'description': product.description,
            }
        }
    # this is not efficient, for workshop practice only
    actions = [format_bulk_action(product) for product in products]
    helpers.bulk(es, actions)
'''

if __name__ == '__main__':
    main()