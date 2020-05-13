from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from operator import add
import re

# filter for at least rating 5;
# group by userid count 5 star ratings per user
# join with users table for firstname and last name
def userratinganalysis(spark):
    comments = spark.read.csv("s3://data3404-nhas9102-a2/comments.csv", inferSchema =True, header=True)\
                         .select('to_user_id', 'rating') # DataFrame 

    comments = comments.filter(comments.rating >= 5)
    comments = comments.drop('rating') # -> 'to_user_id' -> [.., ..., ...]
    comment_rows = comments.rdd.map(lambda x: x[0]) # -> [ id1, id2, id3, ...] 
    counts = comment_rows.map(lambda x: (x, 1)) \ # -> [ (id1, 1), (id2, 1), (id3, 1), (id2, 1),...]
                         .reduceByKey(add) # -> [ (id1, X), (id2, Y), (id3, Z),...]
    counts_sorted = counts.sortBy(lambda x: x[1], False)
    output = counts_sorted.collect()

    for (user, count) in output:
        print("%s: %i" % (user, count))


if __name__ == "__main__":

    spark = SparkSession\
            .builder.appName('UserRatingAnalysis')\
            .getOrCreate()

    userratinganalysis(spark)
    spark.stop()
    # BLAH # FOO