
# coding: utf-8

# # Getting Started with Spark Streaming with Python and Kafka

# Last month I wrote a [series of articles](https://www.rittmanmead.com/blog/2016/12/etl-offload-with-spark-and-amazon-emr-part-5/) in which I looked at the use of Spark for performing data transformation and manipulation. This was in the context of replatforming an existing Oracle-based ETL and datawarehouse solution onto cheaper and more elastic alternatives. The processing that I wrote was very much batch-focussed; read a set of files from block storage ('disk'), process and enrich the data, and write it back to block storage.
# 
# In this article I am going to look at [Spark Streaming](http://spark.apache.org/streaming/). This is one of several libraries that the [Spark platform](http://spark.apache.org) provides (others include [Spark SQL](http://spark.apache.org/sql/), [Spark MLlib](http://spark.apache.org/mllib/), and [Spark GraphX](http://spark.apache.org/graphx/)). Spark Streaming provides a way of processing "unbounded" data - commonly referred to as "streaming" data. It does this by breaking it up into microbatches, and supporting windowing capabilities for processing across multiple batches. 
# 
# ![](http://spark.apache.org/docs/latest/img/streaming-flow.png)
# 
# ([img src](http://spark.apache.org/docs/latest/streaming-programming-guide.html))
# 
# The use-case I'm going to put together is - almost inevitably for a generic unbounded data example - using Twitter, read from a Kafka topic.  We'll start simply, counting the number of tweets per user within each batch and doing some very simple string manipulations. After that we'll see how to do the same but over a period of time (windowing). In the next blog we'll extend this further into a more useful example, still based on Twitter but demonstrating how to satisfy some real-world requirements in the processing.
# 
# I developed all of this code using Jupyter Notebooks. I've written before about how awesome notebooks are (as well as Jupyter, there's Apache Zeppelin). As well as providing a superb development environment in which the results of code can be seen, Jupyter gives the option to download a Notebook to [Markdown]](https://en.wikipedia.org/wiki/Markdown), on which this blog runs - so in fact what you're reading here comes natively from the notebook in which I developed the code. Pretty cool.
# 
# ![](images/ssc01.png) 
# 
# I used the docker image [all-spark-notebook](https://github.com/jupyter/docker-stacks/tree/master/all-spark-notebook) to provide both Jupyter and the Spark runtime environment. The only external aspect was a Kafka cluster that I had already, with tweets from the live Twitter feed on a kafka topic imaginatively called `twitter`. 

# ## Preparing the Environment
# 
# We need to make sure that the packages we're going to use are available to Spark. Instead of downloading `jar` files and worrying about paths, we can instead use the `--packages` option and specify the group/artifact/version based on what's available on [Maven](http://search.maven.org/#search%7Cgav%7C1%7Cg%3A%22org.apache.spark%22%20AND%20a%3A%22spark-streaming-kafka-0-8-assembly_2.11%22) and Spark will handle the downloading. We specify `PYSPARK_SUBMIT_ARGS` for this to get passed correctly when executing from within Jupyter. 
# 
# To run the code in Jupyter, you can put the cursor in each cell and press Shift-Enter to run it each cell at a time -- or you can use menu option `Kernel` -> `Restart & Run All`. When a cell is executing you'll see a `[*]` next to it, and once the execution is complete this changes to `[y]` where `y` is execution step number. Any output from that step will be shown immediately below it.
# 
# To run the code standalone, you would download the `.py` from Jupyter, and execute it using 
# 
#     /usr/local/spark-2.0.2-bin-hadoop2.7/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 spark_code.py

# In[1]:


import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'


# ### Import dependencies
# 
# We need to import the necessary pySpark modules for Spark, Spark Streaming, and Spark Streaming with Kafka. We also need the python `json` module for parsing the inbound twitter data

# In[2]:


#    Spark
from pyspark import SparkContext
#    Spark Streaming
from pyspark.streaming import StreamingContext
#    Kafka
from pyspark.streaming.kafka import KafkaUtils
#    json parsing
import json


# ### Create Spark context
# 
# The Spark context is the primary object under which everything else is called. The `setLogLevel` call is optional, but saves a lot of noise on stdout that otherwise can swamp the actual outputs from the job. 

# In[3]:


sc = SparkContext(appName="PythonSparkStreamingKafka_RM_01")
sc.setLogLevel("WARN")


# ### Create Streaming Context
# 
# We pass the Spark context (from above) along with the batch duration (here, 60 seconds). 
# 
# See the [API reference](http://spark.apache.org/docs/latest/api/python/pyspark.streaming.html#pyspark.streaming.StreamingContext) and [programming guide](http://spark.apache.org/docs/latest/streaming-programming-guide.html#initializing-streamingcontext) for more details. 

# In[4]:


ssc = StreamingContext(sc, 60)


# ### Connect to Kafka
# 
# Using the native Spark Streaming Kafka capabilities, we use the streaming context from above to connect to our Kafka cluster. The topic connected to is `twitter`, from consumer group `spark-streaming`. The latter is an arbitrary name that can be changed as required. 
# 
# For more information see the [documentation](http://spark.apache.org/docs/latest/streaming-kafka-0-8-integration.html).

# In[5]:


kafkaStream = KafkaUtils.createStream(ssc, 'localhost:9092', 'spark-streaming', {'kafkatwitterstream_and':1})


# ## Message Processing

# ### Parse the inbound message as json
# 
# The inbound stream is a [`DStream`](http://spark.apache.org/docs/2.0.0/api/python/pyspark.streaming.html#pyspark.streaming.DStream), which supports various built-in [transformations](http://spark.apache.org/docs/latest/streaming-programming-guide.html#transformations-on-dstreams) such as `map` which is used here to parse the inbound messages from their native JSON format. 
# 
# Note that this will fail horribly if the inbound message _isn't_ valid JSON. 

# In[6]:


parsed = kafkaStream.map(lambda v: json.loads(v[1]))


# ### Count number of tweets in the batch
# 
# The [`DStream`](http://spark.apache.org/docs/2.0.0/api/python/pyspark.streaming.html#pyspark.streaming.DStream) object provides native functions to count the number of messages in the batch, and to print them to the output: 
# 
# * [`count`](http://spark.apache.org/docs/2.0.0/api/python/pyspark.streaming.html#pyspark.streaming.DStream.count)
# * [`pprint`](http://spark.apache.org/docs/2.0.0/api/python/pyspark.streaming.html#pyspark.streaming.DStream.pprint) 
# 
# We use the `map` function to add in some text explaining the value printed. 
# 
# _Note that nothing gets written to output from the Spark Streaming context and descendent objects until the Spark Streaming Context is started, which happens later in the code_
# 
# _*`pprint` by default only prints the first 10 values*_

# In[7]:


parsed.count().map(lambda x:'Tweets in this batch: %s' % x).pprint()


# Note that if you jump ahead and try to use Windowing at this point, for example to count the number of tweets in the last hour using the `countByWindow` function, it'll fail. This is because we've not set up the streaming context with a checkpoint directory yet. You'll get the error: `java.lang.IllegalArgumentException: requirement failed: The checkpoint directory has not been set. Please set it by StreamingContext.checkpoint().`. See later on in the blog for details about how to do this. 

# ### Extract Author name from each tweet
# 
# Tweets come through in a JSON structure, of which you can see an [example here](https://gist.github.com/rmoff/3968605712f437a1f37e7be52129cade). We're going to analyse tweets by author, which is accessible in the json structure at `user.screen_name`. 
# 
# The [`lambda`](https://pythonconquerstheuniverse.wordpress.com/2011/08/29/lambda_tutorial/) anonymous function is used to apply the `map` to each RDD within the DStream. The result is a DStream holding just the author's screenname for each tweet in the original DStream.

# In[8]:


authors_dstream = parsed.map(lambda tweet: tweet['user']['created_at'])


# ### Count the number of tweets per author
# 
# With our authors DStream, we can now count them using the `countByValue` function. This is conceptually the same as this quasi-SQL statement: 
# 
#     SELECT   AUTHOR, COUNT(*)
#     FROM     DSTREAM
#     GROUP BY AUTHOR
# 
# _Using `countByValue` is a more legible way of doing the same thing that you'll see done in tutorials elsewhere with a map / reduceBy. _

# In[9]:


author_counts = authors_dstream.countByValue()
author_counts.pprint()


# ### Sort the author count
# 
# If you try and use the `sortBy` function directly against the DStream you get an error: 
# 
#     'TransformedDStream' object has no attribute 'sortBy'
#     
# This is because sort is not a built-in [DStream](http://spark.apache.org/docs/2.0.0/api/python/pyspark.streaming.html#pyspark.streaming.DStream) function, we use the [`transform`](http://spark.apache.org/docs/latest/streaming-programming-guide.html#transform-operation) function to access [`sortBy`](http://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.RDD.sortBy) from pySpark. 
# 
# To use `sortBy` you specify a lambda function to define the sort order. Here we're going to do it based on first the author name (index 0 of the RDD), and then of that order, by number of tweets (index 1 of the RDD). You'll note these index references being used in the `sortBy` lambda function `x[0]` and `x[1]`. Thanks to [user6910411](http://stackoverflow.com/a/41485394/350613) on StackOverflow for a better way of doing this. 
# 
# _Here I'm using `\` as line continuation characters to make the code more legible._

# In[10]:


author_counts_sorted_dstream = author_counts.transform(  (lambda foo:foo   .sortBy(lambda x:( -x[1]))))
#   .sortBy(lambda x:(x[0].lower(), -x[1]))\
#  ))


# In[11]:


author_counts_sorted_dstream.pprint()


# ### Get top 5 authors by tweet count
# 
# To display just the top five authors, based on number of tweets in the batch period, we'll using the [`take`](http://spark.apache.org/docs/2.0.2/api/python/pyspark.html#pyspark.RDD.take) function. My first attempt at this failed with: 
# 
#     AttributeError: 'list' object has no attribute '_jrdd'
#         
# Per my [woes on StackOverflow](http://stackoverflow.com/questions/41483746/transformed-dstream-in-pyspark-gives-error-when-pprint-called-on-it) a `parallelize` is necessary to return the values into a DStream form.

# In[12]:


top_five_authors = author_counts_sorted_dstream.transform  (lambda rdd:sc.parallelize(rdd.take(5)))
top_five_authors.pprint()


# ### Get authors with more than one tweet, or whose username starts with 'a'
# 
# Let's get a bit more fancy now - filtering the resulting list of authors to only show the ones who have tweeted more than once in our batch window, or -arbitrarily- whose screenname begins with `rm`..

# In[13]:


filtered_authors = author_counts.filter(lambda x:                                                x[1]>1                                                 or                                                 x[0].lower().startswith('rm'))


# We'll print this list of authors matching the criteria, sorted by the number of tweets. Note how the sort is being done inline to the calling of the `pprint` function. Assigning variables and then `pprint`ing them as I've done above is only done for clarity. It also makes sense if you're going to subsequently reuse the derived stream variable (such as with the `author_counts` in this code). 

# In[14]:


filtered_authors.transform  (lambda rdd:rdd  .sortBy(lambda x:-x[1]))  .pprint()


# ### List the most common words in the tweets
# 
# Every example has to have a version of wordcount, right? Here's an all-in-one with line continuations to make it clearer what's going on. It makes for tidier code, but it also makes it harder to debug...

# In[15]:


parsed.    flatMap(lambda tweet:tweet['text'].split(" "))    .countByValue()    .transform      (lambda rdd:rdd.sortBy(lambda x:-x[1]))    .pprint()


# ## Start the streaming context
# 
# Having defined the streaming context, now we're ready to actually start it! When you run this cell, the program will start, and you'll see the result of all the `pprint` functions above appear in the output to this cell below. If you're running it outside of Jupyter (via `spark-submit`) then you'll see the output on stdout.
# 
# _I've added a `timeout` to deliberately cancel the execution after three minutes. In practice, you would not set this :)_

# In[16]:


ssc.start()
ssc.awaitTermination(timeout=60)


# So there we have it, a very simple Spark Streaming application doing some basic processing against an inbound data stream from Kafka.

# ## Windowed Stream Processing

# Now let's have a look at how we can do windowed processing. This is where data is processed based on a 'window' which is a multiple of the batch duration that we worked with above. So instead of counting how many tweets there are every batch (say, 5 seconds), we could instead count how many there are per hour - an hour (/60 minutes/3600 seconds is the _window_ interval). We can perform this count potentially every time the batch runs; how frequently we do the count is known as the _slide_ interval.
# 
# _![](http://spark.apache.org/docs/latest/img/streaming-dstream-window.png)
# Image credit, and more details about window processing, [here](http://spark.apache.org/docs/latest/streaming-programming-guide.html#window-operations)._

# The first thing to do to enable windowed processing in Spark Streaming is to launch the Streaming Context with a [checkpoint directory](http://spark.apache.org/docs/latest/streaming-programming-guide.html#checkpointing) configured. This is used to store information between batches if necessary, and also to recover from failures. You need to rework your code into the pattern [shown here](http://spark.apache.org/docs/latest/streaming-programming-guide.html#how-to-configure-checkpointing). All the code to be executed by the streaming context goes in a function - which makes it less easy to present in a step-by-step form in a notebook as I have above. 

# ### Reset the Environment 
# 
# If you're running this code in the same session as above, first go to the Jupyter **Kernel** menu and select **Restart**.

# ### Prepare the environment
# 
# These are the same steps as above. 

# In[17]:


import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json


# ### Define the stream processing code

# In[18]:


def createContext():
    sc = SparkContext(appName="PythonSparkStreamingKafka_RM_02")
    sc.setLogLevel("WARN")
    ssc = StreamingContext(sc, 5)
    
    # Define Kafka Consumer
    kafkaStream = KafkaUtils.createStream(ssc, 'cdh57-01-node-01.moffatt.me:2181', 'spark-streaming2', {'twitter':1})
    
    ## --- Processing
    # Extract tweets
    parsed = kafkaStream.map(lambda v: json.loads(v[1]))
    
    # Count number of tweets in the batch
    count_this_batch = kafkaStream.count().map(lambda x:('Tweets this batch: %s' % x))
    
    # Count by windowed time period
    count_windowed = kafkaStream.countByWindow(60,5).map(lambda x:('Tweets total (One minute rolling count): %s' % x))

    # Get authors
    authors_dstream = parsed.map(lambda tweet: tweet['user']['screen_name'])
    
    # Count each value and number of occurences 
    count_values_this_batch = authors_dstream.countByValue()                                .transform(lambda rdd:rdd                                  .sortBy(lambda x:-x[1]))                              .map(lambda x:"Author counts this batch:\tValue %s\tCount %s" % (x[0],x[1]))

    # Count each value and number of occurences in the batch windowed
    count_values_windowed = authors_dstream.countByValueAndWindow(60,5)                                .transform(lambda rdd:rdd                                  .sortBy(lambda x:-x[1]))                            .map(lambda x:"Author counts (One minute rolling):\tValue %s\tCount %s" % (x[0],x[1]))

    # Write total tweet counts to stdout
    # Done with a union here instead of two separate pprint statements just to make it cleaner to display
    count_this_batch.union(count_windowed).pprint()

    # Write tweet author counts to stdout
    count_values_this_batch.pprint(5)
    count_values_windowed.pprint(5)
    
    return ssc


# ### Launch the stream processing
# 
# This uses local disk to store the checkpoint data. In a Production deployment this would be on resilient storage such as HDFS.
# 
# Note that, by design, if you restart this code using the same checkpoint folder, it will execute the *previous* code - so if you need to amend the code being executed, specify a different checkpoint folder.

# In[19]:


ssc = StreamingContext.getOrCreate('/tmp/checkpoint_v06',lambda: createContext())
ssc.start()
ssc.awaitTermination()


# You can see in the above output cell the full output from the job, but let's take some extracts and walk through them. 

# ### Total tweet counts

# First, the total tweet counts. In the first slide window, they're the same, since we only have one batch of data so far: 
# 
#     -------------------------------------------
#     Time: 2017-01-11 17:08:55
#     -------------------------------------------
#     Tweets this batch: 782
#     Tweets total (One minute rolling count): 782 
#     
# Five seconds later, we have 25 tweets in the current batch - giving us a total of 807 (782 + 25): 
# 
#     -------------------------------------------
#     Time: 2017-01-11 17:09:00
#     -------------------------------------------
#     Tweets this batch: 25
#     Tweets total (One minute rolling count): 807 
#     
# Fast forward just over a minute and we see that the windowed count for a minute is not just going up - in some cases it goes down - since our window is now not simply the full duration of the inbound data stream, but is shifting along and giving a total count for (now - 60 seconds)
# 
#     -------------------------------------------
#     Time: 2017-01-11 17:09:50
#     -------------------------------------------
#     Tweets this batch: 28
#     Tweets total (One minute rolling count): 1012
# 
#     -------------------------------------------
#     Time: 2017-01-11 17:09:55
#     -------------------------------------------
#     Tweets this batch: 24
#     Tweets total (One minute rolling count): 254
# 

# ### Count by Author
# 
# In the first batch, as with the total tweets, the batch tally is the same as the windowed one: 
#     
#     -------------------------------------------
#     Time: 2017-01-11 17:08:55
#     -------------------------------------------
#     Author counts this batch:	Value AnnaSabryan	Count 8
#     Author counts this batch:	Value KHALILSAFADO	Count 7
#     Author counts this batch:	Value socialvidpress	Count 6
#     Author counts this batch:	Value SabSad_	Count 5
#     Author counts this batch:	Value CooleeBravo	Count 5
#     ...
# 
#     -------------------------------------------
#     Time: 2017-01-11 17:08:55
#     -------------------------------------------
#     Author counts (One minute rolling):	Value AnnaSabryan	Count 8
#     Author counts (One minute rolling):	Value KHALILSAFADO	Count 7
#     Author counts (One minute rolling):	Value socialvidpress	Count 6
#     Author counts (One minute rolling):	Value SabSad_	Count 5
#     Author counts (One minute rolling):	Value CooleeBravo	Count 5    
#     
# But notice in subsequent batches the rolling totals are accumulating for each author. Here we can see `KHALILSAFADO` (with a previous rolling total of 7, as above) has another tweet in this batch, giving a rolling total of 8: 
# 
#     -------------------------------------------
#     Time: 2017-01-11 17:09:00
#     -------------------------------------------
#     Author counts this batch:	Value DawnExperience	Count 1
#     Author counts this batch:	Value KHALILSAFADO	Count 1
#     Author counts this batch:	Value Alchemister5	Count 1
#     Author counts this batch:	Value uused2callme	Count 1
#     Author counts this batch:	Value comfyjongin	Count 1
#     ...
# 
#     -------------------------------------------
#     Time: 2017-01-11 17:09:00
#     -------------------------------------------
#     Author counts (One minute rolling):	Value AnnaSabryan	Count 9
#     Author counts (One minute rolling):	Value KHALILSAFADO	Count 8
#     Author counts (One minute rolling):	Value socialvidpress	Count 6
#     Author counts (One minute rolling):	Value SabSad_	Count 5
#     Author counts (One minute rolling):	Value CooleeBravo	Count 5

# ## Summary
# 
# Processing unbounded data sets, or "stream processing", is a new way of looking at what has always been done as batch in the past. Whilst intra-day ETL and frequent batch executions have brought latencies down, they are still standalone executions with optional bespoke code in place to handle intra-batch accumulations. With Spark Streaming we have a framework that enables this processing to be done natively and with support as default for both within-batch and across-batch (windowing). 
# 
# Here I used Spark Streaming because of its native support for Python, a language that I am familiar with and is (in my view) more accessible to non-coders than Java or Scala. Jupyter Notebooks are a fantastic environment in which to prototype code, and for a local environment providing both Jupyter and Spark it all you can't beat the Docker image [all-spark-notebook](https://github.com/jupyter/docker-stacks/tree/master/all-spark-notebook). 
# 
# There are other stream processing frameworks and languages out there, including Apache Flink, Kafka Streams, and Apache Beam, to name but three. Apache Storm and Apache Samza are also relevant, but whilst were early to the party seem to crop up less frequently in stream processing discussions and literature nowadays. 

# In the next blog we'll see how to extend this Spark Stremaing further with processing that includes: 
# 
# * Matching tweet contents to predefined list of filter terms, and filtering out retweets
# * Including only tweets that include URLs, and comparing those URLs to a whitelist of domains
# * Sending tweets matching a given condition to a Kafka topic
# * Keeping a tally of tweet counts per batch and over a longer period of time, as well as counts for terms matched within the tweets
