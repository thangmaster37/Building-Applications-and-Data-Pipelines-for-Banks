import psycopg2
from pydantic import BaseModel
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd 
import pyarrow.parquet as pq
import pyarrow as pa
import pickle   
import numpy as np
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


class LoanUser(BaseModel):
    username: str | None = None

class Loan(BaseModel):
    username: str | None = None
    loan: int | None = None
    reason: str | None = None
    job: str | None = None
    yoj: float | None = None
    period: str | None = None

class UpdateStatus(BaseModel):
    loanID: int | None = None
    value: str | None = None


model = pickle.load(open('../backend/model/model_df7/SVC.pickle', 'rb'))
labelEncoder = pickle.load(open('../backend/model/model_df7/LabelEncoder.pickle', 'rb'))
standard = pickle.load(open('../backend/model/model_df7/StandardScaler.pickle', 'rb'))


def getCitizenID(username):
    cursor.execute(f"""
                        select p.citizenID
                        from profileuser as p, accountinfo as a
                        where a.user_name = %s
                              AND p.profileID = a.profileID
                    """, (username,))
    
    citizenID = cursor.fetchall()[0][0]
    return citizenID


def getCreditHistory(citizenID):
    cursor.execute(f"""
                        select mortdue, value, derog, delinq, clage, ninq, clno, debtinc
                        from credithistory
                        where citizenID = %s
                    """, (citizenID,))
    
    data = cursor.fetchall()[0]
    if len(data) != 0:
        return data
    else:
        return (0,0,0,0,0,0,0,0,)


def preprocessing(info: Loan):
    credithistory = getCreditHistory(getCitizenID(info.username))
    mortdue = credithistory[0]
    value = credithistory[1]
    derog = credithistory[2]
    delinq = credithistory[3]
    clage = credithistory[4]
    ninq = credithistory[5]
    clno = credithistory[6]
    debtinc = credithistory[7]
    loan = info.loan
    reason = info.reason
    job = info.job
    yoj = info.yoj


    if reason == 'DebtCon':
        reason_debtcon = 1
        reason_homeimp = 0
    else:
        reason_debtcon = 0
        reason_homeimp = 1

    job_mapping = {
                    'Mgr': (1, 0, 0, 0, 0, 0),
                    'Office': (0, 1, 0, 0, 0, 0),
                    'Other': (0, 0, 1, 0, 0, 0),
                    'ProfExe': (0, 0, 0, 1, 0, 0),
                    'Sales': (0, 0, 0, 0, 1, 0),
                    'Self': (0, 0, 0, 0, 0, 1)
                }

    job_mgr, job_office, job_other, job_profexe, job_sales, job_self = job_mapping.get(job, (0, 0, 0, 0, 0, 0))

    input = standard.transform([[loan, mortdue, value, yoj, derog, delinq, 
                                 clage, ninq, clno, reason_debtcon, reason_homeimp,
                                 job_mgr, job_office, job_other,
                                 job_profexe, job_sales, job_self]])
    
    return input


def compute_credit_score(p):
    factor = 25 / np.log(2)
    offset = 600 - factor * np.log(50)
    val = (1-p) / p
    score = offset + factor * np.log(val)
    return round(score, 2)


def getAccountPayID(username):
    cursor.execute(f"""
                        select pay.accountPayID
                        from accountpayment as pay, accountinfo as info
                        where pay.userID = info.userID 
                              AND info.user_name = %s
                    """, (username,))
    
    accountPayID = cursor.fetchall()[0][0]
    return accountPayID


def getLoanID(accountPayID):
    cursor.execute(f"SELECT loanID FROM loan WHERE accountPayID = %s ORDER BY loanID ASC", (accountPayID,))
    data = cursor.fetchall()
    size = len(data)
    loanID = data[size-1][0]
    return loanID


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


def getRate(period):
    dict_period = {"One Month": 0.5, "Six Month": 3, "Twelve Month": 6, "Eighteen Month": 10,
                   "Twenty-Four Month": 13, "Thirty Month": 16, "Thirty-Six Month": 19,
                   "Forty-Two Month": 22, "Forty-Eight Month": 25, 
                   "Fifty-Four Month": 28, "Sixty Month": 30}
    rate = dict_period[period]
    return rate


def getScore(info: Loan):
    input = preprocessing(info)
    pred_proba = model.predict_proba(input)[0,1]
    score = compute_credit_score(pred_proba)
    return score


def wirte_file_parquet(loanID, accountPayID, createDate, expire, period, rate, loan, mortdue, 
                       value, reason, job, yoj, derog, delinq, clage, ninq, clno, debtinc):
    
    dataframe = pd.DataFrame({
        'loanID': [loanID],
        'accountPayID': [accountPayID],
        'createDate': [createDate],
        'expire': [expire],
        'period': [period],
        'rate': [rate],
        'loan': [loan],
        'mortdue': [mortdue],
        'value': [value],
        'reason': [reason],
        'job': [job],
        'yoj': [yoj],
        'derog': [derog],
        'delinq': [delinq],
        'clage': [clage],
        'ninq': [ninq],
        'clno': [clno],
        'debtinc': [debtinc]
    })

    date = datetime.today().strftime("%d_%m_%Y")
    output = f"../airflow-pipeline/dataCollection/loan/{date}.parquet"

    # Create a parquet table from your dataframe
    table = pa.Table.from_pandas(dataframe)

    # Write direct to your parquet file
    pq.write_to_dataset(table , root_path=output)

    # print(pd.read_parquet(output))


def saveInfoLoan(info: Loan):

    current = datetime.now()

    score = getScore(info)

    insert_loan = f"""
                    INSERT INTO loan (accountPayID, loan, reason, job, yoj, createDate, expire, period, rate, status, bad, score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                    
    
    cursor.execute(insert_loan, (getAccountPayID(info.username),
                                 info.loan,
                                 info.reason,
                                 info.job,
                                 info.yoj,
                                 current,
                                 convertPeriodToExpire(current, info.period),
                                 info.period,
                                 getRate(info.period),
                                 None,
                                 None,
                                 score,))
    conn.commit()


    credithistory = getCreditHistory(getCitizenID(info.username))

    
    wirte_file_parquet(getLoanID(getAccountPayID(info.username)),
                       getAccountPayID(info.username),
                       current,
                       convertPeriodToExpire(current, info.period),
                       info.period,
                       getRate(info.period),
                       info.loan,
                       credithistory[0],
                       credithistory[1],
                       info.reason,
                       info.job,
                       info.yoj,
                       credithistory[2],
                       credithistory[3],
                       credithistory[4],
                       credithistory[5],
                       credithistory[6],
                       credithistory[7])
    return getAccountPayID(info.username), score
    

def getDataLoan(user: LoanUser):
    accountPayID = getAccountPayID(user.username)
    cursor.execute(f"""
                        SELECT accountPayID, loan, reason, job, yoj, createDate, expire, period, rate, bad
                        FROM loan
                        WHERE accountPayID = %s AND
                              status = %s

                    """, (accountPayID, 'accept',))
    
    data_loan = cursor.fetchall()
    return accountPayID, data_loan  


def getModerationData():
    cursor.execute(f"""
                        SELECT loanID, accountPayID, loan, reason, job, yoj, createDate, expire, period, rate, score
                        FROM loan
                        WHERE status is NULL
                    """)
    
    data_loan = cursor.fetchall()
    return data_loan


def updateStatusAccept(info: UpdateStatus):
    cursor.execute(f"""
                        UPDATE loan
                        SET status = %s
                        WHERE loanID = %s
                    """, (info.value, info.loanID,))
    conn.commit()
    return True
    
    
def updateStatusReject(info: UpdateStatus):
    cursor.execute(f"""
                        UPDATE loan
                        SET status = %s
                        WHERE loanID = %s
                    """, (info.value, info.loanID,)) 
    conn.commit()
    return True
    


