from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 redshift_conn_id="",
                 aws_credentials_id="",
                 table="",
                 s3_bucket="",
                 s3_key="",
                 delimiter=",",
                 ignore_headers=1,
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.redshift_conn_id = redshift_conn_id,
        self.aws_credentials_id = aws_credentials_id,
        self.table = table,
        self.s3_bucket = s3_bucket,
        self.s3_key = s3_key,
        self.delimiter = delimiter,
        self.ignore_headers = ignore_headers

    def execute(self, context):
        # self.log.info('StageToRedshiftOperator not implemented yet')
        aws_hook = AwsHook(self.aws_credentials_id)
        postgres_hook = PostgresHook(self.redshift_conn_id)
        credentials = aws_hook.get_credentials()
        
        self.log.info("Deleting existing data if available in Redshift tables")
        postgres_hook.run("DELETE FROM {}".format(self.table))
        
        
        self.log.info("Copying data from S3 bucket to Redshift")
        rendered_key = self.s3_key.format(**context)
        s3_path = "s3://{}/{}".format(self.s3_bucket, rendered_key)
        formatted_sql = "COPY {} FROM '{}' \
                          ACCESS_KEY_ID '{{}}' \
                          SECRET_ACCESS_KEY '{{}}' \
                          DELIMITER '{}' \
                          IGNOREHEADER {}".format(self.table, s3_path, credentials.access_key, credentials.secret_key, self.delimiter, self.ignore_headers)
        
        postgres_hook.run(formatted_sql)
        
        pass
        
        



