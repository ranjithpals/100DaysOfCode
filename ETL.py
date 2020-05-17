import configparser
import os

#import logging
#import boto3
#from botocore.exceptions import ClientError

import pandas as pd

from pyspark.sql import SparkSession
from pyspark import SparkContext

from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format

from pyspark.sql.types import StringType, IntegerType, TimestampType, DateType

from pyspark.sql.functions import desc
from pyspark.sql.functions import asc
from pyspark.sql.functions import sum as Fsum
from pyspark.sql import functions as f

config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']= config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']= config['AWS']['AWS_SECRET_ACCESS_KEY']

KEY= config['AWS']['AWS_ACCESS_KEY_ID']
SECRET= config['AWS']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    # get filepath to song data file
    song_data = input_data + "song_data/A/A/*/*.json"

    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df.select(["song_id", "title", "artist_id", "year", "duration"]).dropDuplicates()
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.mode('overwrite').parquet('Output/songs_table')

    # extract columns to create artists table
    artists_table = df.select(["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]).dropDuplicates()
    
    # write artists table to parquet files
    artists_table.write.mode('overwrite').parquet('Output/artists_table')


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    log_data = input_data + "log_data/2018/*/*.json"

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong')

    # extract columns for users table    
    users_table = df.select(['userId', 'firstName', 'lastName', 'gender', 'level']).dropDuplicates()
    
    # write users table to parquet files
    users_table.write.mode('overwrite').parquet('Output/users_table')

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: datetime.fromtimestamp(x/1000.0),TimestampType())
    df = df.withColumn("timestamp", get_timestamp(df.ts))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: datetime.fromtimestamp(x/1000.0), DateType())
    df = df.withColumn("datetime", get_datetime(df.ts))
    
    # extract columns to create time table
    time_table = df.select(col('ts').alias('start_time'),
                        f.hour(df.timestamp).alias('hour'),
                        f.dayofweek(df.datetime).alias('day'),
                        f.weekofyear(df.datetime).alias('week'),
                        f.month(df.datetime).alias('month'), 
                        f.year(df.datetime).alias('year'),
                        date_format(df.datetime, 'E').alias('weekday')).dropDuplicates()
    
    # write time table to parquet files partitioned by year and month
    time_table.write.mode('overwrite').parquet('Output/time_table')

    # read in song data to use for songplays table
    song_data = input_data + "song_data/A/A/*/*.json"
    song_df = spark.read.json(song_data)

    # extract columns from joined song and log datasets to create songplays table 
    songplays = df.join(song_df,
            (df.song == song_df.title) & (df.artist == song_df.artist_name) & (df.length == song_df.duration), how='left')
    
    songplays_table = songplays.select(df.ts.alias('start_time'), f.year(df.datetime).alias('year'), df.userId.alias('user_id'), df.level, song_df.song_id,
                        song_df.artist_id, df.sessionId.alias('session_id'), df.location, 
                        df.userAgent.alias('user_agent'))

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.mode('overwrite').partitionBy('artist_id', 'song_id').parquet('Output/songplays_table')


def main():
    spark = create_spark_session()
    input_data = config['S3']['INPUT_DATA']
    output_data = "Output/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
