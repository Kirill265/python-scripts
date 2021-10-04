import requests
import sys
import os
import calendar
import pandas as pd
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass

SQL_DB = 'MySQL TICKS PROD'
connection = pymysql.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    db='mt5ticks',
    charset='utf8mb4',
    cursorclass=DictCursor
)
pass_dict = {}
daterange = pd.date_range('2017-01-01','2021-03-31')
Symbols_available = ['AUDCADrfd','AUDCHFrfd','AUDJPYrfd','AUDNZDrfd','AUDUSDrfd','CHFJPYrfd','EURAUDrfd','EURCADrfd','EURCHFrfd','EURDKKrfd','EURGBPrfd','EURJPYrfd','EURNOKrfd','EURNZDrfd','EURRUBrfd','EURSEKrfd','EURUSDrfd','GBPAUDrfd','GBPCADrfd','GBPCHFrfd','GBPJPYrfd','GBPNZDrfd','GBPUSDrfd','NZDUSDrfd','USDCADrfd','USDCHFrfd','USDDKKrfd','USDJPYrfd','USDMXNrfd','USDNOKrfd','USDRUBrfd','USDSEKrfd','USDSGDrfd','USDZARrfd']
with connection.cursor() as cursor:
    for date in daterange:
        query = """
                SELECT * FROM tick WHERE QUOTE_AT_MOMENT(timestamp, '"""+str(date)+"""') ORDER BY symbol;
        """
        cursor.execute(query)
        ticks = cursor.fetchall()
        for tick in ticks:
            if tick["symbol"] in Symbols_available and calendar.weekday(date.year, date.month, date.day) in [1,2,3,4,5] and (str(tick["timestamp"]).split(" ")[0] != str(date-timedelta(days=1)).split(" ")[0] or str(tick["timestamp"]).split(" ")[-1].split(":")[0] != '23' or str(tick["timestamp"]).split(" ")[-1].split(":")[1][0] != '5'):
            #if len(tick["symbol"]) == 9 and (str(tick["timestamp"]).split(" ")[0] != str(date-timedelta(days=1)).split(" ")[0] or str(tick["timestamp"]).split(" ")[-1].split(":")[0] != '23'):
                if tick["symbol"] not in pass_dict:
                    pass_dict[tick["symbol"]] = [str(date-timedelta(days=1)) + '\t' + str(tick["timestamp"])]
                else:
                    pass_dict[tick["symbol"]].append(str(date-timedelta(days=1)) + '\t' + str(tick["timestamp"]))
for symbol in pass_dict:
    for line in pass_dict[symbol]:
        print(symbol + '\t' + line)
