from kafka import KafkaProducer
from time import sleep
import json
import psycopg2
from pathlib import Path
import configparser

# Setting configurations. Look config.cfg for more details
config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.cfg"))

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

# Hàm tuần tự hóa để chuyển đổi dữ liệu thành chuỗi JSON
def json_serializer(data):
    return json.dumps(data).encode('utf-8')

# Hàm dùng để lấy giao dịch mới nhất
def getNewTransaction():
    cursor.execute("""
        SELECT 
            m.transID, 
            m.fromBankAccount, 
            m.toBankAccount, 
            m.amount, 
            m.method, 
            m.status, 
            m.fees, 
            m.surplus, 
            p.name as type, 
            m.content, 
            m.createDate 
        FROM moneytransaction as m, payment_type as p
        WHERE m.typeID = p.typeID
        ORDER BY transID DESC
        LIMIT 1;
    """)
    data = cursor.fetchall()[0]
    return {
        'transID': data[0],
        'fromBankAccount': data[1],
        'toBankAccount': data[2],
        'amount': float(data[3]),
        'method': data[4],
        'status': data[5],
        'fees': float(data[6]),
        'surplus': float(data[7]),
        'type': data[8],
        'content': data[9],
        'createDate': data[10].strftime('%Y-%m-%d %H:%M:%S')
    }


producer = KafkaProducer(bootstrap_servers  = ['localhost:9092'],
                         value_serializer=json_serializer,
                         api_version=(0, 10, 1))

Id_new = 0

while True:
    data = getNewTransaction()
    transID = data['transID']
    if transID == Id_new:    
        continue
    else:
        Id_new = transID
        producer.send('test', data)

# Đảm bảo rằng tất cả các thông điệp đã được gửi
producer.flush()

print("Message sent successfully")