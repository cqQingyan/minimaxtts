import logging
import json
import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'line': record.lineno
        }

        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)
