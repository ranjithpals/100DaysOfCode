from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 redshift_conn_id = "",
                 sql_expected = "",
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.conn_id = redshift_conn_id
        self.sql_expected = sql_expected

    def execute(self, context):
        
        postgres_hook = PostgresHook(self.conn_id)
        
        self.log.info('Executing SQL Checks')
        
        for check in self.sql_expected:
            # Iterate through all the checks assigned in the DAG
            records = postgres_hook.get_records(check.get('query'))[0]
            if records[0] != check.get('result'):
                error_dsc = 'Data Quality check failed in the table: %s' % check.get('table')
                raise AirflowException(error_dsc)

            