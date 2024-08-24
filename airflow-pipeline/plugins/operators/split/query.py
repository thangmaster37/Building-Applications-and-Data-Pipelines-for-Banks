
# Lấy dữ liệu cho table accountinfo
def query_get_accountinfo(table):
    return f"""
                SELECT userID, username, password, status, profileID, createDate
                FROM {table}
                ORDER BY userID ASC
            """

# Lấy dữ liệu cho table profileuser
def query_get_profileuser(table):
    return f"""
                SELECT profileID, firstname, middlename, lastname, gender, ward, district, city, dateOfBirth, citizenID
                FROM {table}
                ORDER BY profileID ASC
            """

# Lấy dữ liệu cho table accountpayment
def query_get_accountpayment(table):

    # Tạo truy vấn SQL 
    sql_query = f"""
                    SELECT accountPayID, userID, 
                        CASE 
                            WHEN banktype = 'mbbank' THEN 1
                            WHEN banktype = 'vpbank' THEN 2
                            WHEN banktype = 'techcombank' THEN 3
                            WHEN banktype = 'vietcombank' THEN 4
                            WHEN banktype = 'bidv' THEN 5
                            WHEN banktype = 'agribank' THEN 7
                            WHEN banktype = 'vib' THEN 8
                            WHEN banktype = 'acb' THEN 9
                            WHEN banktype = 'shb' THEN 10
                            WHEN banktype = 'saigonbank' THEN 11
                            WHEN banktype = 'scb' THEN 12
                            WHEN banktype = 'ocb' THEN 13
                            WHEN banktype = 'seabank' THEN 14
                            WHEN banktype = 'oceanbank' THEN 15
                            WHEN banktype = 'gpbank' THEN 16
                            WHEN banktype = 'abbank' THEN 17
                            WHEN banktype = 'pgbank' THEN 18
                            WHEN banktype = 'hdbank' THEN 19
                            WHEN banktype = 'eximbank' THEN 20
                        END AS bankID,
                        surplus, status, createDate
                    FROM {table}
                    ORDER BY userID
                 """
    return sql_query

# Lấy dữ liệu cho table loan
def query_get_loan(table):
    return f"""
                SELECT loanID, accountPayID, loan, reason, job, yoj, createDate, expire, period, rate
                FROM {table}
                ORDER BY loanID
            """

# Lấy dữ liệu cho table saving deposit 
def query_get_saving_deposit(table):

    # Tạo truy vấn SQL
    sql_query = f"""
                    SELECT savingID, accountPayID, money, status,
                    CASE 
                        WHEN savingType = 'mua sam' THEN 1
                        WHEN savingType = 'mua nha' THEN 2
                        WHEN savingType = 'thanh toan hoa don' THEN 3
                        WHEN savingType = 'thanh toan hoc phi' THEN 4
                        WHEN savingType = 'thanh toan luong' THEN 5
                        WHEN savingType = 'mua co phieu' THEN 6
                        WHEN savingType = 'tu thien' THEN 7
                        WHEN savingType = 'dong bao hiem' THEN 8
                        WHEN savingType = 'du lich' THEN 9
                        WHEN savingType = 'tra no' THEN 10
                    END AS typeID,
                    createDate, expire, period, rate
                    FROM {table}
                    ORDER BY savingID
                 """
    return sql_query

# Lấy dữ liệu cho table moneytransaction
def query_get_moneytransaction(table):

    # Tạo truy vấn SQL
    sql_query = f"""
                    SELECT transID, fromBankAccount, toBankAccount, amount, method, status, surplus, fees,
                    CASE 
                        WHEN savingType = 'mua sam' THEN 1
                        WHEN savingType = 'mua nha' THEN 2
                        WHEN savingType = 'thanh toan hoa don' THEN 3
                        WHEN savingType = 'thanh toan hoc phi' THEN 4
                        WHEN savingType = 'thanh toan luong' THEN 5
                        WHEN savingType = 'mua co phieu' THEN 6
                        WHEN savingType = 'tu thien' THEN 7
                        WHEN savingType = 'dong bao hiem' THEN 8
                        WHEN savingType = 'du lich' THEN 9
                        WHEN savingType = 'tra no' THEN 10
                    END AS typeID,  
                    content, createDate
                    FROM {table}
                    ORDER BY transID
                 """
    return sql_query