import psycopg2
from pydantic import BaseModel
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd 
import pyarrow.parquet as pq
import pyarrow as pa
import configparser
from pathlib import Path


# Setting configurations. Look config.cfg for more details
config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/api_config.cfg"))

# Setup configs
host = config.get('POSTGRES_AWS_RDS', 'HOST')
port = config.get('POSTGRES_AWS_RDS', 'PORT')
database = config.get('POSTGRES_AWS_RDS', 'DATABASE')
user = config.get('POSTGRES_AWS_RDS', 'USER')
password = config.get('POSTGRES_AWS_RDS', 'PASSWORD')


# Kết nối đến cơ sở dữ liệu PostgreSQL
conn = psycopg2.connect(
    host=host,
    port=port,
    database=database,
    user=user,
    password=password
)

# Tạo đối tượng cursor để thực hiện truy vấn
cursor = conn.cursor()


class SavingDepositUser(BaseModel):
    username: str | None = None

class SavingDeposit(BaseModel):
    username: str | None = None
    money: float | None = None
    typeID: int | None = None
    period: str | None = None


def getAccountPayID(username):
    cursor.execute(f"""
                        select pay.accountPayID
                        from accountpayment as pay, accountinfo as info
                        where pay.userID = info.userID 
                              AND info.user_name = %s
                    """, (username,))
    
    accountPayID = cursor.fetchall()[0][0]
    return accountPayID


def convertPeriodToExpire(current_date, period):

    dict_period = {"One Month": 1, "Six Month": 6, "Twelve Month": 12, "Eighteen Month": 18,
                   "Twenty-Four Month": 24, "Thirty Month": 30, "Thirty-Six Month": 36,
                   "Forty-Two Month": 42, "Forty-Eight Month": 48, 
                   "Fifty-Four Month": 54, "Sixty Month": 60}

    # Cộng thời gian hiện tại với khoảng thời gian period (theo tháng)
    new_date = current_date + relativedelta(months=dict_period[period])

    # Format ngày mới theo định dạng "YYYY-MM-DD"
    new_date_formatted = new_date.strftime('%Y-%m-%d %H:%M:%S')
    return new_date_formatted


def getSavingType(typeID):
    cursor.execute(f"""
                        SELECT name
                        FROM payment_type
                        WHERE typeID = %s
                    """, (typeID,))
    saving_type = cursor.fetchall()[0][0]
    return saving_type


def getSavingID(accountPayID):
    cursor.execute(f"SELECT savingID FROM savingdeposit WHERE accountPayID = %s ORDER BY savingID ASC", (accountPayID,))
    data = cursor.fetchall()
    size = len(data)
    savingID = data[size-1][0]
    return savingID


def getRate(period):
    dict_period = {"One Month": 0.5, "Six Month": 3, "Twelve Month": 6, "Eighteen Month": 10,
                   "Twenty-Four Month": 13, "Thirty Month": 16, "Thirty-Six Month": 19,
                   "Forty-Two Month": 22, "Forty-Eight Month": 25, 
                   "Fifty-Four Month": 28, "Sixty Month": 30}
    rate = dict_period[period]
    return rate


def wirte_file_parquet(savingID, accountPayID, money, status, saving_type, createDate, expire, 
                       period, rate):
    
    dataframe = pd.DataFrame({
        'savingID': [savingID],
        'accountPayID': [accountPayID],
        'money': [money],
        'status': [status],
        'savingType': [saving_type],
        'createDate': [createDate],
        'expire': [expire],
        'period': [period],
        'rate': [rate]
    })

    date = datetime.today().strftime("%d_%m_%Y")
    output = f"../airflow-pipeline/dataCollection/savingdeposit/{date}.parquet"

    # Create a parquet table from your dataframe
    table = pa.Table.from_pandas(dataframe)

    # Write direct to your parquet file
    pq.write_to_dataset(table , root_path=output)

    # print(pd.read_parquet(output))


def saveInfoSavingDeposit(info: SavingDeposit):

    current = datetime.now()
    status = "Success"

    insert_savingdeposit = f"""
                            INSERT INTO savingdeposit (accountPayID, money, status, typeID, createDate, expire, period, rate)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
                    
    
    cursor.execute(insert_savingdeposit, (getAccountPayID(info.username),
                                          info.money,
                                          status,
                                          info.typeID,
                                          current,
                                          convertPeriodToExpire(current, info.period),
                                          info.period,
                                          getRate(info.period),))
    conn.commit()

    
    wirte_file_parquet(getSavingID(getAccountPayID(info.username)),
                       getAccountPayID(info.username),
                       info.money,
                       status,
                       getSavingType(info.typeID),
                       current,
                       convertPeriodToExpire(current, info.period),
                       info.period,
                       getRate(info.period))
    
    return getAccountPayID(info.username)
    

def getDataSavingDeposit(user: SavingDepositUser):
    accountPayID = getAccountPayID(user.username)
    cursor.execute(f"""
                        SELECT s.accountPayID, s.money, s.status, p.name, s.createDate, s.expire, s.period, s.rate
                        FROM savingdeposit as s, payment_type as p
                        WHERE s.accountPayID = %s 
                              AND s.typeID = p.typeID
                    """, (accountPayID,))
    
    data_savingdeposit = cursor.fetchall()
    return accountPayID, data_savingdeposit

