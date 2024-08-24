import configparser
from airflow.utils.context import Context
import psycopg2
from pathlib import Path
from warehouse_queries import create_warehouse_tables
from warehouse_load import copy_warehouse_tables
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[1]}/warehouse_config.cfg"))

class BankingWarehouseDriver(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs):
        self._conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
        self._cur = self._conn.cursor()
        super(BankingWarehouseDriver, self).__init__(*args, **kwargs)

    def setup_warehouse_tables(self):
        self.execute_query(create_warehouse_tables)

    def setup_copy_warehouse_tables(self):
        self.execute_query(copy_warehouse_tables)

    def execute_query(self, query_list):
        for query in query_list:
            print(query)
            self._cur.execute(query)
            self._conn.commit()

    def execute(self, context):
        self.setup_warehouse_tables()
        self.setup_copy_warehouse_tables()