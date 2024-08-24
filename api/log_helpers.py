import logging
import uuid

def create_log_id():
    # Tạo một UUID ngẫu nhiên
    new_uuid = uuid.uuid4()

    # Chuyển đổi UUID thành chuỗi và định dạng lại
    new_request_id = str(new_uuid).split("-")
    formatted_request_id = f"{new_request_id[0]}-{new_request_id[1][2:6]}-{new_request_id[1][6:10]}{new_request_id[2][:4]}-{new_request_id[4]}"
    return str(formatted_request_id)


# Hàm để log thông điệp với levelname là "START"
def log_start_message(logger, message):
    logger.log(logging.INFO, "START " + message)


# Hàm để log thông điệp với levelname là "END"
def log_end_message(logger, message):
    logger.log(logging.INFO, "END " + message)


# Hàm để log thông điệp với levelname là "REPORT"
def log_report_message(logger, message):
    logger.log(logging.INFO, "REPORT " + message)