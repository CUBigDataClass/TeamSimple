# TeamSimple

Our team aimed to create a real-time twitter map with emojis displaying sentiments of the selected regions for creating a data story. Big data techniques are used through out the implementation of the project.

Current architecture:

![Screenshot](Arch1.png)

## Steps

### To start

#### Back End

**on macOS**

1. Start zookeeper first:

   `zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties`

2. Start Kafka:

   `kafka-server-start /usr/local/etc/kafka/server.properties`

3. Start producer:

   Need to be in project folder. Couple libraries might need to be install by using pip.
   
   Read tweets from twitter API, then send it to kafka

   `python Tweepy-kafkaProducer.py`

4. Start Mongo database:

   `docker run -d -p 27017-27019:27017-27019 --name mongodb mongo:4.0.4`

5. Start consumer
   
   read the tweets from kafka to Mongodb.

   `python kafkaConsumerMongo.py`

6. Start python script that reads tweets from tweets collection --> get emoji --> store emoji counts in emoji collection

   `python sentimentAnalysis-mongo.py`

7. Run Spark analysis

   `python sparkAnalysis_countTextSent.py`
   
   `python SparkSentiment.py`

#### Front End

**on macOS**

1. start `elasticsearch` and `kibana`

   Run:

   `elasticsearch`

   `kibana`

2. activate virtual machine

   in `front-end` folder run:

   `source [VENVNAME]/bin/activate`

3. run two Python script
   
   Search tweets and emojitweets
   
   `python searchapp/index_tweets.py`

   `python searchapp/index_emojitweets.py`

4. Run website

   `python searchapp/run.py`


### To stop:

`Ctrl+c` for two python scripts

Then Stop Kafka first:

`kafka-server-stop`

Stop Zookeeper:

`zookeeper-server-stop`

Stop and remove docker container for Mongo database:

`docker container stop CONTAINER_NAME`

`docker container rm CONTAINER_NAME`


### Demo: 

Link to the live Demo:
Link to the video:


