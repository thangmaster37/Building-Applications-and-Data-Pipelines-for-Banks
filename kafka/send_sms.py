import boto3
from pathlib import Path
import configparser

# Setting configurations. Look config.cfg for more details
config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.cfg"))

client = boto3.client('sns',
                      aws_access_key_id=config.get('AWS_SNS', 'AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=config.get('AWS_SNS', 'AWS_SECRET_ACCESS_KEY'),
                      region_name=config.get('AWS_SNS', 'REGION_NAME'))

def warning():
    client.publish(
        TopicArn='arn:aws:sns:us-east-1:891377140997:banking_announcement',
        Message='Cảnh báo: Dường như phát hiện gian lận trong giao dịch của bạn.'
    )


