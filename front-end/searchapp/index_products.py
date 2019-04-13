from elasticsearch import Elasticsearch, helpers

from constants import DOC_TYPE, INDEX_NAME
from data import all_products, ProductData


def main():
    # Connect to localhost:9200 by default.
    es = Elasticsearch()

    es.indices.delete(index=INDEX_NAME, ignore=404)
    es.indices.create(
        index=INDEX_NAME,
        body={
            'mappings': {
                DOC_TYPE: {
                    'properties': {
                        'name': {
                            'type': 'text',
                            'fields': {
                                'english_analyzed': {
                                    'type': 'text',
                                    'analyzer': 'custom_english_analyzer',
                                }
                            }
                        },
                        'description': {
                            'type': 'text',
                            'fields': {
                                'english_analyzed': {
                                    'type': 'text',
                                    'analyzer': 'custom_english_analyzer',
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

    products = all_products()
    bulk_index_products(es, products)
    #index_product(es, all_products()[0])


def index_product(es, product: ProductData):
    """Add a single product to the ProductData index."""

    es.create(
        index=INDEX_NAME,
        doc_type=DOC_TYPE,
        id=product.id,
        body={
            "name": product.name,
            "image": product.image,
            "description": product.description,
        }
    )

    # Don't delete this! You'll need it to see if your indexing job is working,
    # or if it has stalled.
    print("Indexed {}".format(product.name))

def bulk_index_products(es, products):
    def format_bulk_action(product: ProductData):
        return {
            '_op_type': 'create',
            '_index': INDEX_NAME,
            '_type': DOC_TYPE,
            '_id': product.id,
            '_source': {
                'name': product.name,
                'image': product.image,
                'description': product.description,
            }
        }
    # this is not efficient, for workshop practice only
    actions = [format_bulk_action(product) for product in products]
    helpers.bulk(es, actions)

if __name__ == '__main__':
    main()
