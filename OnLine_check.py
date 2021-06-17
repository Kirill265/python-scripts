import schedule
import time
from check_service import check_all

def check():
    Report = check_all()
    return Report

schedule.every(10).minutes.do(check)

while True:
    schedule.run_pending()
    time.sleep(1)
