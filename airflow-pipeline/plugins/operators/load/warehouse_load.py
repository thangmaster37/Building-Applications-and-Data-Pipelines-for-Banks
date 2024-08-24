import configparser
from pathlib import Path
from helpers.getYesterday import getYesterday

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[1]}/warehouse_config.cfg"))

# Setup configs
schema = config.get('WAREHOUSE', 'SCHEMA')
s3_zone = 's3://' + config.get('BUCKET', 'S3_ZONE')
iam_role = config.get('IAM_ROLE', 'ARN')

yesterday = getYesterday()


copy_profileuser_table = """
COPY {0}.profileuser
FROM '{1}/profileuser/{3}.csv'
IAM_ROLE '{2}'
FORMAT AS CSV
DELIMITER ','
QUOTE '"'
NULL AS  '\\000'
IGNOREHEADER 1
;
""".format(schema, s3_zone, iam_role, yesterday)

copy_accountinfo_table = """
COPY {0}.accountinfo
FROM '{1}/accountinfo/{3}.csv'
IAM_ROLE '{2}'
FORMAT AS CSV
DELIMITER ','
QUOTE '"'
NULL AS  '\\000'
IGNOREHEADER 1
;
""".format(schema, s3_zone, iam_role, yesterday)

copy_accountpayment_table = """
COPY {0}.accountpayment
FROM '{1}/accountpayment/{3}.csv'
IAM_ROLE '{2}'
FORMAT AS CSV
DELIMITER ','
QUOTE '"'
NULL AS  '\\000'
IGNOREHEADER 1
;
""".format(schema, s3_zone, iam_role, yesterday)

copy_moneytransaction_table = """
COPY {0}.moneytransaction
FROM '{1}/moneytransaction/{3}.csv'
IAM_ROLE '{2}'
FORMAT AS CSV
DELIMITER ','
QUOTE '"'
NULL AS  '\\000'
IGNOREHEADER 1
;
""".format(schema, s3_zone, iam_role, yesterday)

copy_loan_table = """
COPY {0}.loan
FROM '{1}/loan/{3}.csv'
IAM_ROLE '{2}'
FORMAT AS CSV
DELIMITER ','
QUOTE '"'
NULL AS  '\\000'
IGNOREHEADER 1
;
""".format(schema, s3_zone, iam_role, yesterday)

copy_savingdeposit_table = """
COPY {0}.savingdeposit
FROM '{1}/savingdeposit/{3}.csv'
IAM_ROLE '{2}'
FORMAT AS CSV
DELIMITER ','
QUOTE '"'
NULL AS  '\\000'
IGNOREHEADER 1
;
""".format(schema, s3_zone, iam_role, yesterday)

copy_warehouse_tables = [copy_profileuser_table,
                         copy_accountinfo_table,
                         copy_accountpayment_table,
                         copy_moneytransaction_table,
                         copy_loan_table,
                         copy_savingdeposit_table]