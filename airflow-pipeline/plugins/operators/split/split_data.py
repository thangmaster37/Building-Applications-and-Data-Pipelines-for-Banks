from airflow.utils.context import Context
from helpers.getYesterday import getYesterday
from pyspark.sql import SparkSession
from botocore.exceptions import ClientError
import pyspark.sql.functions as F
from helpers.read_s3_parquet import pd_read_s3_parquet
from query import query_get_accountinfo, query_get_profileuser, query_get_accountpayment
from query import query_get_loan, query_get_saving_deposit, query_get_moneytransaction
import boto3
import os
import sys
from pathlib import Path
import configparser
from io import StringIO

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[2]}/s3_config.cfg"))

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

class SplitData:
    """
        Clas này thực hiện việc tách các bộ dữ liệu thành các bảng dựa trên database đã thiết kế
        1. Với bộ dữ liệu account tách thành 3 table: profileuser, accountinfo, accountpayment
        2. Với bộ dữ liệu loan sẽ thêm một trường dữ liệu 'bad' với các giá trị đều là giá trị null
        3. Với bộ dữ liệu saving deposit giữ nguyên
        4. Với bộ dữ liệu transaction giữ nguyên
        5. Các bộ dữ liệu này sẽ thực hiện thêm một số chuyển đổi cơ bản
        6. Lưu các file và bucker datasplit-banking theo định dạng CSV
    """

    def __init__(self):
        self._spark = SparkSession.builder.config('spark.master', 'local') \
                                          .config('spark.app.name', 'bank-etl') \
                                          .getOrCreate()
        self._input_bucket_name = config.get('BUCKET', 'CURATED_DATA_ZONE')
        self._output_bucket_name = config.get('BUCKET', 'SPLIT_DATA_ZONE')
        self._s3_client = boto3.client('s3',
                                    aws_access_key_id=config.get('AWS_S3', 'AWS_ACCESS_KEY_ID'),
                                    aws_secret_access_key=config.get('AWS_S3', 'AWS_SECRET_ACCESS_KEY'),
                                    region_name='us-east-1'
                                )
        
    # Đọc dữ liệu từ aws s3 và chuyển đổi thành dataframe
    def read_data(self, key):
        df = self._spark.createDataFrame(pd_read_s3_parquet(self._s3_client, f'{key}/{getYesterday()}.parquet', self._input_bucket_name))
        return df
    
    # Đẩy dữ liệu lên aws s3 sau khi đã tách thành các bảng theo định dạng CSV
    def upload_data(self, df, key):
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        response = self._s3_client.put_object(Bucket=self._output_bucket_name, Key=f'{key}/{getYesterday()}.csv', Body=csv_buffer.getvalue())
        return response
        
    # Tải dữ liệu lên s3 sau khi tách
    def account_split(self, key):
        try:
            self.read_data(key).createOrReplaceTempView('account_data')
            accountinfo = self._spark.sql(query_get_accountinfo('account_data')).toPandas()
            profileuser = self._spark.sql(query_get_profileuser('account_data')).toPandas()
            accountpayment = self._spark.sql(query_get_accountpayment('account_data')).toPandas()

            self.upload_data(accountinfo, 'accountinfo')
            self.upload_data(profileuser, 'profileuser')
            self.upload_data(accountpayment, 'accountpayment')
        except ClientError as e:
            print(f"An error occurred: {e}")

    # Tải dữ liệu lên s3
    def loan_split(self, key):
        try:
            self.read_data(key).createOrReplaceTempView('loan_data')
            loan = self._spark.sql(query_get_loan('loan_data'))
            loan = loan.withColumn('status', F.lit(None))
            loan = loan.withColumn('bad', F.lit(None))
            loan = loan.withColumn('paymentDate', F.lit(None))
            loan = loan.toPandas()
            self.upload_data(loan, 'loan')
        except ClientError as e:
            print(f"An error occurred: {e}")

    # Tải dữ liệu lên aws s3
    def saving_split(self, key):
        try:
            self.read_data(key).createOrReplaceTempView('saving_data')
            saving = self._spark.sql(query_get_saving_deposit('saving_data')).toPandas()

            self.upload_data(saving, 'savingdeposit')
        except ClientError as e:
            print(f"An error occurred: {e}")

    # Tải dữ liệu lên aws s3
    def transaction_split(self, key):
        try:
            self.read_data(key).createOrReplaceTempView('transaction_data')
            transaction = self._spark.sql(query_get_moneytransaction('transaction_data')).toPandas()

            self.upload_data(transaction, 'moneytransaction')
        except ClientError as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    splitData = SplitData()
    splitData.account_split('account')
    splitData.loan_split('loan')
    splitData.saving_split('saving')
    splitData.transaction_split('transaction')





        
