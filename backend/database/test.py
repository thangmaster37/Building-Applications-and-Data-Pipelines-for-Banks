import random
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Định nghĩa dữ liệu
accountPayIDs = [
    '6496913603', '3960086839', '7976125545', '8203283023', '2843848429',
    '5920548482', '3052928452', '9274922399', '6303485293', '1333924038'
]

# Định nghĩa period và rate tương ứng
period_map = {
    "one month": 1,
    "six month": 6,
    "twelve month": 12,
    "eighteen month": 18,
    "twenty-four month": 24,
    "thirty month": 30,
    "thirty-six month": 36,
    "forty-two month": 42,
    "forty-eight month": 48,
    "fifty-four month": 54,
    "sixty month": 60
}

period_rate_map = {
    "one month": 0.5,
    "six month": 3,
    "twelve month": 6,
    "eighteen month": 10,
    "twenty-four month": 13,
    "thirty month": 16,
    "thirty-six month": 19,
    "forty-two month": 22,
    "forty-eight month": 25,
    "fifty-four month": 28,
    "sixty month": 30
}

# # Tạo bộ dữ liệu
# data = []

# for userID in range(1,1001):  # Giả sử cần 10 dòng dữ liệu
#     savingID = userID
#     accountPayID = random.choice(accountPayIDs)
#     money = round(random.uniform(1000000, 50000000), 0)
#     status = "success"
#     typeID = random.randint(1, 10)
    
#     # Random createDate từ 2024-09-12 đổ đi
#     start_date = datetime(2024, 9, 12, 6,0,0)
#     createDate = start_date + relativedelta(minutes=userID)
#     period = random.choice(list(period_map.keys()))
#     expire = createDate + relativedelta(months=period_map[period])
#     # Chọn period và tính expire
#     rate = period_rate_map[period]
    
#     data.append([
#         savingID, accountPayID, money, status, typeID, 
#         createDate.strftime("%Y-%m-%d %H:%M:%S"), 
#         expire.strftime("%Y-%m-%d %H:%M:%S"), 
#         period, rate
#     ])

# # Tạo DataFrame
# df = pd.DataFrame(data, columns=[
#     "savingID", "accountPayID", "money", "status", "typeID", 
#     "createDate", "expire", "period", "rate"
# ])

# # Ghi dữ liệu vào file CSV
# df.to_csv("backend\database\savingdeposit.csv", index=False)


# reasons = ['debtcon', 'homeimp']
# jobs = ['sales','self','mgr','office','profexe','other']
# status_diff = ['','accept','reject']

# # Tạo bộ dữ liệu
# data = []

# for userID in range(1,1001):  # Giả sử cần 10 dòng dữ liệu
#     loanID = userID
#     accountPayID = random.choice(accountPayIDs)
#     loan = int(round(random.uniform(1000000, 50000000), 0))
#     reason = random.choice(reasons)
#     job = random.choice(jobs)
#     yoj = random.randint(0,40)
    
#     # Random createDate từ 2024-09-12 đổ đi
#     start_date = datetime(2024, 9, 12, 5,30,0)
#     createDate = start_date + relativedelta(minutes=userID)
#     period = random.choice(list(period_map.keys()))
#     expire = createDate + relativedelta(months=period_map[period])
#     # Chọn period và tính expire
#     rate = period_rate_map[period]
#     status = random.choice(status_diff)
#     bad = None
#     paymentDate = None
    
#     data.append([
#         loanID, accountPayID, loan, reason, job, yoj,
#         createDate.strftime("%Y-%m-%d %H:%M:%S"), 
#         expire.strftime("%Y-%m-%d %H:%M:%S"), 
#         period, rate, status, bad, paymentDate
#     ])

# # Tạo DataFrame
# df = pd.DataFrame(data, columns=[
#     "loanID", "accountPayID", "loan", "reason", "job", "yoj",
#     "createDate", "expire", "period", "rate", "status", "bad", "paymentDate"
# ])

# # Ghi dữ liệu vào file CSV
# df.to_csv("backend\database\loan.csv", index=False)


# Định nghĩa các giá trị mẫu cho các trường
methods = ["atm card", "wire transfer", "credit card", "debit card"]

# Tạo bộ dữ liệu
data = []

for userID in range(1,4001):  # Giả sử cần 10 dòng dữ liệu
    transID = userID
    fromBankAccount = random.choice(accountPayIDs)
    toBankAccount = random.choice(accountPayIDs)
    amount = round(random.uniform(1000000, 50000000), 2)
    method = random.choice(methods)
    status = 'success'
    surplus = round(random.uniform(1000000, 50000000), 2)
    fees = round(1.0 * amount * 0.02 / 100, 2)
    typeID = random.randint(1,10)
    content = str(fromBankAccount) + " chuyen den " + str(toBankAccount)
    # Random createDate từ 2024-09-12 đổ đi
    start_date = datetime(2024, 9, 12, 0,0,0)
    createDate = start_date + relativedelta(seconds=userID*20)

    data.append([
        transID, fromBankAccount, toBankAccount, amount, method, status, surplus, fees, typeID, content,
        createDate.strftime("%Y-%m-%d %H:%M:%S")
    ])

# Tạo DataFrame
df = pd.DataFrame(data, columns=[
    "transID", "fromBankAccount", "toBankAccount", "amount", "method", "status",
    "surplus", "fees", "typeID", "content", "createDate"
])

# Ghi dữ liệu vào file CSV
df.to_csv("backend\database\moneytransaction.csv", index=False)





