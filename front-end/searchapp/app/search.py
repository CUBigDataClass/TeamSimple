from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from typing import List


HEADERS = {'content-type': 'application/json'}


class SearchResult():
    """Represents a product returned from elasticsearch."""
    def __init__(self, text, timestamp, country, textSentScore):
        self.text = text
        self.timestamp = timestamp
        self.country = country
        self.textSentScore = textSentScore

    def from_doc(doc) -> 'SearchResult':
        return SearchResult(
                text = doc.text,
                timestamp = doc.timestamp,
                country = doc.country,
                textSentScore = doc.textSentScore,
            )

class SearchResult_emoji():
    def __init__(self, timestamp, emoji, country, emojiSent):
        self.timestamp = timestamp
        self.emoji = emoji
        self.country = country
        self.emojiSent = emojiSent

    def from_doc(doc) -> 'SearchResult':
        return SearchResult(
                timestamp = doc.timestamp,
                emoji = emoji,
                country = doc.country,
                emojiSent = doc.emojiSent,

            )


def search(term: str):
    client = Elasticsearch()

    # Elasticsearch 6 requires the content-type header to be set, and this is
    # not included by default in the current version of elasticsearch-py
    client.transport.connection_pool.connection.headers.update(HEADERS)

    s = Search(using=client, index="new_tweets4", doc_type="tweet")
    docs = s.query('match', text=term)[0:10000].execute()

    s_emoji = Search(using=client, index="new_emoji4", doc_type="tweetEmoji")
    docs_emoji = s_emoji.query('match', text=term)[0:10000].execute()

    return [[SearchResult.from_doc(d) for d in docs],[SearchResult_emoji.from_doc(e) for e in docs_emoji ]]
