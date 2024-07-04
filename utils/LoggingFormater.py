import logging
import json

class MultilineJSONFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, dict):
            record.msg = json.dumps(record.msg, indent=4)
        return super().format(record)
    
    def format_message(self, msg):
        return json.dumps(msg, indent=4)