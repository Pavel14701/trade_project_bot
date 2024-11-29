import os, logging, json
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler




def create_logger(logger_name:str) -> logging.Logger:
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.ERROR)
    log_filename = os.path.join('Logs', f'{logger_name}_{datetime.now().strftime("%Y-%m-%d")}.log')
    handler = TimedRotatingFileHandler(
        filename=log_filename, encoding='utf-8', when='midnight',
        interval=1, backupCount=7
    )
    handler.suffix = '%Y-%m-%d'
    if logger_name == 'IventListner':
        handler.setFormatter(MultilineJSONFormatter())
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger


class MultilineJSONFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, dict):
            record.msg = json.dumps(record.msg, indent=4)
        return super().format(record)
    
    def format_message(self, msg):
        return json.dumps(msg, indent=4)