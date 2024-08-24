from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from helpers.create_bucket import create_bucket_name, create_folder, upload_parquet_to_s3
from scripts.function import getYesterday
from airflow.operators.bash import BashOperator
from operators.load.warehouse_driver import BankingWarehouseDriver
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from operators.monitor_cdc_scd.monitor import MonitorOperator
from operators.check.data_quality import DataQualityOperator
from operators.check.data_analytics import AnalyticsOperator
from operators.check.query_test import AnalyticsQueries
import os, sys


default_args = {
    'owner': 'banking', # Tên chủ sỡ hữu
    'depends_on_past': True, # True để xác định rằng các task hiện tại sẽ phụ thuộc vào các tast trước đó 
    'start_date' : datetime(2024, 8, 6, 0, 0, 0, 0), # Ngày bắt đầu thực thi luồng data
    # 'end_date' : datetime(2024, 8, 15, 0, 0, 0, 0),
    'email_on_failure': False, # False để xác định không có email thông báo khi thực thi bị lỗi
    'email_on_retry': False, # False xác định không có email thông báo được gửi khi task được thực hiện lại
    'retries': 1, # Số lần thử lại trước khi đánh dấu task thất bại
    'retry_delay': timedelta(minutes=0), # Khoảng thời gian giữa những lần thử lại task
    'trigger_rule': 'none_failed', # Xác định rằng task hiện tại chỉ được thực hiện khi các task trước đó không bị lỗi
    'catchup': False # Các task sẽ không được chạy lại khi bị lỡ
}


dag_name = 'banking_pipeline'
dag = DAG(dag_name,
          default_args=default_args,
          description='This data stream is built to push data and datawarehouse for data analysis',
          schedule_interval='5 0 * * *', # Khoảng thời gian bắt đầu thực thi
          max_active_runs = 10 # Số lượng chạy DAG tối đa trong cùng một lúc
        )

# Task thông báo bắt đầu thực thi luồng data
start_operator = EmptyOperator(task_id = 'Begin_execution',  dag = dag)

# Tạo bucket trên AWS S3
create_bucket = PythonOperator(task_id = 'Create_Bucket', 
                               python_callable = create_bucket_name,
                               op_kwargs = {
                                   'bucket_name': 'datalake-banking'
                               },
                               dag = dag)

# Tạo folder chứa các dữ liệu về account
create_floder_account = PythonOperator(task_id = "Create_Folder_Account",
                                       python_callable=create_folder,
                                       op_kwargs={
                                           'bucket_name': 'datalake-banking',
                                           'folder_name': 'account'
                                       },
                                       dag = dag)

# Tạo folder chứa các dữ liệu về khoản vay
create_floder_loan = PythonOperator(task_id = "Create_Folder_Loan",
                                    python_callable=create_folder,
                                    op_kwargs={
                                        'bucket_name': 'datalake-banking',
                                        'folder_name': 'loan'
                                    },

                                    dag = dag)

# Tạo folder chứa các dữ liệu về gửi tiết kiệm
create_floder_saving = PythonOperator(task_id = "Create_Folder_Saving",
                                      python_callable=create_folder,
                                      op_kwargs={
                                          'bucket_name': 'datalake-banking',
                                          'folder_name': 'saving'
                                      },
                                      dag = dag)

# Tạo folder chứa các dữ liệu về các giao dịch
create_floder_transaction = PythonOperator(task_id = "Create_Folder_Transaction",
                                       python_callable=create_folder,
                                       op_kwargs={
                                           'bucket_name': 'datalake-banking',
                                           'folder_name': 'transaction'
                                       },
                                       dag = dag)


extract_process = EmptyOperator(task_id = 'Data_Extraction',  dag = dag)

# Tải dữ liệu về các tài khoản lên s3
upload_data_account = PythonOperator(task_id = "Upload_Data_Account",
                                     python_callable = upload_parquet_to_s3,
                                     op_kwargs = {
                                       'local_directory': f'dataCollection/account/{getYesterday()}.parquet', 
                                       'bucket_name': 'datalake-banking',
                                       'folder_direction': f'account/{getYesterday()}.parquet/'
                                     },
                                     dag = dag)

# Tải dữ liệu về các khoản vay lên s3
upload_data_loan = PythonOperator(task_id = "Upload_Data_Loan",
                                  python_callable = upload_parquet_to_s3,
                                  op_kwargs = {
                                    'local_directory': f'dataCollection/loan/{getYesterday()}.parquet', 
                                    'bucket_name': 'datalake-banking',
                                    'folder_direction': f'loan/{getYesterday()}.parquet/'
                                  },
                                  dag = dag)

# Tải dữ liệu về các khoản gửi tiết kiệm lên s3
upload_data_saving = PythonOperator(task_id = "Upload_Data_Saving",
                                    python_callable = upload_parquet_to_s3,
                                    op_kwargs = {
                                      'local_directory': f'dataCollection/savingdeposit/{getYesterday()}.parquet', 
                                      'bucket_name': 'datalake-banking',
                                      'folder_direction': f'saving/{getYesterday()}.parquet/'
                                    },
                                    dag = dag)

# Tải dữ liệu về các giao dịch lên s3
upload_data_transaction = PythonOperator(task_id = "Upload_Data_Transaction",
                                         python_callable = upload_parquet_to_s3,
                                         op_kwargs = {
                                           'local_directory': f'dataCollection/transaction/{getYesterday()}.parquet', 
                                           'bucket_name': 'datalake-banking',
                                           'folder_direction': f'transaction/{getYesterday()}.parquet/'
                                         },
                                         dag = dag)

transform_process = EmptyOperator(task_id = 'Data_Transformation',  dag = dag)

account_transform = SparkSubmitOperator(task_id="Account_Transform",
                                        conn_id='spark-conn',
                                        application='plugins/operators/transform/account_transform.py',
                                        dag=dag)

loan_transform = SparkSubmitOperator(task_id="Loan_Transform",
                                     conn_id='spark-conn',
                                     application='plugins/operators/transform/loan_transform.py',
                                     dag=dag)

saving_transform = SparkSubmitOperator(task_id="Saving_Transform",
                                       conn_id='spark-conn',
                                       application='plugins/operators/transform/saving_transform.py',
                                       dag=dag)

transaction_transform = SparkSubmitOperator(task_id="Transaction_Transform",
                                            conn_id='spark-conn',
                                            application='plugins/operators/transform/transaction_transform.py',
                                            dag=dag)

split_data = SparkSubmitOperator(task_id = "Split_Data",
                                 conn_id='spark-conn',
                                 application='plugins/operators/split/split_data.py',
                                 dag = dag)

load_process = EmptyOperator(task_id = 'Load_Data',  dag = dag)

load_data = BankingWarehouseDriver(task_id = "Load_S3_Warehouse",
                                   dag = dag)

monitor_checkdata = EmptyOperator(task_id = 'Monitor_CheckData',  dag = dag)

monitor_changed = MonitorOperator(task_id = 'Monitor_Changed',
                                  dag = dag)

data_quality = DataQualityOperator(task_id = 'Data_Quality',
                                   tables = ["banking.profileuser",
                                             "banking.accountinfo",
                                             "banking.accountpayment",
                                             "banking.moneytransaction",
                                             "banking.loan",
                                             "banking.savingdeposit"],
                                   dag = dag)

data_analytics = AnalyticsOperator(task_id = 'Data_Analytics',
                                   queries = [AnalyticsQueries.distributed_reason_transaction,
                                              AnalyticsQueries.distributed_bank_transaction,
                                              AnalyticsQueries.trans_month_default,
                                              AnalyticsQueries.reason_job_default,
                                              AnalyticsQueries.statistic_saving],
                                   dag = dag)


end_operator = EmptyOperator(task_id = 'End_execution',  dag = dag)

start_operator >> create_bucket >> [create_floder_account,
                                    create_floder_loan,
                                    create_floder_saving,
                                    create_floder_transaction] >> extract_process

extract_process >> [upload_data_account,
                    upload_data_loan,
                    upload_data_saving,
                    upload_data_transaction] >> transform_process

transform_process >> account_transform >> loan_transform >> saving_transform >> transaction_transform >> split_data >> load_process

load_process >> load_data >> monitor_checkdata

monitor_checkdata >> monitor_changed >> data_quality >> data_analytics >> end_operator