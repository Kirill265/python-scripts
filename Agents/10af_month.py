import sys
import os
import shutil
import pymysql
from pymysql.cursors import DictCursor
import xlsxwriter
import datetime
from datetime import timedelta
from win32com import client
import win32com
import time
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from TeamWox import TW_text_file
from Telegram_report import telegram_bot
from keepass import key_pass

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
month_number_dict = {"1":'январь',"2":'февраль',"3":'март',"4":'апрель',"5":'май',"6":'июнь',"7":'июль',"8":'август',"9":'сентябрь',"10":'октябрь',"11":'ноябрь',"12":'декабрь'}
now = datetime.datetime.now()
if now.day > 15:
    report_date = now - timedelta(days=now.day-15)
else:
    report_date = now - timedelta(days=now.day)
month = month_number_dict[str(report_date.month)]
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
date_from = str(report_date.year)+'-'+sql_month+'-01 00.00.00'
date_to = str(report_date.year)+'-'+sql_month+'-'+str(report_date.day)+' 23.59.59'
direction = os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts"
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, '10af')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT DATE(crh.date) as currency_date, crh.value FROM currency_rate_history crh
            WHERE crh.from_id = 1
            AND crh.to_id = 3
            AND crh.date BETWEEN DATE(\""""+date_from+"""\") AND DATE(\""""+date_to+"""\")
            ORDER BY crh.date
    """
    cursor.execute(query)
    currency_rates = cursor.fetchall()
    query = """
            SELECT DISTINCT u.utm_source FROM utm u
            WHERE u.utm_source = '10af'
    """
    cursor.execute(query)
    utm_sources = cursor.fetchall()
    for utm_source in utm_sources:
        workbook = xlsxwriter.Workbook(direction+utm_source["utm_source"]+' '+month+' '+str(report_date.year)+'.xlsx')
        rub = workbook.add_format({'num_format': '0.00"₽"'})
        usd = workbook.add_format({'num_format': '"$"0.00'})
        rub_border = workbook.add_format({'num_format': '0.00"₽"','border': 1,'align': 'center','valign': 'vcenter'})
        usd_border = workbook.add_format({'num_format': '"$"0.00','border': 1,'align': 'center','valign': 'vcenter'})
        border = workbook.add_format({'border': 1,'align': 'center','valign': 'vcenter'})
        bold = workbook.add_format({'bold': True})
        bold_border = workbook.add_format({'bold': True,'border': 1,'align': 'center','valign': 'vcenter'})
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        worksheet_itog = workbook.add_worksheet('Итог')
        worksheet_itog.set_default_row(12)
        worksheet_itog.set_row(0, 15)
        worksheet_itog.write('A1', 'Клиент', bold_border)
        worksheet_itog.set_column(0, 0, 12)
        worksheet_itog.write('B1', 'Сумма за клиента RUB', bold_border)
        worksheet_itog.set_column(1, 1, 25)
        worksheet_itog.write('C1', 'Итоговая сумма', bold_border)
        worksheet_itog.set_column(2, 2, 20)
        query = """
                SELECT a.login FROM account a
                LEFT JOIN customer_utm cu ON a.customer_id = cu.customer_id
                LEFT JOIN utm u ON cu.utm_id = u.id
                WHERE u.utm_source = '"""+utm_source["utm_source"]+"""'
                AND a.login IN 
                (SELECT DISTINCT pmd.login FROM platform_mt5_deal pmd
                WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\")
        """
        cursor.execute(query)
        logins = cursor.fetchall()
        i = 1
        done_counter = 0
        for login in logins:
            i += 1
            worksheet_login = workbook.add_worksheet(str(login["login"]))
            worksheet_login.set_default_row(12)
            worksheet_login.set_row(0, 20)
            worksheet_login.write('A1', 'id', bold)
            worksheet_login.write('B1', 'login', bold)
            worksheet_login.set_column(0, 1, 13)
            worksheet_login.write('C1', 'mt5_order_id', bold)
            worksheet_login.set_column(2, 2, 15)
            worksheet_login.write('D1', 'action', bold)
            worksheet_login.write('E1', 'entry', bold)
            worksheet_login.set_column(3, 4, 7)
            worksheet_login.write('F1', 'symbol', bold)
            worksheet_login.set_column(5, 5, 12)
            worksheet_login.write('G1', 'created_at', bold)
            worksheet_login.write('H1', 'date', bold)
            worksheet_login.set_column(6, 7, 18)
            worksheet_login.write('I1', 'price', bold)
            worksheet_login.set_column(8, 8, 8)
            worksheet_login.write('J1', 'volume', bold)
            worksheet_login.set_column(9, 9, 9)
            worksheet_login.write('K1', 'profit', bold)
            worksheet_login.set_column(10, 10, 10) 
            worksheet_login.write('L1', 'volume_usd', bold)
            worksheet_login.set_column(11, 11, 14)
            worksheet_login.write('M1', 'expert_position_id', bold)
            worksheet_login.set_column(12, 12, 20)
            worksheet_login.write('N1', 'Вознаграждение, USD', bold)
            worksheet_login.set_column(13, 13, 18)
            worksheet_login.write('O1', 'Курс USDRUR на дату сделки', bold)
            worksheet_login.set_column(14, 14, 14)
            worksheet_login.write('P1', 'Вознаграждение, RUR', bold)
            worksheet_login.set_column(15, 15, 18)
            worksheet_login.write('S1', 'USD без округления', bold)
            worksheet_login.write('T1', 'RUB без округления', bold)
            worksheet_login.set_column(18, 19, 12)
            worksheet_login.write('R2', 'Вознаграждение')
            worksheet_login.set_column(17, 17, 23)
            worksheet_login.write('S2', '=SUM(N:N)', usd)
            worksheet_login.write('T2', '=SUM(P:P)', rub)
            query = """
                    SELECT
                    pmd.id
                    , pmd.login
                    , pmd.mt5_order_id
                    , pmd.action
                    , pmd.entry
                    , pmd.symbol
                    , pmd.created_at
                    , date(pmd.created_at) AS date
                    , pmd.price
                    , pmd.volume
                    , pmd.profit
                    , pmd.volume_usd
                    , pmd.expert_position_id
                    FROM platform_mt5_deal pmd
                    LEFT JOIN account a ON pmd.login = a.login
                    LEFT JOIN customer_utm cu ON a.customer_id = cu.customer_id
                    LEFT JOIN utm u ON cu.utm_id = u.id
                    LEFT JOIN account_group ag ON a.group_id = ag.id
                    WHERE a.login = '"""+str(login["login"])+"""'
                    AND
                    pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
                    ORDER BY pmd.id
            """
            cursor.execute(query)
            deals = cursor.fetchall()
            j = 1
            for deal in deals:
                j += 1
                worksheet_login.write(f'A{j}', deal["id"])
                worksheet_login.write(f'B{j}', deal["login"])
                worksheet_login.write(f'C{j}', deal["mt5_order_id"])
                worksheet_login.write(f'D{j}', deal["action"])
                worksheet_login.write(f'E{j}', deal["entry"])
                worksheet_login.write(f'F{j}', deal["symbol"])
                worksheet_login.write(f'G{j}', str(deal["created_at"]))
                worksheet_login.write(f'H{j}', str(deal["date"]))
                worksheet_login.write(f'I{j}', deal["price"])
                worksheet_login.write(f'J{j}', deal["volume"])
                worksheet_login.write(f'K{j}', deal["profit"])
                worksheet_login.write(f'L{j}', deal["volume_usd"])
                worksheet_login.write(f'M{j}', deal["expert_position_id"])
                worksheet_login.write(f'N{j}', '=IF(J'+str(j)+'>=11,L'+str(j)+'/1000000*30,L'+str(j)+'/1000000*25)')
                worksheet_login.write(f'O{j}', '=VLOOKUP(H'+str(j)+',\'Курс ЦБ\'!A:B,2,FALSE)')
                worksheet_login.write(f'P{j}', '= N'+str(j)+'*O'+str(j)+'')
            worksheet_itog.write(f'A{i}',str(login["login"]), border)
            worksheet_itog.write(f'B{i}','=ROUND(\''+worksheet_login.name+'\'!$T$2,2)', rub_border)
            done_counter += 1
        if i == 2:
            worksheet_itog.write('C2','=B2', rub_border)
        else:
            worksheet_itog.merge_range(f'C2:C{i}','=SUM(B2:B'+str(i)+')', rub_border)
        worksheet_currency = workbook.add_worksheet('Курс ЦБ')
        worksheet_currency.set_default_row(12)
        i = 0
        for currency_rate in currency_rates:
            i += 1
            worksheet_currency.write(f'A{i}',str(currency_rate["currency_date"]))
            worksheet_currency.set_column(0, 0, 12)
            worksheet_currency.write(f'B{i}',currency_rate["value"])
            worksheet_currency.set_column(1, 1, 8)
        workbook.close()
        xl = win32com.client.DispatchEx('Excel.Application')
        xl.Visible = False
        wb = xl.Workbooks.Open(direction+utm_source["utm_source"]+" "+month+" "+str(report_date.year)+".xlsx")
        wb.Close(True)
connection.close()

Report_reward = """[Расчет вознаграждения для агента 10af](https://team.alfaforex.com/servicedesk/view/11278)

Отчетный месяц: *"""+month+""" """+str(report_date.year)+"""*.

Рассчитано для """+str(done_counter)+""" счетов."""

Report_TW = 'За '+month+' '+str(report_date.year)

telegram_bot(Report_reward)
#print(Report_reward)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11278"
message_text = ''
attached_file = direction+utm_source["utm_source"]+" "+month+" "+str(report_date.year)+".xlsx"

TW_text_file(URL_TW,message_text,attached_file)
