# TeamSimple

Our team aims to create a real-time twitter map with emojis. Big data techniques will be used. 

Current architecture:

tweepy -> kafka -> spark -> mongodb -> elasticsearch -> kibana

## Steps

### To start

Start zookeeper first:

`zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties`

Start Kafka:

`kafka-server-start /usr/local/etc/kafka/server.properties`

Start producer:

Need to be in project folder. Couple librarys might need to be instll by using pip.

`python Tweepy-kafkaProducer.py`

Start Mongo database:

`docker run -d -p 27017-27019:27017-27019 --name mongodb mongo:4.0.4`

Start consumer

`python kafkaConsumerMongo.py`

Start python script that reads tweets from tweets collection --> get emoji --> store emoji counts in emoji collection

`python parseTweetsAndStoreEmojiCounts.py`


### To stop:

`Ctrl+c` for two python scripts

Then Stop Kafka first:

`kafka-server-stop`

Stop Zookeeper:

`zookeeper-server-stop`

Stop and remove docker container for Mongo database:

`docker container stop CONTAINER_NAME`

`docker container rm CONTAINER_NAME`









