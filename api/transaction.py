import psycopg2
from pydantic import BaseModel
from datetime import datetime
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


class TransactionUser(BaseModel):
    username: str | None = None

class Transaction(BaseModel):
    username: str | None = None
    banktype: str | None = None
    toBankAccount: str | None = None
    typeID: int | None = None
    method: str | None = None
    amount: float | None = None
    content: str | None = None


def split_number_into_groups(number):
    number_str = str(number).split('.')
    fraction, decimal = number_str[0], number_str[1]
    length = len(fraction)
    groups = []

    for i in range(length - 1, -1, -3):
        group = fraction[max(0, i - 2):i + 1]
        groups.append(group)

    groups.reverse()
    return ','.join(groups) + "." + decimal + " VND"


def getAccountPayID(username):
    cursor.execute(f"""
                        select pay.accountPayID
                        from accountpayment as pay, accountinfo as info
                        where pay.userID = info.userID 
                              AND info.user_name = %s
                    """, (username,))
    
    accountPayID = cursor.fetchall()[0][0]
    return accountPayID


def getSavingType(typeID):
    cursor.execute(f"""
                        SELECT name
                        FROM payment_type
                        WHERE typeID = %s
                    """, (typeID,))
    saving_type = cursor.fetchall()[0][0]
    return saving_type


def getTransID():
    cursor.execute(f"""SELECT count(*) FROM moneytransaction""")
    count = cursor.fetchall()[0][0]
    transID = count
    return transID


def getSurplus(accountPayID):
    cursor.execute(f"""SELECT surplus FROM accountpayment WHERE accountPayID = %s""", (accountPayID,))
    surplus = cursor.fetchall()[0][0]
    return float(surplus)


def checkExistAccount(toBankAccount, banktype):
    cursor.execute(f"""
                        SELECT *
                        FROM accountpayment as a, bank as b
                        WHERE a.accountPayID = %s AND a.bankID = b.bankID AND b.aliasName = %s
                    """, (toBankAccount, banktype,))
    data = cursor.fetchall()
    return len(data) == 1


def wirte_file_parquet(transID, banktype, fromBankAccount, toBankAccount, amount, method, 
                       fees, surplus, saving_type, content, createDate):
    
    dataframe = pd.DataFrame({
        'transID': [transID],
        'toBankType': [banktype],
        'fromBankAccount': [fromBankAccount],
        'toBankAccount': [toBankAccount],
        'amount': [amount],
        'method': [method],
        'status': ["Success"],
        'fees': [fees],
        'surplus': [surplus],
        'savingType': [saving_type],
        'content': [content],
        'createDate': [createDate]
    })

    date = datetime.today().strftime("%d_%m_%Y")
    output = f"../airflow-pipeline/dataCollection/transaction/{date}.parquet"

    # Create a parquet table from your dataframe
    table = pa.Table.from_pandas(dataframe)

    # Write direct to your parquet file
    pq.write_to_dataset(table , root_path=output)

    # print(pd.read_parquet(output))


def saveInfoTransaction(info: Transaction):

    current = datetime.now()
    status = "Success"
    fees = round(1.0 * info.amount * 0.02 / 100, 2)
    surplus = round(getSurplus(getAccountPayID(info.username)) - info.amount - fees, 2)

    if checkExistAccount(info.toBankAccount, info.banktype):

        insert_moneytransaction = f"""
                                    INSERT INTO moneytransaction (fromBankAccount, toBankAccount, amount, method, 
                                                                status, fees, surplus, typeID, content, createDate)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        
        change_surplus_from = f"""
                                    UPDATE accountpayment
                                    SET surplus = %s
                                    WHERE accountPayID = %s
                            """
        
        change_surplus_to = f"""
                                UPDATE accountpayment
                                SET surplus = %s
                                WHERE accountPayID = %s
                            """
                        
        
        cursor.execute(insert_moneytransaction, (getAccountPayID(info.username),
                                                info.toBankAccount,
                                                info.amount,
                                                info.method,
                                                status,
                                                fees,
                                                surplus,
                                                info.typeID,
                                                info.content,
                                                current,))
        conn.commit()


        cursor.execute(change_surplus_from, (surplus,
                                            getAccountPayID(info.username),))
        conn.commit()
    

        cursor.execute(change_surplus_to, (getSurplus(info.toBankAccount) + info.amount,
                                        info.toBankAccount,))
        conn.commit()

        
        wirte_file_parquet(getTransID(),
                        info.banktype,
                        getAccountPayID(info.username),
                        info.toBankAccount,
                        info.amount,
                        info.method,
                        fees,
                        surplus,
                        getSavingType(info.typeID),
                        info.content,
                        current)
        return getAccountPayID(info.username), info.toBankAccount
    else: 
        return getAccountPayID(info.username), -1
    

def getAccountAndSurplus(user: TransactionUser):
    accountPayID = getAccountPayID(user.username)
    cursor.execute(f"""
                        SELECT accountPayID, surplus 
                        FROM accountpayment 
                        WHERE accountPayID = %s
                    """, (accountPayID,))
    
    data = cursor.fetchall()

    return data


def getDataTransaction(user: TransactionUser):
    accountPayID = getAccountPayID(user.username)
    cursor.execute(f"""
                        SELECT amount, status, createDate,
                                CASE
                                    WHEN fromBankAccount = %s THEN 1
                                    ELSE 0
                                END AS sender
                        FROM moneytransaction
                        WHERE fromBankAccount = %s OR toBankAccount = %s
                        ORDER BY createDate DESC
                        LIMIT 7
                    """, (accountPayID, accountPayID, accountPayID,))
    
    data = cursor.fetchall()

    return data


