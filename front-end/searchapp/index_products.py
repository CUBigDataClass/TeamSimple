from elasticsearch import Elasticsearch, helpers

from data import all_products, ProductData

from pymongo import MongoClient


def main():
    # Connect to localhost:9200 by default.
    client = MongoClient(port=27017)
    db = client["mydatabase"]
    highest_previous_primary_key = 1
    mycol = db['tweets_test']
    
    es = Elasticsearch()

    es.indices.delete(index="total6", ignore=404)
    es.indices.create(
        index="total6",
        body={
            'mappings': {
                "tweet": {
                    'properties': {
                        'text': {'type': 'text'},
                        'timestamp': {'type': 'date'},
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

    count = 0
    while True:
        cursor = mycol.find({})
        for msg in cursor:
        #print(msg)
            count+= 1
            current_primary_key = int(str(msg['_id'])[-6:],16)
            if current_primary_key > highest_previous_primary_key:
                action = {
                    "index": "total6",
                    "type": "tweet",
                    'text' : msg["text"],
                    'timestamp': msg["created_at"],
                }
                es.create(index = "total6", doc_type = "tweet", id = count, body = action)
                #print(msg["created_at"])
                highest_previous_primary_key = current_primary_key

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
