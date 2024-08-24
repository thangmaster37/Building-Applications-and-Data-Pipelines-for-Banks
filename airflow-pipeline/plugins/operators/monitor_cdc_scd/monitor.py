from airflow.models import BaseOperator
from airflow.utils.context import Context
from airflow.utils.decorators import apply_defaults
from helpers.getYesterday import getYesterday
import configparser
from pathlib import Path
import psycopg2
from datetime import datetime

config_rds = configparser.ConfigParser()
config_rds.read_file(open(f"{Path(__file__).parents[0]}/rds_config.cfg"))

config_redshift = configparser.ConfigParser()
config_redshift.read_file(open(f"{Path(__file__).parents[1]}/warehouse_config.cfg"))

class MonitorOperator(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs):
        self._conn_rds = psycopg2.connect("host={} port={} dbname={} user={} password={}".format(*config_rds['POSTGRES_AWS_RDS'].values()))
        self._cursor_rds = self._conn_rds.cursor()
        self._conn_redshift = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config_redshift['CLUSTER'].values()))
        self._cursor_redshift = self._conn_redshift.cursor()

        super(MonitorOperator, self).__init__(*args, **kwargs)


    def getChangeDatabase(self):
        sql = f"""
                    SELECT table_name, old_data, new_data, changed_at
                    FROM audit_log
                    WHERE TO_CHAR(changed_at, 'DD_MM_YYYY') = %s
                          AND operation = %s;
               """
        self._cursor_rds.execute(sql, (getYesterday(), 'UPDATE',))
        data = self._cursor_rds.fetchall()
        return data
    
    def getCountData(self):
        self._cursor_redshift.execute('SELECT count(*) FROM banking.loan')
        count = self._cursor_redshift.fetchall()[0][0]
        return count
    
    def insertNewData(self, loanID, accountPayID, loan, reason, job, yoj, createDate, expire, rate, status, bad, paymentDate):
        sql = f"""
                    INSERT INTO banking.loan(loanID, accountPayID, loan, reason, job, yoj, createDate, expire, rate, status, bad, paymentDate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               """
        self._cursor_redshift.execute(sql, (loanID, accountPayID, loan, reason,
                                            job, yoj, createDate, expire,
                                            rate, status, bad, paymentDate,))
        self._conn_redshift.commit()
        return {"message": "Insert one record successfully!"}
    
    def updateBadRecord(self, new_bad, loanID, paymentDate):
        sql = f"""
                    UPDATE banking.loan
                    SET bad = %s, paymentDate = %s
                    WHERE loanID = %s
               """
        self._cursor_redshift.execute(sql, (new_bad, paymentDate, loanID,))
        self._conn_redshift.commit()
        return {"message": "Update one record successfully!"}
    
    def updateStatusRecord(self, status, loanID):
        sql = f"""
                    UPDATE banking.loan
                    SET status = %s
                    WHERE loanID = %s
               """
        self._cursor_redshift.execute(sql, (status,loanID,))
        self._conn_redshift.commit()
        return {"message": "Update one record successfully!"}
    
    def updateWarehouse(self):
        for data in self.getChangeDatabase():
            old_data = data[1]
            new_data = data[2]
            paymentDate = data[3].replace(tzinfo=None, microsecond=0)
            if old_data['status'] is None:
                self.updateStatusRecord(new_data['status'], new_data['loanid'])
                return {'message': 'Update status'}
            else:
                if datetime.strptime(old_data['expire'], '%Y-%m-%d').date() >= paymentDate.date():
                    self.updateBadRecord(new_data['bad'], paymentDate, new_data['loanid'])
                    return {'message': 'Debts that have been paid on time'}
                else:
                    self.insertNewData(loanID = self.getCountData() + 1,
                                    accountPayID= new_data['accountpayid'],
                                    loan = new_data['loan'],
                                    reason = new_data['reason'],
                                    job = new_data['job'],
                                    yoj = new_data['yoj'],
                                    createDate = new_data['createDate'],
                                    expire = new_data['expire'],
                                    rate = new_data['rate'],
                                    status = new_data['status'],
                                    bad = new_data['bad'],
                                    paymentDate = paymentDate)
                    return {'message': 'Overdue debts'}
                
    def execute(self, context):
        self.updateWarehouse()


            



    

    