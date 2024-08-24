import os
import boto3
from airflow.exceptions import AirflowSkipException
import configparser
from pathlib import Path
from datetime import datetime, timedelta

# Setting configurations. Look config.cfg for more details
config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[1]}/s3_config.cfg"))


# Setup configs
aws_key = config.get('AWS_S3', 'AWS_ACCESS_KEY_ID')
aws_secret = config.get('AWS_S3', 'AWS_SECRET_ACCESS_KEY')
region = config.get('AWS_S3', 'REGION_NAME')


s3_client = boto3.client('s3', aws_access_key_id=aws_key, 
                         aws_secret_access_key=aws_secret,
                         region_name=region)


# Kiêm tra sự tồn tại của một bucket trong aws s3
def checkExistBucket(bucket_name):
    # Lấy danh sách các bucket
    response = s3_client.list_buckets()

    # In ra tên của từng bucket
    for bucket in response['Buckets']:
        if bucket['Name'] == bucket_name:
            return True
    return False


# Kiểm tra sự tồn tại của một thư mục trong bucket
def checkExistFolderInBucket(bucket_name, folder_name):
    # Lấy danh sách các "thư mục" trong bucket
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Delimiter='/'
    )

    # Kiểm tra xem phản hồi có chứa các "thư mục" hay không
    if 'CommonPrefixes' in response:
        folders = response['CommonPrefixes']
        for folder in folders:
            name_folder = folder['Prefix']
            if folder_name == name_folder[:-1]:
                return True
    return False


# Tạo một bucket trong aws s3
def create_bucket_name(bucket_name):
    if checkExistBucket(bucket_name):
        # Nếu bucket tồn tại thì ném ra một lỗi khi Airflow chạy sẽ bị skipped
        raise AirflowSkipException
    else:
        # Tạo một bucket 
        response = s3_client.create_bucket(Bucket = bucket_name)
        # Kiểm tra xem bucket đã được tạo thành công hay không
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"Tạo bucket {bucket_name} thành công.")
        else:
            print(f"Không thể tạo bucket {bucket_name}.")


# Tạo thư mục trong bucket
def create_folder(bucket_name, folder_name):
    if checkExistFolderInBucket(bucket_name, folder_name):
        # Nếu bucket tồn tại thư mục thì ném ra một lỗi khi Airflow chạy sẽ bị skipped
        raise AirflowSkipException
    else:
        # Tạo một thư mục trong bucket
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=folder_name + '/'
        )

        # Kiểm tra xem thư mục đã được tạo thành công hay không
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"Thư mục đã được tạo thành công trong bucket.")
        else:
            print("Không thể tạo thư mục.")


# Tải các file parquet lên aws s3
def upload_parquet_to_s3(local_directory, bucket_name, folder_direction):
    for file in os.listdir(local_directory):
        print(file)
        local_path = os.path.join(local_directory, file)
        s3_key = os.path.join(folder_direction, file)
        response = s3_client.upload_file(local_path, bucket_name, s3_key)
    return {"message": "Upload all file successfully!"}
            








