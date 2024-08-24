import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[1]}/warehouse_config.cfg"))

# Setup configs
schema = config.get('WAREHOUSE', 'SCHEMA')

# Setup Staging Schema
create_warehouse_schema = "CREATE SCHEMA IF NOT EXISTS {};".format(schema)

create_credithistory_table = """
    CREATE TABLE IF NOT EXISTS {}.credithistory(
        citizenID VARCHAR(50) PRIMARY KEY NOT NULL,
        mortdue DECIMAL(10,2) NOT NULL,
        value DECIMAL(10,2) NOT NULL,
        derog DECIMAL(10, 0) NOT NULL,
        delinq DECIMAL(10, 2) NOT NULL,
        clage DECIMAL(10, 5) NOT NULL,
        ninq DECIMAL(10, 0) NOT NULL,
        clno DECIMAL(10, 0) NOT NULL,
        debtinc DECIMAL(10, 5) NOT NULL
    );
""".format(schema)

create_profileuser_table = """
    CREATE TABLE IF NOT EXISTS {0}.profileuser(
        profileID BIGINT PRIMARY KEY NOT NULL,
        firstname VARCHAR(20) NOT NULL,
        middlename VARCHAR(20) NOT NULL,
        lastname VARCHAR(20) NOT NULL,
        gender VARCHAR(20) NOT NULL,
        ward VARCHAR(100) NOT NULL,
        district VARCHAR(100) NOT NULL,
        city VARCHAR(100) NOT NULL,
        dateOfBirth DATE NOT NULL,
        citizenID VARCHAR(20) NOT NULL,
        CONSTRAINT fk_citizenID FOREIGN KEY(citizenID) REFERENCES {0}.credithistory(citizenID)
    );
""".format(schema)

create_accountinfo_table = """
    CREATE TABLE IF NOT EXISTS {0}.accountinfo(
        userID BIGINT PRIMARY KEY NOT NULL,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(50) NOT NULL,
        status INTEGER NOT NULL,
        profileID INTEGER NOT NULL,
        createDate TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        CONSTRAINT fk_profile FOREIGN KEY(profileID) REFERENCES {0}.profileuser(profileID)
    );
""".format(schema)

create_accountpayment_table = """
    CREATE TABLE IF NOT EXISTS {0}.accountpayment(
        accountPayID VARCHAR(50) PRIMARY KEY NOT NULL,
        userID INTEGER NOT NULL,
        bankID INTEGER NOT NULL,
        surplus DECIMAL(12, 2) NOT NULL,
        status INTEGER NOT NULL,
        createDate TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES {0}.accountinfo(userID),
        CONSTRAINT fk_bank FOREIGN KEY(bankID) REFERENCES {0}.bank(bankID)
    );
""".format(schema)

create_moneytransaction_table = """
    CREATE TABLE IF NOT EXISTS {0}.moneytransaction(
        transID BIGINT PRIMARY KEY NOT NULL,
        fromBankAccount VARCHAR(50) NOT NULL,
        toBankAccount VARCHAR(50) NOT NULL,
        amount DECIMAL(12, 2) NOT NULL,
        method VARCHAR(20) NOT NULL,
        status VARCHAR(50) NOT NULL,
        surplus DECIMAL(12,2) NOT NULL,
        fees DECIMAL(7, 2) NOT NULL,
        typeID INTEGER NOT NULL,
        content VARCHAR(255) NOT NULL,
        createDate TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        CONSTRAINT fk_fromaccount FOREIGN KEY(fromBankAccount) REFERENCES {0}.accountpayment(accountPayID),
        CONSTRAINT fk_toaccount FOREIGN KEY(toBankAccount) REFERENCES {0}.accountpayment(accountPayID),
        CONSTRAINT fk_type_tracsaction FOREIGN KEY(typeID) REFERENCES {0}.payment_type(typeID)
    );
""".format(schema)

create_loan_table = """
    CREATE TABLE IF NOT EXISTS {0}.loan(
        loanID BIGINT PRIMARY KEY NOT NULL,
        accountPayID VARCHAR(50) NOT NULL,
        loan INTEGER NOT NULL,
        reason VARCHAR(50) NOT NULL,
        job VARCHAR(50) NOT NULL,
        yoj DECIMAL(4, 2) NOT NULL,
        createDate TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        expire TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        period VARCHAR(50) NOT NULL,
        rate DECIMAL(4,1) NOT NULL,
        status VARCHAR(50),
        bad INTEGER,
        paymentDate TIMESTAMP WITHOUT TIME ZONE,
        CONSTRAINT fk_account_loan FOREIGN KEY(accountPayID) REFERENCES {0}.accountpayment(accountPayID)
    );
""".format(schema)

create_savingdeposit_table = """
    CREATE TABLE IF NOT EXISTS {0}.savingdeposit(
        savingID BIGINT PRIMARY KEY NOT NULL,
        accountPayID VARCHAR(50) NOT NULL,
        money DECIMAL(12, 2) NOT NULL,
        status VARCHAR(50) NOT NULL,
        typeID INTEGER NOT NULL,
        createDate TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        expire TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        period VARCHAR(50) NOT NULL,
        rate DECIMAL(4,1) NOT NULL,
        CONSTRAINT fk_account_saving FOREIGN KEY(accountPayID) REFERENCES {0}.accountpayment(accountPayID),
        CONSTRAINT fk_type_saving FOREIGN KEY(typeID) REFERENCES {0}.payment_type(typeID)
    );
""".format(schema)

create_warehouse_tables = [create_warehouse_schema,
                           create_credithistory_table,
                           create_profileuser_table,
                           create_accountinfo_table,
                           create_accountpayment_table,
                           create_moneytransaction_table,
                           create_loan_table,
                           create_savingdeposit_table]

