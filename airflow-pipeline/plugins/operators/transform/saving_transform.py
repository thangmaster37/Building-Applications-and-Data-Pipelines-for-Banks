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

class SavingDepositTransform:
    """
        Class này thực hiện việc chuyển đổi trên bộ dữ liệu saving deposit
        1. Chuyển đổi định dạng chuỗi thời gian về cùng một dạng duy nhất
        2. Loại bỏ các khoảng trắng dư thừa
        3. Đưa dữ liệu dạng string về chữ thường và không dấu
        4. Loại bỏ các bản ghi trùng lặp và sắp xếp dữ liệu
        5. Loại bỏ các bản ghi mà tại đó số tiền gửi tiết kiệm < 0
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
        saving_df = self._spark.createDataFrame(pd_read_s3_multiple_parquets(self._s3_client, f'saving/{getYesterday()}.parquet', self._input_bucket_name))

        # Loại bỏ record trùng lặp
        saving_df = saving_df.dropDuplicates()
        # Sắp xếp các record theo thứ tự tăng dần của trường dữ liệu userID
        saving_df = saving_df.orderBy(F.col('savingID'))
        
        return saving_df
    
    # Thực hiện một số tổng hợp để lọc dữ liệu
    def data_aggregation(self):
        saving_df = self.removeduplicate_orderby_transform()
        saving_filter = saving_df.filter(F.col('money') >= 0)
        return saving_filter

    # Chuyển đổi định dạng của các trường dữ liệu
    def format_transform_saving(self):
        saving_df = self.data_aggregation()

        # Loại bỏ các khoảng trắng dư thừa trong trường dữ liệu accountPayID
        saving_df = saving_df.withColumn('accountPayID', removeExtraSpaces(F.col('accountPayID')))

        # Chuyển trường dữ liệu status về chữ thường
        saving_df = saving_df.withColumn('status', transformLowerCase(F.col('status')))

        # Chuyển trường dữ liệu savingType về chữ thường và không dấu
        saving_df = saving_df.withColumn('savingType', transformUnideCode(transformLowerCase(F.col('savingType'))))

        # Chuyển 2 trường dữ liệu: createDate và expire về cùng một định dạng thống nhất
        saving_df = saving_df.withColumn('createDate', transformDateTime(F.col('createDate')))
        saving_df = saving_df.withColumn('expire', transformDateTime(F.col('expire')))

        # Chuyển period về chữ thường
        saving_df = saving_df.withColumn('period', transformLowerCase(F.col('period')))
        
        return saving_df

    # Hàm thực thi
    def execute(self):
        df = self.format_transform_saving().toPandas()
        out_buffer = io.BytesIO()
        df.to_parquet(out_buffer)
        self._s3_client.put_object(Body=out_buffer.getvalue(), Bucket=self._output_bucket_name, Key=f'saving/{getYesterday()}.parquet')


if __name__ == "__main__":
    savingTransform = SavingDepositTransform()
    savingTransform.execute()