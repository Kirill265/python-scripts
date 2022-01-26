import requests
import sys
import os
import shutil
import calendar
import pandas as pd
import datetime
from datetime import timedelta
import pymysql
from pymysql.cursors import DictCursor

connection = pymysql.connect(
    host='',
    port=
    user='',
    password='',
    db='mt5ticks',
    charset='utf8mb4',
    cursorclass=DictCursor
)
pass_dict = {}
daterange = pd.date_range('2019-01-01','2021-03-31')
Symbols_available = ['AUDCADrfd','AUDCHFrfd','AUDJPYrfd','AUDNZDrfd','AUDUSDrfd','CHFJPYrfd','EURAUDrfd','EURCADrfd','EURCHFrfd','EURDKKrfd','EURGBPrfd','EURJPYrfd','EURNOKrfd','EURNZDrfd','EURRUBrfd','EURSEKrfd','EURUSDrfd','GBPAUDrfd','GBPCADrfd','GBPCHFrfd','GBPJPYrfd','GBPNZDrfd','GBPUSDrfd','NZDUSDrfd','USDCADrfd','USDCHFrfd','USDDKKrfd','USDJPYrfd','USDMXNrfd','USDNOKrfd','USDRUBrfd','USDSEKrfd','USDSGDrfd','USDZARrfd']
with connection.cursor() as cursor:
    for date in daterange:
        date_utc = date-timedelta(hours=3)
        query = """
                SELECT * FROM tick WHERE QUOTE_AT_MOMENT(timestamp, '"""+str(date_utc)+"""') ORDER BY symbol;
        """
        cursor.execute(query)
        ticks = cursor.fetchall()
        for tick in ticks:
            if tick["symbol"] in Symbols_available and calendar.weekday(date_utc.year, date_utc.month, date_utc.day) in [0,1,2,3,4] and (str(tick["timestamp"]).split(" ")[0] != str(date_utc).split(" ")[0] or str(tick["timestamp"]).split(" ")[-1].split(":")[0] != '20' or str(tick["timestamp"]).split(" ")[-1].split(":")[1][0] != '5'):
            #if len(tick["symbol"]) == 9 and (str(tick["timestamp"]).split(" ")[0] != str(date-timedelta(days=1)).split(" ")[0] or str(tick["timestamp"]).split(" ")[-1].split(":")[0] != '23'):
                if tick["symbol"] not in pass_dict:
                    pass_dict[tick["symbol"]] = [str(date_utc) + '\t' + str(tick["timestamp"])]
                else:
                    pass_dict[tick["symbol"]].append(str(date_utc) + '\t' + str(tick["timestamp"]))
direction = os.path.dirname(os.path.abspath(__file__))+'\\'
direction = os.path.join(direction, 'result_ticks')
if os.path.exists(direction):
    shutil.rmtree(direction)
os.mkdir(direction)
for symbol in pass_dict:
    with open(direction+'\\'+symbol+'.txt','w',encoding='utf-8') as by_symb:
        for line in pass_dict[symbol]:
            by_symb.write(symbol + '\t' + line + '\n')
