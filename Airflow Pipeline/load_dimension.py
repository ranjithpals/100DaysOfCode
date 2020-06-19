from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 redshift_conn_id = "",
                 dimension_table_sql = "",
                 table = "",
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.redshift_conn_id = redshift_conn_id,
        self.dimension_table_sql = dimension_table_sql,
        self.table = table,

    def execute(self, context):
        # self.log.info('LoadDimensionOperator not implemented yet')
        
        postgres_hook = PostgresHook(self.redshift_conn_id)
        
        self.log.info('Inserting the log data into the dimension table: {}'.format(self.table))
        formatted_sql = "INSERT INTO SONGS {}".format(self.dimension_table_sql)
        postgres_hook.run(formatted_sql)
        
        pass
