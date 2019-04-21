import tweepy
from tweepy import OAuthHandler
import time
from kafka import KafkaConsumer, KafkaProducer
from kafka import SimpleProducer, KafkaClient
import datetime
import codecs
from tweepy import StreamListener,Stream
import json



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

    indiv = "and"
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
            record += "\"ISO_code\":" + json.dumps(geo_info[2])
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
geo_codes = [['USA','40,-100,1600km',"40,-100"],['Japan','38,140,800km',"38,140"],['England','54.6974,-3.8112,350km',"54.69,-3.81"],['Brazil','-9.8864,-50.4513,1600km',"-9.88,-50.45"],['South Africa','-30.2184,24.3814,610km',"-30.22,24.38"],['Australia','-34.9,145.1,1000km',"-34.9,145.1"]]

# 一分钟只能一个request
# 所以60秒钟除以config file的数量
interval = 60

# 为了实现不停地循环loop列表里的信息，建立两个一直递增的index然后取余数(使用列表长度)，从而实现列表index不停循环
# api token config file 列表
config_index_no_stop = 0
# 国家地理信息列表
geo_info_index_no_stop = 0



while True:

    # 正如上文所说，取余数实现列表无限循环loop
    config_index = config_index_no_stop%len(configs)
    geo_info_index = geo_info_index_no_stop%len(geo_codes)

    api = get_api(configs[config_index])
    tweets_processed = 0
    print("--------------------------")
    print("Token: "+str(config_index), ", Country: "+geo_codes[geo_info_index][0])
    
    # 使用try因为有可能碰到429的情况
    try:
        tweets_processed = get_twitter_data_token(config_index,api, geo_codes[geo_info_index])
    except Exception as e:
        print("429了, 等下一轮吧~")
        # 当前token不能用，不要跳到下一个国家，依旧使用当前国家
        geo_info_index_no_stop -= 1
    print("Tweets processed: "+str(tweets_processed))
    time.sleep(interval)

    config_index_no_stop += 1
    geo_info_index_no_stop += 1









