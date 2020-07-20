from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)

from helpers import SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'ranjith',
    'start_date': datetime(2018, 11, 1),
    #'end_date'  : datetime(2018, 11, 30)
    'email': ['learngvrk@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('data_pipeline_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='@once',
          #catchup=False,
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id = "redshift",
    aws_credentials_id = "aws_credentials",
    table = "staging_events",
    s3_bucket = "udacity-dend",
    s3_key = "log_data/{execution_date.year}/{execution_date.month}",
    json_path = "s3://udacity-dend/log_json_path.json"
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id = "redshift",
    aws_credentials_id = "aws_credentials",
    table = "staging_songs",
    s3_bucket = "udacity-dend",
    s3_key = "song_data",
    json_path = "auto"
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    load_fact_table_sql = SqlQueries.songplay_table_insert,
    table = 'songplays',
)


load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    load_dimension_table_sql = SqlQueries.user_table_insert,
    table = 'users',
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    load_dimension_table_sql = SqlQueries.song_table_insert,
    table = 'songs',
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    load_dimension_table_sql = SqlQueries.artist_table_insert,
    table = 'artists',
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    load_dimension_table_sql = SqlQueries.time_table_insert,
    table = 'time',
)

perform_data_quality_check = DataQualityOperator(
    task_id='Data_quality_check',
    dag=dag,
    redshift_conn_id = 'redshift',
    sql_expected = [{'query':'SELECT COUNT(*) FROM SONGPLAYS WHERE PLAYID IS NULL', 'result':0, 'table':'Songplays'},
                    {'query':'SELECT COUNT(*) FROM USERS WHERE USERID IS NULL', 'result':0, 'table':'Users'}],
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> stage_events_to_redshift >> load_songplays_table
start_operator >> stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table >> perform_data_quality_check
load_songplays_table >> load_song_dimension_table >> perform_data_quality_check
load_songplays_table >> load_artist_dimension_table >> perform_data_quality_check
load_songplays_table >> load_time_dimension_table >> perform_data_quality_check

perform_data_quality_check >> end_operator