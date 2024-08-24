from pyspark.sql.types import StringType,TimestampType
from pyspark.sql.functions import udf
from datetime import datetime
from unidecode import unidecode

# Loại bỏ các khoảng trắng dư thừa
@udf(StringType())
def removeExtraSpaces(data):
    return data.strip()

# Chuyển các trường định dạng string về chữ thường
@udf(StringType())
def transformLowerCase(data):
    return data.lower()

# Bỏ dấu tiếng việt các trường định dạng string
@udf(StringType())
def transformUnideCode(data):
    return unidecode(data)

# Chuyển đổi trường dữ liệu thời gian về một định dạng chuẩn
@udf(TimestampType())
def transformDateTime(time):
    if type(time) != str:
        new_time = time.strftime("%Y-%m-%d %H:%M:%S")
    else: 
        new_time = time
    return datetime.strptime(new_time, "%Y-%m-%d %H:%M:%S")

