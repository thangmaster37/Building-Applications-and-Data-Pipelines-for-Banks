import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()

# Định nghĩa các giá trị mẫu cho các trường
methods = ["ATM Card", "Wire Transfer", "Credit Card", "Debit Card"]
types = ["mua sắm", "mua nhà", "thanh toán hóa đơn", "thanh toán học phí", "thanh toán lương", "mua cổ phiếu", "từ thiện", "đóng bảo hiểm", "du lịch", "trả nợ"]

# Tạo bộ dữ liệu
data = []
for _ in range(999):
    amount = round(np.random.uniform(10000, 50000000), 0)
    method = np.random.choice(methods)
    surplus = round(np.random.uniform(0, 50000000), 0)
    transaction_type = np.random.choice(types)
    year = np.random.choice([2023, 2024])
    month = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    day = np.random.choice([i for i in range(1, 30)])
    hour = np.random.choice([i for i in range(0, 23)])
    minute = np.random.choice([i for i in range(0, 59)])

    is_fraud = np.random.choice([0, 1], p=[0.85, 0.15])  # Giả sử 5% là gian lận
    
    data.append([amount, method, surplus, transaction_type, year, month, day, hour, minute, is_fraud])

# Tạo DataFrame
df = pd.DataFrame(data, columns=["amount", "method", "surplus", "type", "year", "month", "day", "hour", "minute", "isFraud"])

# Lưu ra file CSV
df.to_csv("fraud_transactions.csv", index=False)

