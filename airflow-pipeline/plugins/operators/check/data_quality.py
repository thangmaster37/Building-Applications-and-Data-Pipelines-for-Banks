from airflow.models import BaseOperator
from airflow.utils.context import Context
from airflow.utils.decorators import apply_defaults
import configparser
from pathlib import Path
import psycopg2

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[1]}/warehouse_config.cfg"))

class DataQualityOperator(BaseOperator):

    @apply_defaults
    def __init__(self, tables, *args, **kwargs):
        self._conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
        self._cursor = self._conn.cursor()

        self._tables = tables

        super(DataQualityOperator, self).__init__(*args, **kwargs)

    def check_table(self, table):

        print("Starting data quality validation on table : {}".format(table))
        self._cursor.execute("select count(*) from {};".format(table))
        records = self._cursor.fetchall()

        if len(records) < 1 or len(records[0]) < 1:
            print("Data Quality validation failed for table : {}.".format(table))
            raise ValueError("Data Quality validation failed for table : {}".format(table))
        print("Data Quality Validation Passed on table : {}!!!".format(table))

    def execute(self, context):
        for table in self._tables:
            self.check_table(table)



    