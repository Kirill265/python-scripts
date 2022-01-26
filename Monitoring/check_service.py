import sys
import os
import shutil
import requests
import time
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
import psutil
import win32com.client
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass
from Telegram_alert import telega_alert, edit_message, reply_message, pin_message, unpin_message

site_for_check=["alfaforex.ru",
                "alfaforex.ru/open-account",
                "my.alfaforex.ru/login",
                "office.alfaforex.ru/login",
                "agent.alfaforex.ru/login",
                #"tw.alfaforex.ru",
                "team.alfaforex.com"]

if __name__ == '__main__':
    all_site_for_check=["office.alfaforex.ru/login"]
else:
    all_site_for_check=site_for_check+["alfaforex.ru/trading-terms",
                                   "alfaforex.ru/deposit-withdrawal",
                                   "alfaforex.ru/online-trading",
                                   "alfaforex.ru/metatrader",
                                   "alfaforex.ru/analytics",
                                   "alfaforex.ru/currency-exchange",
                                   "alfaforex.ru/faq",
                                   "alfaforex.ru/agentskaya-programma",
                                   "alfaforex.ru/documents",
                                   "alfaforex.ru/requisites",
                                   "alfaforex.ru/disclosure",
                                   "alfaforex.ru/about",
                                   "alfaforex.ru/news",
                                   "alfaforex.ru/contacts",
                                   "alfaforex.ru/economic-calendar",
                                   "alfaforex.ru/trading-calc",
                                   "alfaforex.ru/analytics/analytics-reviews",
                                   "alfaforex.ru/analytics/analytics-currencies",
                                   "alfaforex.ru/analytics/analytics-rates",
                                   "alfaforex.ru/demo-account",
                                   "alfaforex.ru/analytics/education",
                                   "alfaforex.ru/analytics/education/archive-daily-reviews"]

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
            from_time = now - timedelta(minutes = 5)
            to_time = now
            if not ((to_time.hour == 23 and to_time.minute > 50) or (to_time.hour == 0 and to_time.minute <= 12)):
                ticks = mt5.copy_ticks_range(symbol, from_time, to_time, mt5.COPY_TICKS_ALL)
                if len(ticks) == 0:
                    Report_ticks += '\n'+symbol+': нет котировок за '+str(from_time.time()).split('.')[0]+' - '+str(to_time.time()).split('.')[0]
            return Report_ticks
    except:
        return '\n\nОшибка в функции *tics* для: '+symbol

def check_site(site: str, name = ""):
    try:
        http = httplib2.Http()
        now = datetime.datetime.now()
        if now.hour == 3 and site == "team.alfaforex.com" :
            return ''
        try:
            response = http.request("https://"+site, 'HEAD')
            if not (response[0]["status"] == '200' or ((now.hour == 2 or now.hour == 3 or now.hour == 4 or now.hour == 5) and site == "team.alfaforex.com" and response[0]["status"] == '502')):
                Report = '['+site+'](https://'+site+') - '+response[0]["status"]
                telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
                return Report
            return '['+site+'](https://'+site+') - OK'
        except ssl.SSLCertVerificationError:
            Report = '['+site+'](https://'+site+') - '+'Certificate Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except AttributeError:
            Report = '['+site+'](https://'+site+') - '+'SSL Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except TimeoutError:
            Report = '['+site+'](https://'+site+') - '+'Timeout Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except httplib2.RedirectMissingLocation:
            Report = '['+site+'](https://'+site+') - '+'RedirectMissingLocation Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except httplib2.RedirectLimit:
            Report = '['+site+'](https://'+site+') - '+'RedirectLimit Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except httplib2.ServerNotFoundError:
            Report = '['+site+'](https://'+site+') - '+'ServerNotFound Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
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
        for site_check in all_site_for_check:
            Report += check_site(site_check,name) + '\n'
        return Report
    except:
        return '\n\nОшибка в функции *check_sites*'

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
                    SELECT MAX(id) as 'id', MAX(created_at) as 'date'
                    FROM customer
                    ;
            """
            cursor.execute(query)
            max_customer = cursor.fetchone()
            last_date = max_customer["date"]
        connection.close()
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"monitoring_status.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        if last_date <= now - timedelta(hours = 1):
            Report = 'Регистрация больше часа назад:\n'+str(last_date)
            if data["customer"]["problem_id"] != str(max_customer["id"]):
                response = telega_alert(u'\U000026A0'+' '+Report+'\n\nАктуально на '+str(now.date())+' '+str(now.time()).split('.')[0]+'\n\n#customer')
                pin_message(response.message_id)
                data["customer"]["problem_id"] = str(max_customer["id"])
                data["customer"]["message_id"] = str(response.message_id)
                data["customer"]["text"] = str(Report)
                jFile = open(path, "w")
                jFile.write(json.dumps(data))
                jFile.close()
            else:
                msg_id = data["customer"]["message_id"]
                text = data["customer"]["text"]
                edit_message(msg_id, u'\U000026A0'+text.replace('.','\.').replace('-','\-')+'\n\nАктуально на '+str(now.date()).replace('-','\-')+' '+str(now.time()).split('.')[0]+'\n\n#customer'.replace('#','\#'))
            return Report
        Report = 'Регистрации появились:\n'+str(last_date)
        if data["customer"]["problem_id"] != "0":
            msg_id = data["customer"]["message_id"]
            text = data["customer"]["text"]
            reply_message(msg_id,u'\U00002705'+' '+Report+'\n\n#customer')
            data["customer"]["problem_id"] = "0"
            data["customer"]["message_id"] = "0"
            data["customer"]["text"] = "0"
            jFile = open(path, "w")
            jFile.write(json.dumps(data))
            jFile.close()
            try:
                unpin_message(msg_id)
                edit_message(msg_id,u'\U000026A0'+' ~'+text.replace('.','\.').replace('-','\-')+'~\n\n#customer'.replace('#','\#'))
            except:
                pass
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
                    SELECT MAX(id) as 'id', MAX(created_at) as 'date'
                    FROM account
                    ;
            """
            cursor.execute(query)
            max_account = cursor.fetchone()
            last_date = max_account["date"]
        connection.close()
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"monitoring_status.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        if last_date <= now - timedelta(hours = 2) - timedelta(minutes = 30):
            Report = 'Счет создан больше 2.5 часов назад:\n'+str(last_date)
            if data["account"]["problem_id"] != str(max_account["id"]):
                response = telega_alert(u'\U000026A0'+' '+Report+'\n\nАктуально на '+str(now.date())+' '+str(now.time()).split('.')[0]+'\n\n#account')
                pin_message(response.message_id)
                data["account"]["problem_id"] = str(max_account["id"])
                data["account"]["message_id"] = str(response.message_id)
                data["account"]["text"] = Report
                jFile = open(path, "w")
                jFile.write(json.dumps(data))
                jFile.close()
            else:
                msg_id = data["account"]["message_id"]
                text = data["account"]["text"]
                edit_message(msg_id, u'\U000026A0'+text.replace('.','\.').replace('-','\-')+'\n\nАктуально на '+str(now.date()).replace('-','\-')+' '+str(now.time()).split('.')[0]+'\n\n#account'.replace('#','\#'))
            return Report
        Report = 'Счета создаются:\n'+str(last_date)
        if data["account"]["problem_id"] != "0":
            msg_id = data["account"]["message_id"]
            text = data["account"]["text"]
            reply_message(msg_id,u'\U00002705'+' '+Report+'\n\n#account')
            data["account"]["problem_id"] = "0"
            data["account"]["message_id"] = "0"
            data["account"]["text"] = "0"
            jFile = open(path, "w")
            jFile.write(json.dumps(data))
            jFile.close()
            try:
                unpin_message(msg_id)
                edit_message(msg_id,u'\U000026A0'+' ~'+text.replace('.','\.').replace('-','\-')+'~\n\n#account'.replace('#','\#'))
            except:
                pass
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
                    SELECT MAX(id) as 'id', MAX(created_at) as 'date'
                    FROM communication
                    ;
            """
            cursor.execute(query)
            max_comm = cursor.fetchone()
            last_date = max_comm["date"]
        connection.close()
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"monitoring_status.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        if last_date <= now - timedelta(hours = 2) - timedelta(minutes = 30):
            Report = 'Коммуникация больше 2.5 часов назад:\n'+str(last_date)
            if data["communication"]["problem_id"] != str(max_comm["id"]):
                response = telega_alert(u'\U000026A0'+' '+Report+'\n\nАктуально на '+str(now.date())+' '+str(now.time()).split('.')[0]+'\n\n#communication')
                pin_message(response.message_id)
                data["communication"]["problem_id"] = str(max_comm["id"])
                data["communication"]["message_id"] = str(response.message_id)
                data["communication"]["text"] = Report
                jFile = open(path, "w")
                jFile.write(json.dumps(data))
                jFile.close()
            else:
                msg_id = data["communication"]["message_id"]
                text = data["communication"]["text"]
                edit_message(msg_id, u'\U000026A0'+text.replace('.','\.').replace('-','\-')+'\n\nАктуально на '+str(now.date()).replace('-','\-')+' '+str(now.time()).split('.')[0]+'\n\n#communication'.replace('#','\#'))
            return Report
        Report = 'Коммуникации появились:\n'+str(last_date)
        if data["communication"]["problem_id"] != "0":
            msg_id = data["communication"]["message_id"]
            text = data["communication"]["text"]
            reply_message(msg_id,u'\U00002705'+' '+Report+'\n\n#communication')
            data["communication"]["problem_id"] = "0"
            data["communication"]["message_id"] = "0"
            data["communication"]["text"] = "0"
            jFile = open(path, "w")
            jFile.write(json.dumps(data))
            jFile.close()
            try:
                unpin_message(msg_id)
                edit_message(msg_id,u'\U000026A0'+' ~'+text.replace('.','\.').replace('-','\-')+'~\n\n#communication'.replace('#','\#'))
            except:
                pass
        return 'Последняя коммуникация:\n'+str(last_date)
    except:
        return '\n\nОшибка в функции *check_communication*'

def check_mt(name = ""):
    try:
        now = datetime.datetime.now()
        Symbols = ['AUDCADrfd','AUDCHFrfd','AUDJPYrfd','AUDNZDrfd','AUDUSDrfd','CHFJPYrfd','EURAUDrfd','EURCADrfd','EURCHFrfd','EURDKKrfd','EURGBPrfd','EURJPYrfd','EURNOKrfd','EURNZDrfd','EURRUBrfd','EURSEKrfd','EURUSDrfd','GBPAUDrfd','GBPCADrfd','GBPCHFrfd','GBPJPYrfd','GBPNZDrfd','GBPUSDrfd','NZDUSDrfd','USDCADrfd','USDCHFrfd','USDDKKrfd','USDJPYrfd','USDMXNrfd','USDNOKrfd','USDRUBrfd','USDSEKrfd','USDSGDrfd','USDZARrfd']
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"MT5_eng_works.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        work_from = re.split(r'[^0-9]', data["from"][0])
        work_to = re.split(r'[^0-9]', data["to"][0])
        eng_from = datetime.datetime.combine(date(int(work_from[0]),int(work_from[1]),int(work_from[2])), time(int(work_from[3]),int(work_from[4])))
        eng_to = datetime.datetime.combine(date(int(work_to[0]),int(work_to[1]),int(work_to[2])), time(int(work_to[3]),int(work_to[4])))
        Report = 'МТ5:'
        if now >= eng_from and now <= eng_to:
            if name != "":
                return 'Технические работы на МТ5'
        else:
            Account = 'MT5 Account EUR'
            alias=key_pass(Account).url
            user=int(key_pass(Account).username)
            password=key_pass(Account).password
            if not mt5.initialize(login=user, server=alias, password=password):
                Report += '\nОшибка подключения:\nInitialize() failed, error code = '+str(mt5.last_error())
                mt5.shutdown()
                telega_alert(u'\U0000274C'+' '+Report+'\n\n#mt5')
                return Report
            else:
                connect = mt5.terminal_info().connected
                if connect != True:
                    Report += '\nНет подключения'
                trade = mt5.account_info().trade_allowed
                if trade != True:
                    Report += '\nНе разрешена торговля для ТС'
                wday = calendar.weekday(now.year, now.month, now.day)
                if (wday not in [5,6]) and (name != ""):
                    if name != "":
                        Report += '\n\nПоследние котировки:'
                    for symb in Symbols:
                        Report += tics(symb, now, name)
                mt5.shutdown()
        if Report != 'МТ5:':
            if name == "":
                telega_alert(u'\U0000274C'+' '+Report+'\n\n#mt5')
            return Report
        return Report+'\nПодключение есть.'
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
            if ("pythonw" in p.name()):
                for item in p.cmdline():
                    if (scriptName in item):
                        return 'Script: '+scriptName + '\nStatus: Running'
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
        Report = check_task('AF_Monitoring', name)
        return Report
    except:
        return 'Ошибка в функции *check_monitoring*'

def check_bot(name = ""):
    try:
        Report = check_script('AFBusinessBot', name)
        return Report
    except:
        return 'Ошибка в функции *check_bot*'

if __name__ == '__main__':
    check_all()
