from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from typing import List


HEADERS = {'content-type': 'application/json'}


class SearchResult():
    """Represents a product returned from elasticsearch."""
    def __init__(self, text, timestamp):
        self.text = text
        self.timestamp = timestamp

    def from_doc(doc) -> 'SearchResult':
        return SearchResult(
                text = doc.text,
                timestamp = doc.timestamp,
            )


def search(term: str) -> List[SearchResult]:
    client = Elasticsearch()

    # Elasticsearch 6 requires the content-type header to be set, and this is
    # not included by default in the current version of elasticsearch-py
    client.transport.connection_pool.connection.headers.update(HEADERS)

    s = Search(using=client, index="total6", doc_type="tweet")
    docs = s.query('match', text=term)[0:10000].execute()

    return [SearchResult.from_doc(d) for d in docs]
