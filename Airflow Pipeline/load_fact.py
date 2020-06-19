from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 redshift_conn_id = "",
                 load_fact_table_sql = "",
                 table = "",
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.redshift_conn_id = redshift_conn_id,
        self.load_fact_table_sql = load_fact_table_sql,
        self.table = table

    def execute(self, context):
        
        postgres_hook = PostgresHook(self.redshift_conn_id)
        
        self.log.info('Delete existing data in {} table if exists'.format(self.table))
        formatted_sql = "DELETE FROM {}".format(self.table)
        postgres_hook.run(formatted_sql)
        
        self.log.info('Inserting the log data into the Fact table: {}'.format(self.table))
        formatted_sql = "INSERT INTO {} {}".format(self.table, self.load_fact_table_sql)
        postgres_hook.run(formatted_sql)
        
        pass
