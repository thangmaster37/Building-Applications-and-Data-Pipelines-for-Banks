import psycopg2
from pydantic import BaseModel
from datetime import datetime
import random
import string
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


# Thông tin đăng nhập
class LoginInfo(BaseModel):
    username: str | None = None
    password: str | None = None


# Thông tin đăng ký tài khoản
class RegisterInfo(BaseModel):
    username: str | None = None
    password: str | None = None
    firstname: str | None = None
    middlename: str | None = None
    lastname: str | None = None
    banktype: str | None = None
    gender: str | None = None
    placeOfPermanent: str | None = None 
    dateOfBirth: str | None = None
    citizenID: str | None = None


def getAccountPayID(username):
    cursor.execute(f"""
                        select pay.accountPayID
                        from accountpayment as pay, accountinfo as info
                        where pay.userID = info.userID 
                              AND info.user_name = %s
                    """, (username,))
    
    accountPayID = cursor.fetchall()[0][0]
    return accountPayID


def checkLogin(info: LoginInfo):
    sql =  f"""
                select * from accountinfo
                where user_name = %s and password = %s
            """
    cursor.execute(sql, (info.username, info.password))
    response = cursor.fetchall()

    if len(response) == 1:
        return getAccountPayID(info.username)
    return -1


def getProfileID(citizenID):
    cursor.execute(f"""
                        select profileID from profileuser where citizenID = %s
                    """, (citizenID,))
    
    profileID = cursor.fetchall()[0][0]
    return profileID


def getUserID(username):
    cursor.execute(f"""
                        select userID
                        from accountinfo
                        where user_name = %s
                    """, (username,))
    
    userID = cursor.fetchall()[0][0]
    return userID


def getBankID(banktype):
    cursor.execute(f"""
                        select bankID
                        from bank
                        where aliasName = %s
                    """, (banktype,))
    
    bankID = cursor.fetchall()[0][0]
    return bankID


def checkExists(username):
    cursor.execute(f"SELECT * FROM accountinfo WHERE user_name = %s", (username,))
    data = cursor.fetchall()
    return len(data) == 0


def wirte_file_parquet(userID, username, password, firstname, middlename, lastname, banktype, accountPayID, gender, placeOfPermanent, dateOfBirth, citizenID, current):
    
    dataframe = pd.DataFrame({
        'userID': [userID],
        'username': [username],
        'password': [password],
        'status': [1],
        'firstname': [firstname],
        'middlename': [middlename],
        'lastname': [lastname],
        'banktype': [banktype],
        'accountPayID': [accountPayID],
        'surplus': [1000000.0],
        'gender': [gender],
        'placeOfPermanent': [placeOfPermanent],
        'dateOfBirth': [dateOfBirth],
        'citizenID': [citizenID],
        'createDate': [current]
    })

    date = datetime.today().strftime("%d_%m_%Y")
    output = f"../airflow-pipeline/dataCollection/account/{date}.parquet"

    # Create a parquet table from your dataframe
    table = pa.Table.from_pandas(dataframe)

    # Write direct to your parquet file
    pq.write_to_dataset(table , root_path=output)

    # print(pd.read_parquet(output))


def register_account(info: RegisterInfo):
    current = datetime.now()
    status = 1
    surplus = 1000000

    insert_profileuser = f"""
                            INSERT INTO profileuser (firstname, middlename, lastname, gender, placeOfPermanent, fullname, dateOfBirth, citizenID)
                            SELECT %s, %s, %s, %s, %s, %s, %s, %s
                            WHERE NOT EXISTS (SELECT 1
                                              FROM profileuser
                                              WHERE citizenID = %s);
                          """
    
    insert_accountinfo = f"""
                            INSERT INTO accountinfo (user_name, password, status, profileID, createDate)
                            SELECT %s, %s, %s, %s, %s
                            WHERE NOT EXISTS (SELECT 1
                                              FROM accountinfo
                                              WHERE user_name = %s);
                          """
    
    insert_accountpayment = f"""
                                INSERT INTO accountpayment (accountPayID, userID, bankID, surplus, status, createDate)
                                SELECT %s, %s, %s, %s, %s, %s
                                WHERE NOT EXISTS (SELECT 1
                                                FROM accountpayment
                                                WHERE userID = %s);
                             """
    if checkExists(info.username):
        cursor.execute(insert_profileuser, (info.firstname, 
                                            info.middlename, 
                                            info.lastname,
                                            info.gender,
                                            info.placeOfPermanent, 
                                            info.firstname + " " + info.middlename + " " + info.lastname,
                                            info.dateOfBirth,
                                            info.citizenID,
                                            info.citizenID,))
        conn.commit()

        profileID = getProfileID(info.citizenID)

        cursor.execute(insert_accountinfo, (info.username,
                                            info.password,
                                            status,
                                            profileID,
                                            current,
                                            info.username,))
        conn.commit()

        userID = getUserID(info.username)
        bankID = getBankID(info.banktype)
        accountPayID = ''.join(random.choices(string.digits, k=10))

        cursor.execute(insert_accountpayment, (accountPayID,
                                            userID,
                                            bankID,
                                            surplus,
                                            status,
                                            current,
                                            userID,))
        conn.commit()

        wirte_file_parquet(userID, info.username, info.password, info.firstname, 
                        info.middlename, info.lastname, info.banktype, 
                        accountPayID, info.gender, info.placeOfPermanent, 
                        info.dateOfBirth, info.citizenID, current)
        
        return True
    else:
        return False