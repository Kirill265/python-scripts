import sys
import os
import shutil
import requests
import time
from keepass import key_pass
import httplib2
from httplib2 import ServerNotFoundError, RedirectMissingLocation, RedirectLimit, RelativeURIError, FailedToDecompressContent, UnimplementedHmacDigestAuthOptionError, UnimplementedDigestAuthOptionError, HttpLib2Error
import ssl
import pymysql
from pymysql.cursors import DictCursor
import datetime
import calendar
from datetime import timedelta, date, time
import MetaTrader5 as mt5
import json
import re
from Telegram_alert import telega_alert
import psutil
import win32com.client

site_for_check=["alfaforex.ru","alfaforex.ru/open-account","my.alfaforex.ru/login",
                "office.alfaforex.ru/login","team.alfaforex.com","tw.alfaforex.ru",
                "alfaforex.ru/chat"]

def tics(symbol: str, now, name = ""):
    try:
        if name != "":
            ticks = mt5.copy_ticks_range(symbol, now - timedelta(minutes = 15), now, mt5.COPY_TICKS_ALL)
            if len(ticks) != 0:
                last_tick = datetime.datetime.fromtimestamp(ticks[-1][0]).strftime('%Y-%m-%d %H:%M:%S')
                #last_ = datetime.datetime.fromtimestamp(ticks[-1][0])
                return '\n'+symbol+': '+str(last_tick)
            else:
                return '\n'+symbol+': за последние 15 минут котировок нет'
        else:
            Report_ticks = ''
            for i in reversed(range(5)):
                from_time = now - timedelta(minutes = i+1)
                to_time = now - timedelta(minutes = i)
                if not ((to_time.hour == 23 and to_time.minute > 50) or (to_time.hour == 0 and to_time.minute < 10)):
                    ticks = mt5.copy_ticks_range(symbol, from_time, to_time, mt5.COPY_TICKS_ALL)
                    if len(ticks) == 0:
                        Report_ticks += '\n'+symbol+': нет котировок за '+str(from_time.time()).split('.')[0]+' - '+str(to_time.time()).split('.')[0]
            return Report_ticks
    except:
        return '\n\nОшибка в функции *tics* для: '+symbol

def check_site(site: str, name = ""):
    try:
        http = httplib2.Http()
        try:
            response = http.request("https://"+site, 'HEAD')
            if response[0]["status"] != '200':
                Report = '['+site+'](https://'+site+') - '+response[0]["status"]
                telega_alert(Report+'\n\n#site')
                return Report
            return '['+site+'](https://'+site+') - '+response[0]["status"]
        except ssl.SSLCertVerificationError:
            Report = '['+site+'](https://'+site+') - '+'Certificate Error'
            telega_alert(Report+'\n\n#site')
            return Report
        except AttributeError:
            Report = '['+site+'](https://'+site+') - '+'SSL Error'
            telega_alert(Report+'\n\n#site')
            return Report
        except TimeoutError:
            Report = '['+site+'](https://'+site+') - '+'Timeout Error'
            telega_alert(Report+'\n\n#site')
            return Report
        except httplib2.RedirectMissingLocation:
            Report = '['+site+'](https://'+site+') - '+'RedirectMissingLocation Error'
            telega_alert(Report+'\n\n#site')
            return Report
        except httplib2.RedirectLimit:
            Report = '['+site+'](https://'+site+') - '+'RedirectLimit Error'
            telega_alert(Report+'\n\n#site')
            return Report
        except httplib2.ServerNotFoundError:
            Report = '['+site+'](https://'+site+') - '+'ServerNotFound Error'
            telega_alert(Report+'\n\n#site')
            return Report
        except httplib2.RelativeURIError:
            Report = '['+site+'](https://'+site+') - '+'RelativeURI Error'
            return Report
        except httplib2.FailedToDecompressContent:
            Report = '['+site+'](https://'+site+') - '+'Decompression algorithm failed'
            return Report
        except httplib2.UnimplementedHmacDigestAuthOptionError:
            Report = '['+site+'](https://'+site+') - '+'Uknown HMACDigest authentication'
            return Report
        except httplib2.UnimplementedDigestAuthOptionError:
            Report = '['+site+'](https://'+site+') - '+'Uknown Digest authentication'
            return Report
        except httplib2.HttpLib2Error:
            Report = '['+site+'](https://'+site+') - '+'HttpLib2 Error'
            return Report
    except:
        Report = '\n\nОшибка в функции *check_site* для: '+site
        return Report

def check_sites(name = ""):
    try:
        Report = ''
        for site_check in site_for_check:
            Report += check_site(site_check,name) + '\n'
        return Report
    except:
        return '\n\nОшибка в функции *check_sites*'
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
    try:
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
            Report = 'Регистрация больше часа назад:\n'+str(last_date)
            telega_alert(Report+'\n\n#customer')
            return Report
        return 'Последняя регистрация:\n'+str(last_date)
    except:
        return '\n\nОшибка в функции *check_customer*'

def check_account(name = ""):
    try:
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
                    FROM account
                    ;
            """
            cursor.execute(query)
            max_account = cursor.fetchone()
            last_date = max_account["date"]
        connection.close()
        if last_date <= now - timedelta(hours = 1):
            Report = 'Счет создан больше часа назад:\n'+str(last_date)
            telega_alert(Report+'\n\n#account')
            return Report
        return 'Последнее создание счета:\n'+str(last_date)
    except:
        return '\n\nОшибка в функции *check_account*'

def check_communication(name = ""):
    try:
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
                    FROM communication
                    ;
            """
            cursor.execute(query)
            max_comm = cursor.fetchone()
            last_date = max_comm["date"]
        connection.close()
        if last_date <= now - timedelta(hours = 1):
            Report = 'Коммуникация больше часа назад:\n'+str(last_date)
            telega_alert(Report+'\n\n#communication')
            return Report
        return 'Последняя коммуникация:\n'+str(last_date)
    except:
        return '\n\nОшибка в функции *check_communication*'

def check_mt(name = ""):
    try:
        now = datetime.datetime.now()
        Symbols = ['EURCADrfd','EURRUBrfd','EURUSDrfd','GBPCHFrfd','GBPUSDrfd','NZDUSDrfd','USDCADrfd','USDCHFrfd','USDJPYrfd','USDRUBrfd','AUDUSDrfd','EURGBPrfd','USDZARrfd','AUDCADrfd','EURJPYrfd','GBPJPYrfd','EURCHFrfd','EURNOKrfd','USDMXNrfd','USDNOKrfd','AUDCHFrfd','AUDJPYrfd','AUDNZDrfd','CHFJPYrfd','EURAUDrfd','EURNZDrfd','GBPAUDrfd','GBPCADrfd','GBPNZDrfd']
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"MT5_eng_works.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        work_from = re.split(r'[^0-9]', data["from"][0])
        work_to = re.split(r'[^0-9]', data["to"][0])
        eng_from = datetime.datetime.combine(date(int(work_from[0]),int(work_from[1]),int(work_from[2])), time(int(work_from[3]),int(work_from[4])))
        eng_to = datetime.datetime.combine(date(int(work_to[0]),int(work_to[1]),int(work_to[2])), time(int(work_to[3]),int(work_to[4])))
        Report = ''
        if now >= eng_from and now <= eng_to:
            if name != "":
                return 'Технические работы на МТ5'
        else:
            Account = 'MT5 Account EUR'
            alias=key_pass(Account).url
            user=int(key_pass(Account).username)
            password=key_pass(Account).password
            if not mt5.initialize(login=user, server=alias, password=password):
                Report += 'Ошибка подключения МТ5:\nInitialize() failed, error code = '+str(mt5.last_error())
                mt5.shutdown()
            else:
                connect = mt5.terminal_info().connected
                if connect != True:
                    Report += '\nНет подключения к МТ5'
                trade = mt5.account_info().trade_allowed
                if trade != True:
                    Report += '\nНе разрешена торговля для ТС в МТ5'
                if Report == '':
                    Report += 'С подключением к МТ5 все ОК!'
                wday = calendar.weekday(now.year, now.month, now.day)
                if wday not in [5,6]:
                    if name != "":
                        Report += '\n\nПоследние котировки:'
                    for symb in Symbols:
                        Report += tics(symb, now, name)
                mt5.shutdown()
        if Report != 'С подключением к МТ5 все ОК!' and name == "":
            telega_alert(Report+'\n\n#mt5')
            return Report
        return Report
    except:
        return '\n\nОшибка в функции *check_mt5*'

def check_all(name = ""):
    try:
        Report = ''
        Report += check_customer(name) + '\n\n'
        Report += check_communication(name) + '\n\n'
        Report += check_account(name) + '\n\n'
        Report += check_sites(name) + '\n\n'
        Report += check_mt(name)
        return Report
    except:
        return '\n\nОшибка в функции *check_all*'

def check_script(scriptName, name = ""):
    try:
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if ("python" in p.name()):
                for item in p.cmdline():
                    if (scriptName in item):
                        return '\n\nScript: '+scriptName + '\nStatus: Running'
        return 'Script: '+scriptName + '\nStatus: Disabled'
    except:
        return 'Ошибка в функции *check_script*'

def check_task(taskName, name = ""):
    try:
        TASK_ENUM_HIDDEN = 1
        TASK_STATE = {0: 'Unknown',
                      1: 'Disabled',
                      2: 'Queued',
                      3: 'Ready',
                      4: 'Running'}

        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()

        folders = [scheduler.GetFolder('\\')]
        while folders:
            folder = folders.pop(0)
            folders += list(folder.GetFolders(0))
            tasks = list(folder.GetTasks(TASK_ENUM_HIDDEN))
            for task in tasks:
                settings = task.Definition.Settings
                if taskName in task.Name:
                    return 'Task: ' + str(task.Name) + '\nState: ' + str(TASK_STATE[task.State]) + '\nLast Run: ' + str(task.LastRunTime)
            return taskName + ' не найден.'
    except:
        return 'Ошибка в функции *check_task*'

def check_monitoring(name = ""):
    try:
        Report = ''
        Report += check_task('AF_Monitoring', name) + '\n\n'
        Report += check_script('OnLine_check', name)
        return Report
    except:
        return 'Ошибка в функции *check_monitoring*' 
