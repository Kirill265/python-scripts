import requests
import time
from keepass import key_pass
import httplib2
import ssl
import pymysql
from pymysql.cursors import DictCursor
import datetime
import calendar
from datetime import timedelta
import MetaTrader5 as mt5

def tics(symbol: str, Report: str, name = ""):
    ticks = mt5.copy_ticks_range(symbol, now - timedelta(minutes = 15), now, mt5.COPY_TICKS_ALL)
    last_tick = datetime.datetime.fromtimestamp(ticks[-1][0]).strftime('%Y-%m-%d %H:%M:%S')
    last_ = datetime.datetime.fromtimestamp(ticks[-1][0])
    if last_ <= now - timedelta(minutes = 1):
        Report += """
Последняя котировка """+symbol+""" больше минуты назад:
    """+str(last_tick)
    if last_ >= now - timedelta(minutes = 1) and name != "":
        Report += """
Последняя котировка """+symbol+""":
    """+str(last_tick)
    return Report

def check_site(site: str, name = ""):
    http = httplib2.Http()
    try:
        response = http.request("https://"+site, 'HEAD')
        if response[0]["status"] != '200':
            Report = "["+site+"](https://"+site+") - "+response[0]["status"]
            telega_alert(Report)
        if response[0]["status"] == '200' and name != "":
            Report = "["+site+"](https://"+site+") - "+response[0]["status"]
            print(Report)
            #telega_alert(Report)
    except ssl.SSLCertVerificationError:
        Report = "["+site+"](https://"+site+") - "+"Certificate Error"
        telega_alert(Report)
    except AttributeError:
        Report = "["+site+"](https://"+site+") - "+"SSL Error"
        telega_alert(Report)
    except TimeoutError:
        Report = "["+site+"](https://"+site+") - "+"Timeout Error"
        telega_alert(Report)
    except:
        Report = "["+site+"](https://"+site+") - "+"unknown Error"
        telega_alert(Report)

def check_sites(name = ""):
    check_site("alfaforex.ru",name)
    check_site("alfaforex.ru/open-account",name)
    check_site("my.alfaforex.ru/login",name)
    check_site("office.alfaforex.ru/login",name)
    check_site("team.alfaforex.com",name)
    check_site("tw.alfaforex.ru",name)
    check_site("alfaforex.ru/chat",name)
'''
site = "https://alfaforex.ru/"
site = "https://alfaforex.ru/open-account/"
site = "https://my.alfaforex.ru/login"
site = "https://office.alfaforex.ru/login"
site = "https://team.alfaforex.com/"
site = "https://tw.alfaforex.ru/"
site = "https://alfaforex.ru/chat/"
'''

def check_customer(name = ""):
    now = datetime.datetime.now()
    SQL_DB = 'MySQL DB PROD'
    connection = pymysql.connect(
        host=key_pass(SQL_DB).url[:-5],
        port=int(key_pass(SQL_DB).url[-4:]),
        user=key_pass(SQL_DB).username,
        password=key_pass(SQL_DB).password,
        db='my',
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    with connection.cursor() as cursor:
        query = """
                SET @@time_zone = \"+3:00\";
        """
        cursor.execute(query)
        query = """
                SELECT MAX(created_at) as 'date'
                FROM customer
                ;
        """
        cursor.execute(query)
        max_customer = cursor.fetchone()
        last_date = max_customer["date"]
    connection.close()
    if last_date <= now - timedelta(hours = 1):
        Report = """Последняя регистрация больше часа назад:
"""+str(last_date)
        telega_alert(Report)
    if last_date >= now - timedelta(hours = 1) and name != "":
        Report = """Последняя регистрация:
"""+str(last_date)
        telega_alert(Report)

def check_communication(name = ""):
    now = datetime.datetime.now()
    SQL_DB = 'MySQL DB PROD'
    connection = pymysql.connect(
        host=key_pass(SQL_DB).url[:-5],
        port=int(key_pass(SQL_DB).url[-4:]),
        user=key_pass(SQL_DB).username,
        password=key_pass(SQL_DB).password,
        db='my',
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    with connection.cursor() as cursor:
        query = """
                SET @@time_zone = \"+3:00\";
        """
        cursor.execute(query)
        query = """
                SELECT MAX(created_at) as 'date'
                FROM comminication
                ;
        """
        cursor.execute(query)
        max_comm = cursor.fetchone()
        last_date = max_comm["date"]
    connection.close()
    if last_date <= now - timedelta(hours = 1):
        Report = """Последняя коммуникация больше часа назад:
"""+str(last_date)
        telega_alert(Report)
    if last_date >= now - timedelta(hours = 1) and name != "":
        Report = """Последняя коммуникация:
"""+str(last_date)
        telega_alert(Report)

def check_mt(name = "")
    now = datetime.datetime.now()
    Report = ""

    try:
        if not mt5.initialize(login=1000005037, server="AlfaForexRU-Real",password="KirillAF1701"):
            Report += """Ошибка подключения МТ5:
Initialize() failed, error code = """+str(mt5.last_error())
            mt5.shutdown()
        
        connect = mt5.terminal_info().connected
        if connect != True:
            Report += """
Нет подключения к МТ5"""
        trade = mt5.account_info().trade_allowed
        if trade != True:
            Report += """
Не разрешена торговля для ТС в МТ5"""
        if Report == """""":
            Report += """С подключением к МТ5 все ОК"""
        
        Report = tics('EURCADrfd',Report, name)
        Report = tics('EURRUBrfd',Report, name)
        Report = tics('EURUSDrfd',Report, name)
        Report = tics('GBPCHFrfd',Report, name)
        Report = tics('GBPUSDrfd',Report, name)
        Report = tics('NZDUSDrfd',Report, name)
        Report = tics('USDCADrfd',Report, name)
        Report = tics('USDCHFrfd',Report, name)
        Report = tics('USDJPYrfd',Report, name)
        Report = tics('USDRUBrfd',Report, name)
        Report = tics('AUDUSDrfd',Report, name)
        Report = tics('EURGBPrfd',Report, name)
        Report = tics('USDZARrfd',Report, name)
        Report = tics('AUDCADrfd',Report, name)
        Report = tics('EURJPYrfd',Report, name)
        Report = tics('GBPJPYrfd',Report, name)
        Report = tics('EURCHFrfd',Report, name)
        Report = tics('EURNOKrfd',Report, name)
        Report = tics('USDMXNrfd',Report, name)
        Report = tics('USDNOKrfd',Report, name)
        Report = tics('AUDCHFrfd',Report, name)
        Report = tics('AUDJPYrfd',Report, name)
        Report = tics('AUDNZDrfd',Report, name)
        Report = tics('CHFJPYrfd',Report, name)
        Report = tics('EURAUDrfd',Report, name)
        Report = tics('EURNZDrfd',Report, name)
        Report = tics('GBPAUDrfd',Report, name)
        Report = tics('GBPCADrfd',Report, name)
        Report = tics('GBPNZDrfd',Report, name)
        
        mt5.shutdown()
    except:
        Report += """Ошибка подключения МТ5"""
        
    if Report != """С подключением к МТ5 все ОК""":
        telega_alert(Report)
