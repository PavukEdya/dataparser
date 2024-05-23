import datetime
from typing import Any


class Validator:

    @staticmethod
    def try_parse_date(value: Any, date_format: str = '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(str(value), date_format)
        except:
            return False
    @staticmethod
    def is_string(value: Any)->bool:
        return isinstance(value,str)
    
