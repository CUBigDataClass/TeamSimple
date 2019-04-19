from flask import Flask, render_template, request
from pymongo import MongoClient
from app.search import search

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    """
    Search for products across a variety of terms, and show 9 results for each.
    """
    '''
    search_terms = [
        'necklace',
        'metal necklace',
        'necklce',
        'OK',
        'brass necklace',
        'a brass necklace',
        'necklaces made of brass',
        "men's jacket",
    ]

    products_by_category = [(t, search(t)) for t in search_terms]
    '''

    #tweets and emoji count
    count = 0
    client = MongoClient('localhost', 27017)
    mydb = client['mydatabase']
    # Source collection to read from.
    tweets_collection = mydb['tweets_test']
    # Collection to store sentiment and emoji count
    tweets_with_sentiment_collection = mydb['tweets_with_sentiment_test']
    emoji_collection = mydb['emojis_test']
    
    totalCount = tweets_collection.count()
    emojiCount = emoji_collection.count()



    #updated time
    return render_template(
        'index.html',
        totalCount = totalCount,
        emojiCount = emojiCount
    )


@app.route('/search', methods=['GET', 'POST'])
def search_single_product():
    """
    Execute a search for a specific search term.

    """
    query = request.args.get('search')
    searched_results = [(query, search(query))]
    
    return render_template(
        'search.html',
        search_term=query,
        totalCount = len(search(query)),


    )


