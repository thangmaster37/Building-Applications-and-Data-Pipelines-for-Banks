-- Tạo một trigger để nhận biết có record được update trong table loan
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION audit_update()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, old_data, new_data)
    VALUES (TG_TABLE_NAME, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER loan_update_audit
AFTER UPDATE ON loan
FOR EACH ROW EXECUTE FUNCTION audit_update();


-- Tạo một trigger để nhận biết có một record được thêm vào table moneytransaction
CREATE TABLE IF NOT EXISTS transaction_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION audit_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO transaction_log (table_name, operation, old_data, new_data)
    VALUES (TG_TABLE_NAME, 'INSERT', NULL, row_to_json(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER transaction_insert_audit
AFTER INSERT ON moneytransaction
FOR EACH ROW
EXECUTE FUNCTION audit_insert();
