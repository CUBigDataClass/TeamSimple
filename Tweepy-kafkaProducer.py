import tweepy
from tweepy import OAuthHandler
import time
from kafka import KafkaConsumer, KafkaProducer
from kafka import SimpleProducer, KafkaClient
import datetime
import codecs
from tweepy import StreamListener

#twitter setup
config = {}
exec(compile(open("config.py", "rb").read(), "config.py", 'exec'), config)
consumer_key = config["consumer_key"]
consumer_secret = config["consumer_secret"]
access_token = config["access_key"]
access_secret = config["access_secret"]
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#normalize timestamp
#def normalize_timestamp(time):
    #mytime = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    #mytime += timedelta(hours=1)   # the tweets are timestamped in GMT timezone, while I am in +1 timezone
    #return (mytime.strftime("%Y-%m-%d %H:%M:%S"))

#defining the kafka producer
#producer = KafkaProducer(bootstrap_servers='localhost:9092')
#topic_name = 'tweets-kafka-test'
kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)

#twitter api to kafka
class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)
        
    def on_error(self, status_code):
        if status_code == 420:
            return False

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=["google"],languages=["en"])


'''def get_twitter_data():
    indiv = "and"
    count = 0
    file = "/Users/hanxu/Desktop/TeamSimple/tweetcount_" + str(indiv) + str(call_api_count) + ".txt"
    outfile = codecs.open(file, 'w', "utf-8")
    currentTime = str(datetime.datetime.utcnow().date())
    for t in tweepy.Cursor(api.search, q = str(indiv), include_entities=True, since = currentTime).items(10000):
        shouldContinue = True
        tweetTime = t.created_at # get the current time of the tweet
        now = datetime.datetime.utcnow()
        interval = now - tweetTime # subtract tweetTime from currentTime
        count += 1
        if interval.seconds <= 20: #get interval in seconds and use your time constraint in seconds (mine is 1hr and 5 mins = 3900secs)
            record = ''
            record += str(t.text)
            record += ';'
            record += str(t.created_at)
            
            outfile.write(str(now))
            outfile.write(record)
            outfile.write('------------------------------------------------------------------------')
            outfile.write(str("\n"))
            try:
                producer.send_messages('kafkatwitterstream_' + str(indiv),t.text.encode("utf-8"))
            except Exception as e:
                print(e)
                break
        else:
            shouldContinue = False
            record = ''
            record += str(t.text)
            record += ';'
            record += str(t.created_at)
    
            outfile.write(str(now))
            outfile.write(record)
            outfile.write('------------------------------------------------------------------------')
            outfile.write(str("\n"))
            try:
                producer.send_messages('kafkatwitterstream_'+ str(indiv),t.text.encode("utf-8"))
            except Exception as e:
                print(e)
                break

        #print('\n')

        if not shouldContinue: # check if tweet is still within time range. Tweet returned are ordered according to recent already.
            print('exiting the loop')
            break
    print(count)
    '''

#get twitter data every 6 secs
def periodic_work(interval):
    global call_api_count 
    call_api_count = 0
    #print(call_api_count)
    while True:
        get_twitter_data()
        call_api_count += 1
        #interval should be an integer, the number of seconds to wait
        time.sleep(interval)

#periodic_work(6)

