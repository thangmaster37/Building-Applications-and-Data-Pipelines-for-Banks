CREATE TABLE IF NOT EXISTS payment_type(
    typeID SERIAL PRIMARY KEY NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL
);

INSERT INTO payment_type(name, description)
VALUES 
      ('mua sắm', 'sử dụng tiền để tri trả các khoản phí khi đi mua sắm hàng hóa'),
      ('mua nhà', 'sử dụng tiền để tri trả các khoản phí khi mua nhà'),
      ('thanh toán hóa đơn', 'sử dụng tiền để thanh toán hóa đơn'),
      ('thanh toán học phí', 'sử dụng để thanh toán học phí'),
      ('thanh toán lương', 'sử dụng để trả lương cho các nhân viên'),
      ('mua cổ phiếu', 'sử dụng để đầu tư cổ phiếu'),
      ('từ thiện', 'sử dụng cho việc từ thiện'),
      ('đóng bảo hiểm', 'sử dụng để đóng tiền bảo hiểm'),
      ('du lịch', 'sử dụng thanh toán cho phí du lịch nghỉ dưỡng'),
      ('trả nợ', 'sử dụng để trả nợ');


CREATE TABLE IF NOT EXISTS bank(
    bankID SERIAL PRIMARY KEY NOT NULL,
    bankName VARCHAR(100) NOT NULL,
    aliasName VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    status INTEGER NOT NULL,
    dateOfEstablishment DATE NOT NULL
);

INSERT INTO bank(bankName, aliasName, description, status, dateOfEstablishment)
VALUES 
      ('NHTMCP Quân đội', 'MBBank', 'Ngân hàng', 1, '2000-01-02'),
      ('NHTMCP VN Thịnh Vượng', 'VPBank', 'Ngân hàng', 1, '2001-01-02'),
      ('NHTMCP Kỹ thương', 'TechcomBank', 'Ngân hàng', 1, '2002-01-02'),
      ('Ngân hàng Ngoại thương Việt Nam', 'VietcomBank', 'Ngân hàng', 1, '2002-05-02'),
      ('Ngân hàng Đầu tư và Phát triển VN', 'BIDV', 'Ngân hàng', 1, '2003-07-03'),
      ('Ngân hàng Công thương VN', 'VietinBank', 'Ngân hàng', 1, '2004-05-06'),
      ('Ngân hàng Nông nghiệp và Phát triển Nông thôn VN', 'AgriBank', 'Ngân hàng', 1, '2005-07-23'),
      ('NHTMCP Quốc tế', 'VIB', 'Ngân hàng', 1, '1995-11-24'),
      ('NHTMCP Á châu', 'ACB', 'Ngân hàng', 1, '2001-10-15'),
      ('NHTMCP Sài Gòn - Hà Nội', 'SHB', 'Ngân hàng', 1, '2006-04-29'),
      ('NHTMCP SG Công Thương', 'SaigonBank', 'Ngân hàng', 1, '2001-06-12'),
      ('NHTMCP Sài Gòn', 'SCB', 'Ngân hàng', 1, '1999-12-01'),
      ('NHTMCP Phương Đông', 'OCB', 'Ngân hàng', 1, '1996-01-01'),
      ('NHTMCP Đông Nam Á', 'SeaBank', 'Ngân hàng', 1, '2005-09-18'),
      ('NHTMCP Đại Dương', 'OceanBank', 'Ngân hàng', 1, '2003-12-12'),
      ('NHTMCP Dầu khí Toàn cầu', 'GPBank', 'Ngân hàng', 1, '1990-03-28'),
      ('NHTMCP An Bình', 'ABBank', 'Ngân hàng', 1, '1890-05-12'),
      ('NHTMCP Xăng dầu Petrolimex', 'PGBank', 'Ngân hàng', 1, '2001-06-28'),
      ('NHTMCP phát triển TPHCM', 'HDBank', 'Ngân hàng', 1, '1999-12-09'),
      ('NHTMCP Xuất Nhập Khẩu', 'EximBank', 'Ngân hàng', 1, '2010-05-26');


CREATE TABLE IF NOT EXISTS credithistory(
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


CREATE TABLE IF NOT EXISTS profileuser(
    profileID SERIAL PRIMARY KEY NOT NULL,
    firstname VARCHAR(20) NOT NULL,
    middlename VARCHAR(20) NOT NULL,
    lastname VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    placeOfPermanent VARCHAR(255) NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    dateOfBirth DATE NOT NULL,
    citizenID VARCHAR(20) NOT NULL,
    CONSTRAINT fk_citizenID FOREIGN KEY(citizenID) REFERENCES credithistory(citizenID)
);


CREATE TABLE IF NOT EXISTS accountinfo(
    userID SERIAL PRIMARY KEY NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    status INTEGER NOT NULL,
    profileID INTEGER NOT NULL,
    createDate TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT fk_profile FOREIGN KEY(profileID) REFERENCES profileuser(profileID)
);


CREATE TABLE IF NOT EXISTS accountpayment(
    accountPayID VARCHAR(50) PRIMARY KEY NOT NULL,
    userID INTEGER NOT NULL,
    bankID INTEGER NOT NULL,
    surplus DECIMAL(12, 2) NOT NULL,
    status INTEGER NOT NULL,
    createDate TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY(userID) REFERENCES accountinfo(userID),
    CONSTRAINT fk_bank FOREIGN KEY(bankID) REFERENCES bank(bankID)
);


CREATE TABLE IF NOT EXISTS moneytransaction(
    transID SERIAL PRIMARY KEY NOT NULL,
    fromBankAccount VARCHAR(50) NOT NULL,
    toBankAccount VARCHAR(50) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    method VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL,
    fees DECIMAL(7, 2) NOT NULL,
    surplus DECIMAL(12,2) NOT NULL,
    typeID INTEGER NOT NULL,
    content VARCHAR(255) NOT NULL,
    createDate TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT fk_fromaccount FOREIGN KEY(fromBankAccount) REFERENCES accountpayment(accountPayID),
    CONSTRAINT fk_toaccount FOREIGN KEY(toBankAccount) REFERENCES accountpayment(accountPayID),
    CONSTRAINT fk_type_tracsaction FOREIGN KEY(typeID) REFERENCES payment_type(typeID)
);


CREATE TABLE IF NOT EXISTS loan(
    loanID SERIAL PRIMARY KEY NOT NULL,
    accountPayID VARCHAR(50) NOT NULL,
    loan INTEGER NOT NULL,
    reason VARCHAR(50) NOT NULL,
    job VARCHAR(50) NOT NULL,
    yoj DECIMAL(4, 2) NOT NULL,
    createDate TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    expire TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    period VARCHAR(50) NOT NULL,
    rate DECIMAL(4,1) NOT NULL,
    status VARCHAR(50),
    bad INTEGER,
    score DECIMAL(6,2) NOT NULL,
    CONSTRAINT fk_account_loan FOREIGN KEY(accountPayID) REFERENCES accountpayment(accountPayID)
);


CREATE TABLE IF NOT EXISTS savingdeposit(
    savingID SERIAL PRIMARY KEY NOT NULL,
    accountPayID VARCHAR(50) NOT NULL,
    money DECIMAL(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    typeID INTEGER NOT NULL,
    createDate TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    expire TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    period VARCHAR(50) NOT NULL,
    rate DECIMAL(4,1) NOT NULL,
    CONSTRAINT fk_account_saving FOREIGN KEY(accountPayID) REFERENCES accountpayment(accountPayID),
    CONSTRAINT fk_type_saving FOREIGN KEY(typeID) REFERENCES payment_type(typeID)
);


CREATE TABLE IF NOT EXISTS card(
    cardID SERIAL PRIMARY KEY NOT NULL,
    accountPayID VARCHAR(50) NOT NULL,
    identifyID VARCHAR(20) NOT NULL,
    typeCard VARCHAR(50) NOT NULL,
    status INTEGER NOT NULL,
    issuedOn TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    expire TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    branch VARCHAR(255) NOT NULL,
    CONSTRAINT fk_account_card FOREIGN KEY(accountPayID) REFERENCES accountpayment(accountPayID)
);


