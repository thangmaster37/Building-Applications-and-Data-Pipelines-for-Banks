class AnalyticsQueries:

    """
        Những phân tích được sử dụng trong báo cáo
        1. Lấy ra TOP 3 lí do chuyển khoản nhiều nhất trong một ngày để phục vụ cho việc đưa ra các ưu đãi cho người dùng
        2. Lấy ra các ngân hàng, số lượng tài khoản và số hoạt động hàng ngày và lợi nhuận mà ngân hàng thu được
        3. Thống kê số lượng giao dịch trong 1 tháng gần nhất của những người vỡ nợ
        4. Top 5 những công việc và lí do gây ra vỡ nợ nhiều nhất
        5. Thống kê lí do gửi tiết kiệm, số lượng và tổng số tiền gửi tiết kiệm
    """

    distributed_reason_transaction = """
        SELECT 
            p.name, 
            count(*) as count
        FROM 
            banking.moneytransaction as m,
            banking.payment_type as p
        WHERE 
            DATE(createDate) = CURRENT_DATE AND
            m.typeID = p.typeID
        GROUP BY 
            p.name
        ORDER BY 
            count DESC
        LIMIT 3;
    """

    distributed_bank_transaction = """
        SELECT 
            b.aliasName,
            COUNT(ap.accountPayID) AS account_count,
            COUNT(mt.transID) AS transaction_count,
            SUM(mt.fees) AS profit
        FROM 
            banking.bank b
        LEFT JOIN 
            banking.accountpayment ap ON b.bankID = ap.bankID
        LEFT JOIN 
            banking.moneytransaction mt ON ap.accountPayID = mt.fromBankAccount
        WHERE 
            DATE(mt.createDate) = CURRENT_DATE
        GROUP BY 
            b.aliasName;
    """

    trans_month_default = """
        WITH recent_transactions AS (
            SELECT 
                mt.fromBankAccount AS accountPayID,
                mt.amount,
                mt.createDate
            FROM 
                banking.moneytransaction mt
            WHERE 
                mt.createDate >= CURRENT_DATE - INTERVAL '1 month'
            UNION ALL
            SELECT 
                mt.toBankAccount AS accountPayID,
                mt.amount,
                mt.createDate
            FROM 
                banking.moneytransaction mt
            WHERE 
                mt.createDate >= CURRENT_DATE - INTERVAL '1 month'
        )
        SELECT 
            ap.accountPayID,
            ap.surplus,
            COUNT(rt.amount) AS transaction_count,
            SUM(rt.amount) AS total_transaction_amount
        FROM 
            banking.accountpayment ap
        JOIN 
            banking.loan l ON ap.accountPayID = l.accountPayID
        JOIN 
            recent_transactions rt ON ap.accountPayID = rt.accountPayID
        WHERE 
            l.bad = 1
        GROUP BY 
            ap.accountPayID, ap.surplus
        ORDER BY 
            total_transaction_amount DESC;
    """

    reason_job_default = """
        SELECT 
            l.job,
            l.reason,
            COUNT(*) AS bad_loan_count
        FROM 
            banking.loan l
        WHERE 
            l.bad = 1
        GROUP BY 
            l.job, l.reason
        ORDER BY 
            bad_loan_count DESC
        LIMIT 5;
    """

    statistic_saving = """
        SELECT 
            pm.name,
            COUNT(*) AS total_deposits,
            SUM(sd.money) AS total_money_saving
        FROM 
            banking.savingdeposit sd,
            banking.payment_type pm
        WHERE 
            pm.typeID = sd.typeID
        GROUP BY 
            pm.name
        ORDER BY 
            total_money_saving DESC;
    """





    

    

