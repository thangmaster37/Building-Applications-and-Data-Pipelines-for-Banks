# import psycopg2

# host = 'database-bank-postgres.czmige66gy40.us-east-1.rds.amazonaws.com'
# port = '5432'
# database = 'bank'
# user = 'postgres'
# password = 'banking03072003'

# # Kết nối đến cơ sở dữ liệu PostgreSQL
# conn = psycopg2.connect(
#     host=host,
#     port=port,
#     database=database,
#     user=user,
#     password=password
# )

# # Tạo đối tượng cursor để thực hiện truy vấn
# cursor = conn.cursor()

# # Chèn dữ liệu từ file CSV vào bảng
# with open('backend\database\credithistory.csv', 'r') as file:
#     next(file)  # Bỏ qua header của file CSV
#     cursor.copy_from(file, 'credithistory', sep=',')
# conn.commit()
# cursor.close()
# conn.close()

import psycopg2

host = 'localhost'
port = '5432'
database = 'bank'
user = 'postgres'
password = 'thang2003'

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

# Chèn dữ liệu từ file CSV vào bảng
with open('backend/database/moneytransaction.csv', 'r') as file:
    next(file)  # Bỏ qua header của file CSV
    cursor.copy_from(file, 'moneytransaction', sep=',', null='')
conn.commit()
cursor.close()
conn.close()





