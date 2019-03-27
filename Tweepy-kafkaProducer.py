import tweepy
from tweepy import OAuthHandler
import time
from kafka import KafkaConsumer, KafkaProducer
from kafka import SimpleProducer, KafkaClient
import datetime
import codecs
from tweepy import StreamListener,Stream

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


config2 = {}
exec(compile(open("config1.py", "rb").read(), "config1.py", 'exec'), config2)
consumer_key2 = config2["consumer_key"]
consumer_secret2 = config2["consumer_secret"]
access_token2 = config2["access_key"]
access_secret2 = config2["access_secret"]
auth2 = OAuthHandler(consumer_key2, consumer_secret2)
auth2.set_access_token(access_token2, access_secret2)
api2 = tweepy.API(auth2)


config3 = {}
exec(compile(open("config3.py", "rb").read(), "config3.py", 'exec'), config3)
consumer_key3 = config3["consumer_key"]
consumer_secret3 = config3["consumer_secret"]
access_token3 = config3["access_key"]
access_secret3 = config3["access_secret"]
auth3 = OAuthHandler(consumer_key3, consumer_secret3)
auth3.set_access_token(access_token3, access_secret3)
api3 = tweepy.API(auth3)
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

'''class tweetlistener(StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        client = KafkaClient("localhost:9092")
        #print(client)

        #https://kafka-python.readthedocs.io/en/1.0.1/apidoc/SimpleProducer.html
        self.producer = SimpleProducer(client, async = True, batch_send_every_n = 1000, batch_send_every_t = 10)
        print("after init producer")

    def on_status(self, status):
        global file, outfile, counter

        print(counter)
        counter += 1
        record = ''
        record += str(status.text)
        record += ';'
        record += str(status.created_at)
           
        print(record)
        print('------------------------------------------------------------------------')    
        outfile.write(record)
        outfile.write('------------------------------------------------------------------------')
        outfile.write(str("\n"))

        #send data using kafka producer to kafka topic
        msg = status.text.encode("utf-8")
        try:
            self.producer.send_messages('kafkatwitterstream',msg)
        except Exception as e:
            print(e)
            return False
        return True
        
    def on_error(self, status_code):
        if status_code == 420:
            return False'''

'''def get_twitter_data():
    global file, outfile, counter
    indiv = "and"
    counter = 0
    file = "/Users/hanxu/Desktop/TeamSimple/tweetcount_" + str(indiv) + ".txt"
    outfile = codecs.open(file, 'w', "utf-8")
    twitterStream = Stream(auth, tweetlistener(api)) 
    twitterStream.filter()'''


def get_twitter_data_token1():
    indiv = "and"
    count = 0
    file = "/home/yichen/Downloads/tweetcount_"+ str(indiv) + str(call_api_count) + ".txt"
    #file = "/Users/hanxu/Desktop/TeamSimple/tweetcount_" + str(indiv) + str(call_api_count) + ".txt"
    outfile = codecs.open(file, 'w', "utf-8")
    currentTime = str(datetime.datetime.utcnow().date())
    a = tweepy.Cursor(api.search, q = str(indiv), since = currentTime).items(3000)
    now = datetime.datetime.utcnow()
    for t in a:
        shouldContinue = True
        tweetTime = t.created_at # get the current time of the tweet
        
        interval = now - tweetTime # subtract tweetTime from currentTime
        count += 1
        if interval.seconds <= 21: #get interval in seconds and use your time constraint in seconds (mine is 1hr and 5 mins = 3900secs)
            record = ''
            record += str(t.text)
            record += ';'
            record += str(t.created_at)
            
            outfile.write(str(now))
            outfile.write(record)
            outfile.write('------------------------------------------------------------------------')
            outfile.write(str("\n"))
            try:
                #producer.send_messages('kafkatwitterstream_' + str(indiv),t.text.encode("utf-8"))
                producer.send_messages('es_test', record.encode("utf-8"))
                #print(record)
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
                #producer.send_messages('kafkatwitterstream_'+ str(indiv),t.text.encode("utf-8"))
                producer.send_messages('es_test', record.encode("utf-8"))
            except Exception as e:
                print(e)
                break

        #print('\n')

        if not shouldContinue: # check if tweet is still within time range. Tweet returned are ordered according to recent already.
            print('exiting the loop')
            break
    print(count)


def get_twitter_data_token2():
    indiv = "and"
    count = 0
    file = "/home/yichen/Downloads/tweetcount_"+ str(indiv) + str(call_api_count) + ".txt"
    #file = "/Users/hanxu/Desktop/TeamSimple/tweetcount_" + str(indiv) + str(call_api_count) + ".txt"
    outfile = codecs.open(file, 'w', "utf-8")
    currentTime = str(datetime.datetime.utcnow().date())
    a = tweepy.Cursor(api2.search, q = str(indiv), since = currentTime).items(3000)
    now = datetime.datetime.utcnow()
    for t in a:
        shouldContinue = True
        tweetTime = t.created_at # get the current time of the tweet
        
        interval = now - tweetTime # subtract tweetTime from currentTime
        count += 1
        if interval.seconds <= 21: #get interval in seconds and use your time constraint in seconds (mine is 1hr and 5 mins = 3900secs)
            record = ''
            record += str(t.text)
            record += ';'
            record += str(t.created_at)
            
            outfile.write(str(now))
            outfile.write(record)
            outfile.write('------------------------------------------------------------------------')
            outfile.write(str("\n"))
            try:
                #producer.send_messages('kafkatwitterstream2_' + str(indiv),t.text.encode("utf-8"))
                producer.send_messages('es_test', record.encode("utf-8"))
                #print(record)
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
                #producer.send_messages('kafkatwitterstream2_'+ str(indiv),t.text.encode("utf-8"))
                producer.send_messages('es_test', record.encode("utf-8"))
            except Exception as e:
                print(e)
                break

        #print('\n')

        if not shouldContinue: # check if tweet is still within time range. Tweet returned are ordered according to recent already.
            print('exiting the loop')
            break
    print("token2:"+ str(count))


def get_twitter_data_token3():
    indiv = "and"
    count = 0
    file = "/home/yichen/Downloads/tweetcount_"+ str(indiv) + str(call_api_count) + ".txt"
    #file = "/Users/hanxu/Desktop/TeamSimple/tweetcount_" + str(indiv) + str(call_api_count) + ".txt"
    outfile = codecs.open(file, 'w', "utf-8")
    currentTime = str(datetime.datetime.utcnow().date())
    a = tweepy.Cursor(api3.search, q = str(indiv), since = currentTime).items(3000)
    now = datetime.datetime.utcnow()
    for t in a:
        shouldContinue = True
        tweetTime = t.created_at # get the current time of the tweet
        
        interval = now - tweetTime # subtract tweetTime from currentTime
        count += 1
        if interval.seconds <= 21: #get interval in seconds and use your time constraint in seconds (mine is 1hr and 5 mins = 3900secs)
            record = ''
            record += str(t.text)
            record += ';'
            record += str(t.created_at)
            
            outfile.write(str(now))
            outfile.write(record)
            outfile.write('------------------------------------------------------------------------')
            outfile.write(str("\n"))
            try:
                #producer.send_messages('kafkatwitterstream2_' + str(indiv),t.text.encode("utf-8"))
                producer.send_messages('es_test', record.encode("utf-8"))
                #print(record)
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
                #producer.send_messages('kafkatwitterstream2_'+ str(indiv),t.text.encode("utf-8"))
                producer.send_messages('es_test', record.encode("utf-8"))
            except Exception as e:
                print(e)
                break

        #print('\n')

        if not shouldContinue: # check if tweet is still within time range. Tweet returned are ordered according to recent already.
            print('exiting the loop')
            break
    print("token3:"+ str(count))

#get twitter data every 6 secs
def periodic_work(interval):
    global call_api_count 
    global file, outfile, counter
    call_api_count = 0
    #print(call_api_count)
    while True:
        get_twitter_data_token1()
        #interval should be an integer, the number of seconds to wait
        time.sleep(interval)
        get_twitter_data_token2()
        time.sleep(interval)
        get_twitter_data_token3()
        time.sleep(interval)

periodic_work(300)
