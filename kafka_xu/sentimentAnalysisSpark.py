from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import operator
import numpy as np
import matplotlib.pyplot as plt
def main():
	global labels,colors,all_figs
	all_figs = []
	conf = SparkConf().setMaster("local[2]").setAppName("sentimentAnalysis")
	sc = SparkContext(conf=conf)
	#create a streaming context w/ batch interval 5 sec
	ssc = StreamingContext(sc,5)
	ssc.checkpoint("checkpoint")
	pwords = load_wordlist("positive_words.txt")
	nwords = load_wordlist("negative_words.txt")
	counts = stream(ssc,pwords,nwords,60)
	print("inside main func")
	print("counts:",counts)

def load_wordlist(filename):
	words = {}
	f = open(filename,"rU")
	text = f.read()
	text = text.split('\n')
	for line in text:
		words[line] = 1
	return words
def updateFunction(newValues,runningCount):
	if runningCount is None:
		runningCount = 0
	return sum(newValues,runningCount)
def stream(ssc,pwords,nwords,duration):
	global labels,color,all_figs
	kstream = KafkaUtils.createDirectStream(ssc,topics=['kafkatwitterstream'],kafkaParams={"metadata.broker.list":'localhost:9092'})
	tweets = kstream.map(lambda x:x[1].encode("ascii",ignore))
	words = tweets.flatMap(lambda line:line.split(" "))
	pos = words.map(lambda word:('Positive',1) if word in pwords else ('Positive',0))
	neg = words.map(lambda word:('Negative',1) if word in nwords else ('Negative',0))
	allSentiments = pos.union(neg)
	sentimentCounts = allSentiments.reduceByKey(lambda x,y:x+y)
	runningSentimentCounts = sentimentCounts.updateStateByKey(updateFunction)
	runningCount.print()
	return runningSentimentCounts
main()
