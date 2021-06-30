import sys
import os
import schedule
import time
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from check_service import check_all

def check():
    Report = check_all()
    return Report

schedule.every(10).minutes.do(check)

while True:
    schedule.run_pending()
    time.sleep(1)
