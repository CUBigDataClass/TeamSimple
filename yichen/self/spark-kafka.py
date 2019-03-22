
# coding: utf-8

# In[1]:


from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import os
import findspark

def start():
    os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars spark-streaming-kafka-assembly_2.11-2.4.0.jar pyspark-shell' #note that the "pyspark-shell" part is very important!!
    sconf=SparkConf()
    # sconf.set('spark.streaming.blockInterval','100')
    sconf.set('spark.cores.max' , 8)
    sc=SparkContext(appName='KafkaWordCount',conf=sconf)
    ssc=StreamingContext(sc,6)
    topic = "tweets-kafka-test"
    brokers = "localhost:9092"
    numStreams = 1
    #kafkaStreams = KafkaUtils.createStream(ssc,[topic],kafkaParams={"metadata.broker.list": brokers})
    kafkaStreams = KafkaUtils.createStream(ssc,"localhost:9092","test1",{"tweets-kafka-test":0})# for _ in range (numStreams)]
    dataGet = kafkaStreams.map(lambda line: line[1]) 
    #unifiedStream = ssc.union(*kafkaStreams)
    dataGet.pprint()
    
    ssc.start()             # Start the computation
    ssc.awaitTermination()  # Wait for the computation to terminate

if __name__ == '__main__':
    findspark.init()
    start()


# In[ ]:


pyspark

