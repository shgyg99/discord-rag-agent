import logging
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            log_record['timestamp'] = datetime.utcnow().isoformat()
            log_record['logger'] = record.name
            log_record['level'] = record.levelname
            if hasattr(record, 'user_id'):
                log_record['user_id'] = record.user_id
            if hasattr(record, 'latency_ms'):
                log_record['latency_ms'] = record.latency_ms
            if hasattr(record, 'query'):
                log_record['query'] = record.query

    # File handler
    log_file = os.path.join('logs', f'{name}.log')
    os.makedirs('logs', exist_ok=True)
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s'))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
