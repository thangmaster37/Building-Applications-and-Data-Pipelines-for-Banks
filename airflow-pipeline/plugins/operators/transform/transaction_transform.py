from airflow.utils.context import Context
from helpers.format_data import removeExtraSpaces, transformDateTime, transformLowerCase, transformUnideCode
from airflow.models import BaseOperator
from pyspark.sql import SparkSession
from helpers.getYesterday import getYesterday
import pyspark.sql.functions as F
from airflow.utils.decorators import apply_defaults
from helpers.read_s3_parquet import pd_read_s3_multiple_parquets
from pathlib import Path
import configparser
import boto3
import sys
import io
import os
import pandas as pd

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[2]}/s3_config.cfg"))

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

class TransactionTransform:
    """
        Class này thực hiện việc chuyển đổi trên bộ dữ liệu transaction
        1. Chuyển đổi định dạng chuỗi thời gian về cùng một dạng duy nhất
        2. Loại bỏ các khoảng trắng dư thừa
        3. Đưa dữ liệu dạng string về chữ thường và không dấu
        4. Loại bỏ các bản ghi trùng lặp và sắp xếp dữ liệu
        5. Loại bỏ các bản ghi mà tại đó số tiền giao dịch < 0 và số dư tài khoản < 0
        5. Lưu dữ liệu vào bucket: curated-banking dưới dạng file parquet
    """


    def __init__(self):
        self._spark = SparkSession.builder.config('spark.master', 'local') \
                                          .config('spark.app.name', 'bank-etl') \
                                          .getOrCreate()
        self._input_bucket_name = config.get('BUCKET', 'RAW_DATA_ZONE')
        self._output_bucket_name = config.get('BUCKET', 'CURATED_DATA_ZONE')
        self._s3_client = boto3.client('s3',
                                    aws_access_key_id=config.get('AWS_S3', 'AWS_ACCESS_KEY_ID'),
                                    aws_secret_access_key=config.get('AWS_S3', 'AWS_SECRET_ACCESS_KEY'),
                                    region_name='us-east-1'
                                )
        
    # Thực hiện loại bỏ trùng lặp và sắp xếp dữ liệu
    def removeduplicate_orderby_transform(self):
        transaction_df = self._spark.createDataFrame(pd_read_s3_multiple_parquets(self._s3_client, f'transaction/{getYesterday()}.parquet', self._input_bucket_name))

        # Loại bỏ record trùng lặp
        transaction_df = transaction_df.dropDuplicates()
        # Sắp xếp các record theo thứ tự tăng dần của trường dữ liệu userID
        transaction_df = transaction_df.orderBy(F.col('transID'))
        
        return transaction_df
    
    # Thực hiện một số tổng hợp để lọc dữ liệu
    def data_aggregation(self):
        transaction_df = self.removeduplicate_orderby_transform()
        transaction_filter = transaction_df.filter((F.col('amount') >= 0) & (F.col('surplus') >= 0))
        return transaction_filter
        
    # Chuyển đổi định dạng của các trường dữ liệu
    def format_transform_transaction(self):
        tracsaction_df = self.data_aggregation()

        # Chuyển về chữ thường trường dữ liệu toBankType
        tracsaction_df = tracsaction_df.withColumn('toBankType', transformLowerCase(F.col('toBankType')))

        # Loại bỏ các khoảng trắng dư thừa trong trường dữ liệu fromBankAccount, toBankAccount
        tracsaction_df = tracsaction_df.withColumn('fromBankAccount', removeExtraSpaces(F.col('fromBankAccount')))
        tracsaction_df = tracsaction_df.withColumn('toBankAccount', removeExtraSpaces(F.col('toBankAccount')))
        
        # Chuyển về chữ thường trường dữ liệu method và loại bỏ khoảng trắng
        tracsaction_df = tracsaction_df.withColumn('method', transformLowerCase(removeExtraSpaces(F.col('method'))))

        # Chuyển trường dữ liệu status về chữ thường
        tracsaction_df = tracsaction_df.withColumn('status', transformLowerCase(F.col('status')))

        # Chuyển 2 trường dữ liệu savingType, content về chữ thường và không dấu 
        tracsaction_df = tracsaction_df.withColumn('savingType', transformUnideCode(transformLowerCase(F.col('savingType'))))
        tracsaction_df = tracsaction_df.withColumn('content', transformUnideCode(transformLowerCase(removeExtraSpaces(F.col('content')))))

        # Chuyển 2 trường dữ liệu: createDate và expire về cùng một định dạng thống nhất
        tracsaction_df = tracsaction_df.withColumn('createDate', transformDateTime(F.col('createDate')))
        
        return tracsaction_df
        
    # Hàm thực thi
    def execute(self):
        df = self.format_transform_transaction().toPandas()
        out_buffer = io.BytesIO()
        df.to_parquet(out_buffer)
        self._s3_client.put_object(Body=out_buffer.getvalue(), Bucket=self._output_bucket_name, Key=f'transaction/{getYesterday()}.parquet')


if __name__ == "__main__":
    transactionTransform = TransactionTransform()
    transactionTransform.execute()

    
    


    
