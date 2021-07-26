import sys
import os
import shutil
import psycopg2
from psycopg2.extras import DictCursor
import time
import datetime
import calendar
from datetime import timedelta, date, time
import json
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass
from Telegram_Net_Total import telega_alert

def all_exposure(name = ""):
    try:
        now = datetime.datetime.now()
        wday = calendar.weekday(now.year, now.month, now.day)
        if (wday in [5,6]) and  (name == ""):
            return 'Выходной день'
        SQL_DB = 'PotgreSQL DB PROD'
        Postgre_connection = psycopg2.connect(
            host=key_pass(SQL_DB).url[:-5],
            port=int(key_pass(SQL_DB).url[-4:]),
            user=key_pass(SQL_DB).username,
            password=key_pass(SQL_DB).password,
            dbname='mt5_report'
        )
        with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                    Select
                    "finaly"."sign" as "PosNeg",
                    SUM("finaly"."inUSD") as "NetoTotal"
                    from (
                    SELECT "prev"."valute",
                    case
                    WHEN "prev"."valute" = 'AUD' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'AUDUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'CAD' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDCADrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'CHF' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDCHFrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'EUR' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'EURUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'GBP' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'GBPUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'JPY' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDJPYrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'MXN' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDMXNrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'NOK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDNOKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'NZD' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'NZDUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'RUB' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDRUBrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'USD' THEN 1* sum(prev.volume)
                    WHEN "prev"."valute" = 'ZAR' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDZARrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'SEK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDSEKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'DKK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDDKKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'SGD' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDSGDrfd')* sum(prev.volume)
                    end as "inUSD",
                    sum(prev.volume),
                    case
                    When SIGN(sum(prev.volume)) = -1 then 'Neg'
                    When SIGN(sum(prev.volume)) = 1 then 'Pos'
                    end as "sign"
                    from
                    (
                    Select *
                    from (
                    SELECT 
                    substring("Symbol",1,3) as "valute",
                    SUM(20*"Volume"*(0.5 - "Action")) as "volume"
                    FROM public.mt5_positions
                    group by "valute") as "p1"
                    UNION
                    (
                    SELECT 
                    substring("Symbol",4,3) as "valute",
                    SUM("PriceOpen"*20*"Volume"*("Action" - 0.5)) as "volume"
                    FROM public.mt5_positions
                    group by "valute") 
                    ) as "prev"
                    group by "prev"."valute"
                    ) as "finaly"
                    group by "finaly"."sign"
                    ;
            """
            cursor.execute(query)
            TotalNeto = cursor.fetchall()
            positive_neto = 0
            negative_neto = 0
            for neto in TotalNeto:
                if neto["PosNeg"] == 'Pos':
                    positive_neto = round(float(neto["NetoTotal"]),2)
                elif neto["PosNeg"] == 'Neg':
                    negative_neto = round(float(neto["NetoTotal"]),2)
        Postgre_connection.close()
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"neto_limit.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        if abs(positive_neto*2 + negative_neto) >= int(data["Total"])*1000000.00:
            Report = 'Нето по всем валютам:\n$'+ '{0:,}'.format(round(positive_neto*2 + negative_neto,2)).replace(',', ' ')
            telega_alert(u'\U000026A0'+' '+Report)
        return 'Нето по всем валютам:\n$'+ '{0:,}'.format(round(positive_neto*2 + negative_neto,2)).replace(',', ' ')
    except:
        return '\n\nОшибка в функции *all_exposure*'

def by_exposure(name = ""):
    try:
        now = datetime.datetime.now()
        wday = calendar.weekday(now.year, now.month, now.day)
        if (wday in [5,6]) and  (name == ""):
            return 'Выходной день'
        SQL_DB = 'PotgreSQL DB PROD'
        Postgre_connection = psycopg2.connect(
            host=key_pass(SQL_DB).url[:-5],
            port=int(key_pass(SQL_DB).url[-4:]),
            user=key_pass(SQL_DB).username,
            password=key_pass(SQL_DB).password,
            dbname='mt5_report'
        )
        with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                    SELECT "prev"."valute",
                    case
                    WHEN "prev"."valute" = 'AUD' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'AUDUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'CAD' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDCADrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'CHF' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDCHFrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'EUR' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'EURUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'GBP' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'GBPUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'JPY' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDJPYrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'MXN' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDMXNrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'NOK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDNOKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'NZD' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'NZDUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'RUB' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDRUBrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'USD' THEN 1* sum(prev.volume)
                    WHEN "prev"."valute" = 'ZAR' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDZARrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'SEK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDSEKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'DKK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDDKKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'SGD' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDSGDrfd')* sum(prev.volume)
                    end as "inUSD"
                    from
                    (
                    Select *
                    from (
                    SELECT 
                    substring("Symbol",1,3) as "valute",
                    SUM(20*"Volume"*(0.5 - "Action")) as "volume"
                    FROM public.mt5_positions
                    group by "valute") as "p1"
                    UNION
                    (
                    SELECT 
                    substring("Symbol",4,3) as "valute",
                    SUM("PriceOpen"*20*"Volume"*("Action" - 0.5)) as "volume"
                    FROM public.mt5_positions
                    group by "valute") 
                    ) as "prev"
                    group by "prev"."valute"
            """
            cursor.execute(query)
            ValuteNeto = cursor.fetchall()
            TotalValute = {}
            for byValute in ValuteNeto:
                TotalValute[byValute["valute"]] = round(float(byValute["inUSD"]),2)
        Postgre_connection.close()
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"neto_limit.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        Report = ''
        for key in TotalValute:
            if abs(TotalValute[key]) >= int(data["TotalValute"][key])*1000000.00:
                Report += '\n' + key + ': $'+'{0:,}'.format(round(TotalValute[key],2)).replace(',', ' ')
        if Report != '':
            telega_alert(u'\U000026A0'+' Нето по всем клиентам:'+Report)
        for key in TotalValute:
            Report += '\n' + key + ': $'+'{0:,}'.format(round(TotalValute[key],2)).replace(',', ' ')
        return 'Нето по всем клиентам:'+Report
    except:
        return '\n\nОшибка в функции *by_exposure*'

def by_login(name = ""):
    try:
        now = datetime.datetime.now()
        wday = calendar.weekday(now.year, now.month, now.day)
        if (wday in [5,6]) and  (name == ""):
            return 'Выходной день'
        SQL_DB = 'PotgreSQL DB PROD'
        Postgre_connection = psycopg2.connect(
            host=key_pass(SQL_DB).url[:-5],
            port=int(key_pass(SQL_DB).url[-4:]),
            user=key_pass(SQL_DB).username,
            password=key_pass(SQL_DB).password,
            dbname='mt5_report'
        )
        with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                    SELECT "prev"."valute",
                    case
                    WHEN "prev"."valute" = 'AUD' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'AUDUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'CAD' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDCADrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'CHF' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDCHFrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'EUR' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'EURUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'GBP' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'GBPUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'JPY' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDJPYrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'MXN' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDMXNrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'NOK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDNOKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'NZD' THEN (SELECT "BidLast" FROM public.mt5_prices	where "Symbol" like 'NZDUSDrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'RUB' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDRUBrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'USD' THEN 1* sum(prev.volume)
                    WHEN "prev"."valute" = 'ZAR' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDZARrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'SEK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDSEKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'DKK' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDDKKrfd')* sum(prev.volume)
                    WHEN "prev"."valute" = 'SGD' THEN (SELECT 1/"BidLast" FROM public.mt5_prices where "Symbol" like 'USDSGDrfd')* sum(prev.volume)
                    end as "inUSD"
                    from
                    (
                    Select *
                    from (
                    SELECT 
                    substring("Symbol",1,3) as "valute",
                    SUM(20*"Volume"*(0.5 - "Action")) as "volume"
                    FROM public.mt5_positions
                    where "Login" = 1100003787
                    group by "valute") as "p1"
                    UNION
                    (
                    SELECT 
                    substring("Symbol",4,3) as "valute",
                    SUM("PriceOpen"*20*"Volume"*("Action" - 0.5)) as "volume"
                    FROM public.mt5_positions
                    where "Login" = 1100003787
                    group by "valute") 
                    ) as "prev"
                    group by "prev"."valute"
            """
            cursor.execute(query)
            ValuteNeto = cursor.fetchall()
            ClientValute = {}
            for byValute in ValuteNeto:
                ClientValute[byValute["valute"]] = round(float(byValute["inUSD"]),2)
        Postgre_connection.close()
        direction = os.path.dirname(os.path.abspath(__file__))+'\\'
        path = direction+"neto_limit.json"
        with open(path, encoding="utf-8") as fjson:
            data = json.load(fjson)
        Report = ''
        for key in ClientValute:
            if abs(ClientValute[key]) >= int(data["ClientValute"][key])*1000000.00:
                Report += '\n' + key + ': $'+'{0:,}'.format(round(ClientValute[key],2)).replace(',', ' ')
        if Report != '':
            telega_alert(u'\U000026A0'+' Нето по клиенту 1100003787:'+Report)
        for key in ClientValute:
            Report += '\n' + key + ': $'+'{0:,}'.format(round(ClientValute[key],2)).replace(',', ' ')
        return 'Нето по клиенту 1100003787:'+Report
    except:
        return '\n\nОшибка в функции *by_login*'

def check_all_net(name = ""):
    try:
        Report = ''
        Report += all_exposure(name) + '\n\n'
        Report += by_exposure(name) + '\n\n'
        Report += by_login(name)
        return Report
    except:
        return '\n\nОшибка в функции *check_all_net*'

if __name__ == '__main__':
    check_all_net()
