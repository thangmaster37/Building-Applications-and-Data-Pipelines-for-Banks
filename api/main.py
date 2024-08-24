import os
import time
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from register_and_login import checkLogin, register_account, LoginInfo, RegisterInfo
from loan import Loan, saveInfoLoan, compute_credit_score, preprocessing, model, getDataLoan, LoanUser, getModerationData, UpdateStatus, updateStatusAccept, updateStatusReject
from savingdeposit import SavingDeposit, saveInfoSavingDeposit, getDataSavingDeposit, SavingDepositUser
from transaction import Transaction, saveInfoTransaction, TransactionUser, getAccountAndSurplus, split_number_into_groups, getDataTransaction
from log_helpers import create_log_id, log_start_message, log_end_message, log_report_message

app = FastAPI()

date = datetime.today().strftime("%d_%m_%Y")

templates = Jinja2Templates(directory="../frontend/bank")

# Tạo một formatter chung cho các handlers
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Dictionary để lưu các handlers cho từng API
api_loggers = {}
 
# Hàm để tạo handler cho mỗi API và thư mục log tương ứng
def create_api_logger(api_name, log_dir):
    os.makedirs(log_dir, exist_ok=True)

    handler = logging.FileHandler(f'{log_dir}/{api_name}_{date}.log')
    handler.setFormatter(formatter) 

    # Tạo một logger chung
    logger = logging.getLogger(api_name)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(handler)
    api_loggers[api_name] = logger


# Định nghĩa các API và thư mục log tương ứng
apis = {
    'login': '../airflow-pipeline/logs/api/login',
    'register': '../airflow-pipeline/logs/api/register',
    'loan': '../airflow-pipeline/logs/api/loan',
    'savingdeposit': '../airflow-pipeline/logs/api/savingdeposit',
    'transaction': '../airflow-pipeline/logs/api/transaction',
    'dataloan': '../airflow-pipeline/logs/api/dataloan',
    'datasaving': '../airflow-pipeline/logs/api/datasaving'
}


# Tạo handlers cho từng API và thư mục log
for api, log_dir in apis.items():
    create_api_logger(api, log_dir)


# API dùng để kiểm tra đăng nhập
@app.post('/api/login')
async def login(info: LoginInfo):

    request_id = create_log_id()

    log_start_message(api_loggers['login'], f"RequestId: {request_id} Version: $LATEST")

    try:
        # Hàm kiểm tra đăng nhập
        start_time = time.time()
        account = checkLogin(info)
        end_time = time.time()
    except Exception as e:
        api_loggers['login'].error('Error')
        log_end_message(api_loggers['login'], f"RequestId: {request_id}")
        log_report_message(api_loggers['login'], f"RequestId: {request_id}")

    if account != -1:
        api_loggers['login'].info({"accountPayID": account})
        log_end_message(api_loggers['login'], f"RequestId: {request_id}")
        log_report_message(api_loggers['login'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")
        return {"response": True}
    else:
        api_loggers['login'].info({"accountPayID": "-1"})
        log_end_message(api_loggers['login'], f"RequestId: {request_id}")
        log_report_message(api_loggers['login'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time),2)} ms")
        return {"response": False}


# API dùng để tạo tài khoản ngân hàng và lưu thông tin
@app.post('/api/register')
async def register(info: RegisterInfo):

    request_id = create_log_id()

    log_start_message(api_loggers['register'], f"RequestId: {request_id} Version: $LATEST")

    try:
        # Đăng kí tài khoản ngân hàng
        start_time = time.time()
        response = register_account(info)
        end_time = time.time()
    except Exception as e:
        api_loggers['register'].error("Error")
        log_end_message(api_loggers['register'], f"RequestId: {request_id}")
        log_report_message(api_loggers['register'], f"RequestId: {request_id}")

    if response:
        api_loggers['register'].info({"response": True})
        log_end_message(api_loggers['register'], f"RequestId: {request_id}")
        log_report_message(api_loggers['register'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")
        return {"response": response}
    else:
        api_loggers['register'].info({"response": False})
        log_end_message(api_loggers['register'], f"RequestId: {request_id}")
        log_report_message(api_loggers['register'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")
        return {"response": response}


# API dùng để tính credit score cho người vay và lưu thông tin
@app.post('/api/credit_score')
async def score(info: Loan):

    request_id = create_log_id()

    log_start_message(api_loggers['loan'], f"RequestId: {request_id} Version: $LATEST")

    try:    
        start_time = time.time()
        # Lưu thông tin
        accountPayID, score = saveInfoLoan(info)
        end_time = time.time()
    except Exception as e:
        api_loggers['loan'].error("Error")
        log_end_message(api_loggers['loan'], f"RequestId: {request_id}")
        log_report_message(api_loggers['loan'], f"RequestId: {request_id}")

    api_loggers['loan'].info({"accountPayID": accountPayID})
    log_end_message(api_loggers['loan'], f"RequestId: {request_id}")
    log_report_message(api_loggers['loan'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")
    return {'score': score, 'response': True}
    

# API dùng để gửi tiết kiệm và lưu thông tin
@app.post('/api/saving_deposit')
async def savingDeposit(info: SavingDeposit):

    request_id = create_log_id()

    log_start_message(api_loggers['savingdeposit'], f"RequestId: {request_id} Version: $LATEST")
    
    try:
        start_time = time.time()
        accountPayID = saveInfoSavingDeposit(info)
        end_time = time.time()
    except Exception as e:
        api_loggers['savingdeposit'].error("Error")
        log_end_message(api_loggers['savingdeposit'], f"RequestId: {request_id}")
        log_report_message(api_loggers['savingdeposit'], f"RequestId: {request_id}")

    api_loggers['savingdeposit'].info({"accountPayID": accountPayID})
    log_end_message(api_loggers['savingdeposit'], f"RequestId: {request_id}")
    log_report_message(api_loggers['savingdeposit'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")
    
    return {"response": True}
    

# API dùng để giao dịch giữa các tài khoản và lưu thông tin
@app.post('/api/transaction')
async def transaction(info: Transaction):

    request_id = create_log_id()

    log_start_message(api_loggers['transaction'], f"RequestId: {request_id} Version: $LATEST")

    try:
        start_time = time.time()
        fromBankAccount, toBankAccount = saveInfoTransaction(info)
        end_time = time.time()
    except Exception as e:
        api_loggers['transaction'].error("Error")
        log_end_message(api_loggers['transaction'], f"RequestId: {request_id}")
        log_report_message(api_loggers['transaction'], f"RequestId: {request_id}")

    if toBankAccount != -1:
        api_loggers['transaction'].info({"fromBankAccount": fromBankAccount})
        log_end_message(api_loggers['transaction'], f"RequestId: {request_id}")
        log_report_message(api_loggers['transaction'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")
        return {"response": True}
    else: 
        api_loggers['transaction'].info({"fromBankAccount": "-1"})
        log_end_message(api_loggers['transaction'], f"RequestId: {request_id}")
        log_report_message(api_loggers['transaction'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")
        return {"response": False}
    

# API dùng để trả về lịch sử vay của khách hàng
@app.post('/api/data_loan')
async def get_data_loan(user: LoanUser):

    request_id = create_log_id()

    log_start_message(api_loggers['dataloan'], f"RequestId: {request_id} Version: $LATEST")

    try:
        start_time = time.time()
        accountPayID, data = getDataLoan(user)
        end_time = time.time()
    except Exception as e:
        api_loggers['dataloan'].error(e)
        api_loggers['dataloan'].info({"response": False, "message": "Get data loan failed!"})
        log_end_message(api_loggers['dataloan'], f"RequestId: {request_id}")
        log_report_message(api_loggers['dataloan'], f"RequestId: {request_id}")

    api_loggers['dataloan'].info({"accountPayID": accountPayID, "response": True, "message": "Get data loan successfully!"})
    log_end_message(api_loggers['dataloan'], f"RequestId: {request_id}")
    log_report_message(api_loggers['dataloan'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")

    return {'loan': data}
    
# API dùng để trả về lịch sử gửi tiết kiệm của khách hàng
@app.post('/api/data_savingdeposit')
async def get_data_loan(user: SavingDepositUser):

    request_id = create_log_id()

    log_start_message(api_loggers['datasaving'], f"RequestId: {request_id} Version: $LATEST")

    try:
        start_time = time.time()
        accountPayID, data = getDataSavingDeposit(user)
        end_time = time.time()
    except Exception as e:
        api_loggers['datasaving'].error(e)
        api_loggers['datasaving'].info({"response": False, "message": "Get data saving deposit failed!"})
        log_end_message(api_loggers['datasaving'], f"RequestId: {request_id}")
        log_report_message(api_loggers['datasaving'], f"RequestId: {request_id}")

    api_loggers['datasaving'].info({"accountPayID": accountPayID, "response": True, "message": "Get data saving deposit successfully!"})
    log_end_message(api_loggers['datasaving'], f"RequestId: {request_id}")
    log_report_message(api_loggers['datasaving'], f"RequestId: {request_id} Duration: {round(1000.0 * (end_time - start_time), 2)} ms")

    return {'savingdeposit': data}

# API dùng để lấy dữ liệu loan chưa được kiểm duyệt
@app.post('/api/data_moderation')
async def get_moderation_data():
    data = getModerationData()
    return {'data': data}

# API dùng để update status loan thành ACCEPT
@app.put('/api/loan_accept')
async def loan_accept(update: UpdateStatus):
    return {'response': updateStatusAccept(update)}

# API dùng để update status loan thành REJECT
@app.put('/api/loan_reject')
async def loan_reject(update: UpdateStatus):
    return {'response': updateStatusReject(update)}
    
# API dùng để lấy tài khoảng và số dư của người dùng
@app.post('/api/account_surplus')
async def get_account_surplus(user: TransactionUser):
    data = getAccountAndSurplus(user)
    account = data[0][0]
    surplus = float(data[0][1])
    return {"account": account, "surplus": split_number_into_groups(surplus)}

# API dùng để lấy lịch sử giao dịch của người dùng
@app.post('/api/data_transaction')
async def get_data_transaction(user: TransactionUser):
    data = getDataTransaction(user)
    return {"transaction": data}

# Cập nhật các URL cho phù hợp với URL của ứng dụng frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)