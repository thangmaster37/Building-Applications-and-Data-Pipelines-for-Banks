from datetime import datetime, timedelta

# Lấy thời gian của ngày hôm qua - tên file sẽ được đẩy lên aws s3
def getYesterday():
    yesterday = datetime.today() - timedelta(days=1)
    date = yesterday.strftime("%d_%m_%Y")
    return date
