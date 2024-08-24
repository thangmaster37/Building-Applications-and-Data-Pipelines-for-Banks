# import psycopg2
# from pathlib import Path
# import configparser


# from datetime import datetime, timedelta

# # Lấy thời gian của ngày hôm qua - tên file sẽ được đẩy lên aws s3
# def getYesterday():
#     yesterday = datetime.today() - timedelta(days=1)
#     date = yesterday.strftime("%d_%m_%Y")
#     return date


# config_rds = configparser.ConfigParser()
# config_rds.read_file(open(f"{Path(__file__).parents[0]}/rds_config.cfg"))

# conn_rds = psycopg2.connect("host={} port={} dbname={} user={} password={}".format(*config_rds['POSTGRES_AWS_RDS'].values()))

# cursor = conn_rds.cursor()

# sql = f"""
#                     SELECT table_name, old_data, new_data, changed_at
#                     FROM audit_log
#                     WHERE TO_CHAR(changed_at, 'DD_MM_YYYY') = %s
#                           AND operation = %s;
#                """
# cursor.execute(sql, (getYesterday(), 'UPDATE',))
# data = cursor.fetchall()
# print(data)
import datetime

a = datetime.datetime(2024, 8, 11, 3, 17, 53, 603864, tzinfo=datetime.timezone.utc)
print(a.replace(tzinfo=None, microsecond=0))