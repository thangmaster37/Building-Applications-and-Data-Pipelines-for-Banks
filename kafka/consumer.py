import streamlit as st
from kafka import KafkaConsumer
import json
from json import loads
import pickle
from datetime import datetime
from send_sms import warning

model_fraud = pickle.load(open('../backend/model_fraud/DecisionTreeClassifier.pickle', 'rb'))
stardardScaler = pickle.load(open('../backend/model_fraud/StandardScaler.pickle', 'rb'))

# Hàm giải mã để chuyển đổi chuỗi JSON trở lại thành Python object
def json_deserializer(data):
    return json.loads(data.decode('utf-8'))

consumer = KafkaConsumer('test',
                         bootstrap_servers=['localhost:9092'],
                         value_deserializer=json_deserializer,
                         api_version=(0, 10))

def getInfoDate(date):
    # Chuyển đổi chuỗi thành đối tượng datetime
    date_time_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    # Trích xuất ngày, tháng, năm, giờ, phút và giây
    year = date_time_obj.year
    month = date_time_obj.month
    day = date_time_obj.day
    hour = date_time_obj.hour
    minute = date_time_obj.minute

    return year, month, day, hour, minute

def predict_fraud(data, standardScaler, model):
    infodate = getInfoDate(data['createDate'])
    amount = data['amount']
    surplus = data['surplus']
    method = data['method']
    typePay = data['type']
    year = infodate[0]
    month = infodate[1]
    day = infodate[2]
    hour = infodate[3]
    minute = infodate[4]


    method_mapping = {
                    'ATM Card': (1, 0, 0, 0),
                    'Credit Card': (0, 1, 0, 0),
                    'Debit Card': (0, 0, 1, 0),
                    'Wire Transfer': (0, 0, 0, 1)
                }

    method_ATM, method_Credit, method_Debit, method_Wire = method_mapping.get(method, (0, 0, 0, 0))

    type_mapping = {
                    'du lịch': (1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                    'mua cổ phiếu': (0, 1, 0, 0, 0, 0, 0, 0, 0, 0),
                    'mua nhà': (0, 0, 1, 0, 0, 0, 0, 0, 0, 0),
                    'mua sắm': (0, 0, 0, 1, 0, 0, 0, 0, 0, 0),
                    'thanh toán hóa đơn': (0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
                    'thanh toán học phí': (0, 0, 0, 0, 0, 1, 0, 0, 0, 0),
                    'thanh toán lương': (0, 0, 0, 0, 0, 0, 1, 0, 0, 0),
                    'trả nợ': (0, 0, 0, 0, 0, 0, 0, 1, 0, 0),
                    'từ thiện': (0, 0, 0, 0, 0, 0, 0, 0, 1, 0),
                    'đóng bảo hiểm': (0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
                }
    
    type_dulich, type_cophieu, type_muanha, type_muasam, type_hoadon, type_hocphi, type_luong, type_trano, type_tuthien, type_baohiem = type_mapping.get(typePay, (0,0,0,0,0,0,0,0,0,0))


    data_std = standardScaler.transform([[amount, surplus, year, month, day, hour, minute,
                                         method_ATM, method_Credit, method_Debit, method_Wire,
                                         type_dulich, type_cophieu, type_muanha, type_muasam, 
                                         type_hoadon, type_hocphi, type_luong, type_trano, type_tuthien, type_baohiem]])
    
    predict = model.predict(data_std)

    return predict

# Hàm để tạo bảng với màu sắc xen kẽ
def create_colored_table(datas, standardScaler, model):
    # Tạo HTML table
    html_table = '<h2 class="title">Dashboard for Detection Fraud Transactions</h2>'
    html_table += '<div class="table-container"><table class="styled-table">'
    html_table += '<thead><tr>'
    for column in ['transID', 'fromBankAccount', 'toBankAccount', 'amount', 'method', 'status', 'fees', 'surplus', 'type', 'content', 'createDate']:
        html_table += f'<th>{column}</th>'
    html_table += '</tr></thead><tbody>'

    # Thêm các hàng với màu sắc xen kẽ
    for data in datas:
        predict = predict_fraud(data, standardScaler, model)[0]
        if predict % 2 == 0:
            color = '#00FF80' 
        else:
            color = '#FF3333'
            warning()
        html_table += f'<tr style="background-color: {color};">'
        for key in ['transID', 'fromBankAccount', 'toBankAccount', 'amount', 'method', 'status', 'fees', 'surplus', 'type', 'content', 'createDate']:
            html_table += f'<td>{data[key]}</td>'
        html_table += '</tr>'
    html_table += '</tbody></table></div>'
    
    return html_table

# Tạo một CSS style cho bảng
st.markdown(
    """
    <style>
    .table-container {
        max-height: 50px;
    }
    .styled-table {
        width: 190%;
        font-size: 0.9em;
        margin-left: -20rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .styled-table th, .styled-table td {
        border: 1px solid #dddddd;
        text-align: center;
        padding: 10px; /* Điều chỉnh khoảng cách */
    }
    .styled-table th {
        background-color: #009879;
        color: #ffffff;
    }
    .title {
        font-size: 2em;
        margin-left: -20rem;
        margin-top: -5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Tạo dữ liệu trống
datas = []

# Tạo một vị trí trống cho bảng
table_placeholder = st.empty()

# Vòng lặp Kafka Consumer và cập nhật bảng khi có bản ghi mới
for mess in consumer:
    record = mess.value
    datas.append(record)
    
    # Cập nhật bảng với dữ liệu mới
    table_html = create_colored_table(datas, stardardScaler, model_fraud)
    table_placeholder.markdown(table_html, unsafe_allow_html=True)
