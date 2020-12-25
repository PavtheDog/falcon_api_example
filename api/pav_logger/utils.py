import os
import calendar
from datetime import datetime,timedelta, timezone

def get_app_base_path():
    return os.path.abspath(os.path.dirname(__file__))

def check_and_create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

def get_current_unix_time():
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    return (str(unixtime))