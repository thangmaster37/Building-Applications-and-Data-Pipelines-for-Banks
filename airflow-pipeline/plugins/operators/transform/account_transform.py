from airflow.utils.context import Context
from helpers.format_data import removeExtraSpaces, transformDateTime, transformLowerCase, transformUnideCode
from airflow.models import BaseOperator
from pyspark.sql import SparkSession
from pyspark.sql.functions import split
import pyspark.sql.functions as F
from helpers.getYesterday import getYesterday
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

class AccountTransform:
    """
        Class này thực hiện việc chuyển đổi trên bộ dữ liệu account
        1. Chuyển đổi định dạng chuỗi thời gian về cùng một dạng duy nhất
        2. Loại bỏ các khoảng trắng dư thừa
        3. Đưa dữ liệu dạng string về chữ thường và không dấu (unidecode)
        4. Đưa trường dữ liệu gender về 2 kiểu: Male và Female
        5. Loại bỏ các bản ghi trùng lặp và sắp xếp dữ liệu
        6. Tách trường dữ liệu placeOfPermanent thành 3 cột: "ward", "district", "city"
        7. Thêm một trường dữ liệu profileID
        8. Lưu dữ liệu vào bucket: curated-banking dưới dạng file parquet
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
        account_df = self._spark.createDataFrame(pd_read_s3_multiple_parquets(self._s3_client, f'account/{getYesterday()}.parquet', self._input_bucket_name))

        # Loại bỏ record trùng lặp
        account_df = account_df.dropDuplicates()
        # Sắp xếp các record theo thứ tự tăng dần của trường dữ liệu userID
        account_df = account_df.orderBy(F.col('userID'))
        
        return account_df
    
    # Tách các giá trị của trường dữ liệu placeOfPermanent thành Xã / Huyện / Thành Phố
    def data_split(self):
        account_df = self.removeduplicate_orderby_transform()
        # Tách trường dữ liệu "placeOfPermanent" thành 3 cột "ward", "district", "city"
        account_df = account_df.withColumn("ward", split(account_df["placeOfPermanent"], " - ").getItem(0)) \
                               .withColumn("district", split(account_df["placeOfPermanent"], " - ").getItem(1)) \
                               .withColumn("city", split(account_df["placeOfPermanent"], " - ").getItem(2))
        
        # Loại bỏ các khoảng trắng dư thừa trong 3 trường dữ liệu mới vừa tạo được
        account_df = account_df.withColumn('ward', removeExtraSpaces(F.col('ward')))
        account_df = account_df.withColumn('district', removeExtraSpaces(F.col('district')))
        account_df = account_df.withColumn('city', removeExtraSpaces(F.col('city')))

        return account_df
        
    # Chuyển đổi định dạng của các trường dữ liệu
    def format_transform_account(self):
        account_df = self.data_split()
        
        # Áp dụng các biểu thức chuyển đổi lên từng cột
        # username và password loại bỏ khoảng trắng dư thừa
        account_df = account_df.withColumn('username', removeExtraSpaces(F.col('username')))
        account_df = account_df.withColumn('password', removeExtraSpaces(F.col('password')))

        # firstname, middlename và lastname sẽ loại bỏ khoảng trắng thừa, chuyển về chữ thường và chữ không dấu
        account_df = account_df.withColumn('firstname', transformUnideCode(transformLowerCase(removeExtraSpaces(F.col('firstname')))))
        account_df = account_df.withColumn('middlename', transformUnideCode(transformLowerCase(removeExtraSpaces(F.col('middlename')))))
        account_df = account_df.withColumn('lastname', transformUnideCode(transformLowerCase(removeExtraSpaces(F.col('lastname')))))

        # banktype sẽ loại bỏ khoảng trắng và đưa về chữ thường
        account_df = account_df.withColumn('banktype', transformLowerCase(F.col('banktype')))

        # accountPayID sẽ loại bỏ khoảng trắng
        account_df = account_df.withColumn('accountPayID', removeExtraSpaces(F.col('accountPayID')))

        # gender sẽ loại bỏ khoảng trắng dư thừa và đưa về chữ thường và chữ tiếng anh
        account_df = account_df.withColumn('gender', transformLowerCase(F.col('gender')))

        # ward, district, city loại bỏ khoảng trắng dư thừa và chuyển về chữ thường và chữ không dấu
        account_df = account_df.withColumn('ward', transformUnideCode(transformLowerCase(removeExtraSpaces(F.col('ward')))))
        account_df = account_df.withColumn('district', transformUnideCode(transformLowerCase(removeExtraSpaces(F.col('district')))))
        account_df = account_df.withColumn('city', transformUnideCode(transformLowerCase(removeExtraSpaces(F.col('city')))))

        # citizenID loại bỏ khoảng trắng dư thừa
        account_df = account_df.withColumn('citizenID', removeExtraSpaces(F.col('citizenID')))

        # createDate chuyển về định dạng thời gian phù hợp
        account_df = account_df.withColumn('createDate', transformDateTime(F.col('createDate')))

        return account_df

    # Thực hiện thêm một cột là profileID
    def add_column(self):
        account_df = self.format_transform_account()
        account_df = account_df.withColumn('profileID', F.col('userID'))
        return account_df
    
    # Hàm thực thi
    def execute(self):
        df = self.add_column().toPandas()
        out_buffer = io.BytesIO()
        df.to_parquet(out_buffer)
        self._s3_client.put_object(Body=out_buffer.getvalue(), Bucket=self._output_bucket_name, Key=f'account/{getYesterday()}.parquet')


if __name__ == "__main__":
    accountTransform = AccountTransform()   
    accountTransform.execute()             
    




    
    

    
    