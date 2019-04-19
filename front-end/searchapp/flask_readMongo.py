from flask import Flask
from pymongo import MongoClient
app = Flask(__name__)

@app.route("/")
def hello():
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

    return "total tweets: " + str(totalCount) + "tweets having emoji:" + str(emojiCount)

if __name__ == "__main__":

    app.run()