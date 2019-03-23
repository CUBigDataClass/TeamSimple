import tweepy
import time
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime,timedelta

#setting up twitter authentication details
access_key = "183318037-X55KeNRcwNIUlXQNvFxTFWxCIiXIjmXtKboT "
access_secret = "FXH25B24OcdW54ilKDxcee274aqfNNj9C3Ps1J9bVW"
consumer_key = "qMplSgIp0ekz3Lpjs3w4tKQ"
consumer_secret = "FI8ulEiCWiThkfxlK18LLcYe8kXLzOJsFzKksMorhncNJ "


#creating authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#setting access to token and secret
auth.set_access_token(access_key, access_secret)
api= tweepy.API(auth)


def normalize_timestamp(time):
    mytime= datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
    mytime+= timedelta(hours=1)
    return (mytime.strftime(("%Y-%m-%d %H:%M:%S")))

producer = KafkaProducer(bootstrap_servers='localhost:9092')
topic_name = 'tweets-lambda1'

def get_twitter_data():
    res = api.search("Martin King OR Martin Luther")
    for i in res:
        record = ''
        record += str(i.user.id_str)
        record += ';'
        record += str(normalize_timestamp(str(i.created_at)))
        record += ';'
        record += str(i.user.followers_count)
        record += ';'
        record += str(i.user.location)
        record += ';'
        record += str(i.favorite_count)
        record += ';'
        record += str(i.retweet_count)
        record += ';'
        producer.send(topic_name, str.encode(record))

get_twitter_data()

def periodic_work(interval):
    while True:
        get_twitter_data()
        #interval should be an integer, the number of seconds to wait
        time.sleep(interval)
periodic_work(60*1)  # get data every couple of minutes
