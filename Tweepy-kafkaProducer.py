import tweepy
from tweepy import OAuthHandler
import time
from kafka import KafkaConsumer, KafkaProducer
from kafka import SimpleProducer, KafkaClient
import datetime
import codecs
from tweepy import StreamListener,Stream
import json
# from random import shuffle



# Get twitter api based on a local config file
def get_api(config_file):

    config = {}
    exec(compile(open(config_file, "rb").read(), config_file, 'exec'), config)
    consumer_key = config["consumer_key"]
    consumer_secret = config["consumer_secret"]
    access_token = config["access_key"]
    access_secret = config["access_secret"]
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit_notify=True)

    return api



# Get twitts from api based on geo info and send to kafaka server as producer
def get_twitter_data_token(index, api, geo_info):

    indiv = "and OR の OR y"
    count = 0
    call_api_count = 0
    #file = "./tweetcount_"+ str(indiv) + str(call_api_count) + ".txt"

    #outfile = codecs.open(file, 'w', "utf-8")
    currentTime = str(datetime.datetime.utcnow().date())
    a = tweepy.Cursor(api.search, q = str(indiv), since = currentTime, geocode=geo_info[1]).items(3000)

    now = datetime.datetime.utcnow()
    for t in a:
        shouldContinue = True
        tweetTime = t.created_at # get the current time of the tweet
        
        interval = now - tweetTime # subtract tweetTime from currentTime
        count += 1
        if interval.seconds <= 50: #get interval in seconds and use your time constraint in seconds (mine is 1hr and 5 mins = 3900secs)
            record = '{'
            record += "\"created_at\":" +  json.dumps(str(t.created_at)[:10]+'T'+str(t.created_at)[11:]+'Z')
            record += ','
            record += "\"text\":" +  json.dumps(str(t.text))
            record += ','
            record += "\"country\":" +  json.dumps(geo_info[0])
            record += ','
            record += "\"location\":" + json.dumps(geo_info[2])
            record += '}'
            
            #outfile.write(str(now))
            #outfile.write(record)
            #outfile.write('------------------------------------------------------------------------')
            #outfile.write(str("\n"))
            try:
                    #producer.send_messages('kafkatwitterstream_' + str(indiv),t.text.encode("utf-8"))
                producer.send_messages('tweepy-kafka-test1', str.encode(record))
            #print(record)
            except Exception as e:
                print(e)
                break
        else:
            shouldContinue = False
            record = '{'
            record += "\"created_at\":" +  json.dumps(str(t.created_at)[:10]+'T'+str(t.created_at)[11:]+'Z')
            record += ','
            record += "\"text\":" +  json.dumps(str(t.text))
            record += ','
            record += "\"country\":" +  json.dumps(geo_info[0])
            record += ','
            record += "\"location\":" + json.dumps(geo_info[2])
            record += '}'
            
            # outfile.write(str(now))
            # outfile.write(record)
            # outfile.write('------------------------------------------------------------------------')
            # outfile.write(str("\n"))
            try:
                #producer.send_messages('kafkatwitterstream_' + str(indiv),t.text.encode("utf-8"))
                producer.send_messages('tweepy-kafka-test1', str.encode(record))

            except Exception as e:
                print(e)
                break

        if not shouldContinue: # check if tweet is still within time range. Tweet returned are ordered according to recent already.
            #print('exiting the loop')
            break
    return count



  

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)

configs = ['config0.py','config1.py','config2.py','config3.py','config4.py','config5.py','config6.py']
# shuffle(configs)
geo_codes = [['USA','40,-100,1600km',"40,-100"],['Japan','38,140,800km',"38,140"],['England','54.6974,-3.8112,350km',"54.69,-3.81"],['Brazil','-9.8864,-50.4513,1600km',"-9.88,-50.45"],['South Africa','-30.2184,24.3814,610km',"-30.22,24.38"],['Australia','-34.9,145.1,1000km',"-34.9,145.1"]]

# Only one request is allowed per minute.
interval = 60

# We would like to keep looping items in both arrays.
# In order to do that we define two variables and make them incrementing and divide them by 
# len of the array and take the residue. By doing this we could loop from beging to the end infinitely.
# Two arrays we would like to loop: api token, config file



config_index_no_stop = 0
# country geo info array index big number.
geo_info_index_no_stop = 0



while True:

    config_index = config_index_no_stop%len(configs)
    geo_info_index = geo_info_index_no_stop%len(geo_codes)

    api = get_api(configs[config_index])
    tweets_processed = 0
    print("--------------------------")
    print("Token: "+str(config_index), ", Country: "+geo_codes[geo_info_index][0])
    
    # We might have 429 response which means that our twitter api time frame is used up.
    try:
        tweets_processed = get_twitter_data_token(config_index,api, geo_codes[geo_info_index])
    except Exception as e:
        print("429, wait for next token")
        # If we have a 429
        # Then we need to use next token
        # But do not turn to next country
        geo_info_index_no_stop -= 1
    print("Tweets processed: "+str(tweets_processed))
    time.sleep(interval)

    config_index_no_stop += 1
    geo_info_index_no_stop += 1









