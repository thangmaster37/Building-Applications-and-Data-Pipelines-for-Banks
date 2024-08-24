from airflow.models import BaseOperator
from airflow.utils.context import Context
from airflow.utils.decorators import apply_defaults
import configparser
from pathlib import Path
import psycopg2

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[1]}/warehouse_config.cfg"))

class AnalyticsOperator(BaseOperator):

    @apply_defaults
    def __init__(self, queries, *args, **kwargs):
        self._conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
        self._cursor = self._conn.cursor()

        self._queries = queries

        super(AnalyticsOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        for query in self._queries:
            try: 
                print("Running Analytics query :  {}".format(query))
                self._cursor.execute(query)
                print("Query ran successfully!!")
            except Exception as e:
                raise ValueError(e)