import requests
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
import xlsxwriter
import datetime
#import calendar
from datetime import timedelta
import shutil
from win32com import client
import win32com
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from Telegram_report import telegram_bot
from keepass import key_pass

SQL_DB = 'MySQL DB ACC'
connection = pymysql.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    db='report_new', 
    charset='utf8mb4',
    cursorclass=DictCursor
)
month_number_dict = {"1":'January',"2":'February',"3":'March',"4":'April',"5":'May',"6":'June',"7":'July',"8":'August',"9":'September',"10":'October',"11":'November',"12":'December'} 
now = datetime.datetime.now()
report_date = now - timedelta(days=now.day)
month = month_number_dict[str(report_date.month)]
prev_month_date = report_date - timedelta(days=report_date.day)
month_prev = month_number_dict[str(prev_month_date.month)]
date_from = '2021-10-01 00.00.00'
date_to = '2021-10-13 23.59.59'

if date_to[5:7] in ['10','11','12']:
    month = month_number_dict[date_to[5:7]]
else:
    month = month_number_dict[date_to[6:7]]

direction = os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts"
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, 'ACM')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, str(report_date.year)+' '+month)
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'
log_txt = open(direction+'log.txt', 'w')
log_txt.write('пользователь: '+key_pass(SQL_DB).username+'\n')
log_txt.write('месяц: '+month+'\n')
log_txt.write('начало расчета: '+str(datetime.datetime.now())+'\n')
Report_success = ''
mt5 = 0
mt4 = 0
with connection.cursor() as cursor:
    query = """
            SET time_zone = 'Europe/Moscow';
    """
    cursor.execute(query)
    # 2.1. Summary report (MT5)
    log_txt.write('2.1. Summary report (MT5)\n')
    query = """
            SELECT report_new.mt5_deals.Login
            ,mu.name
            ,trim(mu.state) as customer_id
            ,round(sum(mt5_deals.profit),2) as profit
            ,round(sum(mt5_deals.storage),2) as swap
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            ,case
            WHEN mu.state = '268' then '10297-MTA'
            WHEN mu.state = '231' then '10277-MTA'
            WHEN mu.state = '210' then '10264-МТА'
            WHEN mu.state = '294' then '10304MTA'
            else mu.zipcode
            end as 'ZipCode' 
             -- поле нужно, чтобы вычленять клиентов-юр лиц (для них нужно выводить номер договора вида ХХХХХ-МТА, для физиков - только номер ЛК)
            FROM report_new.mt5_deals
            left join report_new.mt5_users_view  mu on mu.login=report_new.mt5_deals.Login
            where mt5_deals.time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt5_deals.action < 2
            GROUP BY mt5_deals.login,mu.state,mu.zipcode,mu.`group`,mu.name;
    """
    cursor.execute(query)
    summary_report_mt5 = cursor.fetchall()
    if len(summary_report_mt5) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+date_to[0:4]+'_'+date_from[8:10]+'-'+date_to[8:10]+' '+month[0:3]+'_пункт1_Summary report_MT5.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','Login', bold_title)
        worksheet.set_column(0, 0, 10)
        worksheet.write('B1','Name', bold_title)
        worksheet.set_column(1, 1, 20)
        worksheet.write('C1','customer_id', bold_title)
        worksheet.set_column(2, 2, 13.5)
        worksheet.write('D1','profit', bold_title)
        worksheet.set_column(3, 3, 10)
        worksheet.write('E1','swap', bold_title)
        worksheet.set_column(4, 4, 8)
        worksheet.write('F1','currency_id', bold_title)
        worksheet.set_column(5, 5, 13)
        worksheet.write('G1','ZipCode', bold_title)
        worksheet.set_column(6, 6, 10)
        i = 1
        for summary_mt5 in summary_report_mt5:
            i += 1
            worksheet.write(f'A{i}',summary_mt5["Login"])
            worksheet.write(f'B{i}',summary_mt5["Name"])
            worksheet.write(f'C{i}',summary_mt5["customer_id"])
            worksheet.write(f'D{i}',summary_mt5["profit"])
            worksheet.write(f'E{i}',summary_mt5["swap"])
            worksheet.write(f'F{i}',summary_mt5["currency_id"])
            worksheet.write(f'G{i}',summary_mt5["ZipCode"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Summary report (MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 2.2. Summary report (MT4)
    log_txt.write('2.2. Summary report (MT4)')
    query = """
            SELECT mt4_trades.login
            ,mu.name
            ,trim(mu.state) as customer_id
            ,round(sum(mt4_trades.profit),2) as profit
            ,round(sum(mt4_trades.swaps),2) as swap
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            ,case
            WHEN mu.state = '268' then '10297-MTA'
            WHEN mu.state = '231' then '10277-MTA'
            WHEN mu.state = '210' then '10264-МТА'
            WHEN mu.state = '294' then '10304MTA'
            else mu.zipcode
            end as 'ZIPCODE' 
            -- поле нужно, чтобы вычленять клиентов-юр лиц (для них нужно выводить номер договора вида ХХХХХ-МТА, для физиков - только номер ЛК)
            FROM mt4_trades
            left join mt4_users_view mu on mu.login=mt4_trades.login
            where mt4_trades.close_time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt4_trades.cmd < 2
            GROUP BY mt4_trades.login
            ,mu.state
            ,mu.zipcode
            ,mu.name,currency_id;
    """
    cursor.execute(query)
    summary_report_mt4 = cursor.fetchall()
    if len(summary_report_mt4) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+date_to[0:4]+'_'+date_from[8:10]+'-'+date_to[8:10]+' '+month[0:3]+'_пункт1_Summary report_MT4.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','login', bold_title)
        worksheet.write('B1','NAME', bold_title)
        worksheet.write('C1','customer_id', bold_title)
        worksheet.write('D1','profit', bold_title)
        worksheet.write('E1','swap', bold_title)
        worksheet.write('F1','currency_id', bold_title)
        worksheet.write('G1','ZIPCODE', bold_title)
        i = 1
        for summary_mt4 in summary_report_mt4:
            i += 1
            worksheet.write(f'A{i}',summary_mt4["login"])
            worksheet.write(f'B{i}',summary_mt4["NAME"])
            worksheet.write(f'C{i}',summary_mt4["customer_id"])
            worksheet.write(f'D{i}',summary_mt4["profit"])
            worksheet.write(f'E{i}',summary_mt4["swap"])
            worksheet.write(f'F{i}',summary_mt4["currency_id"])
            worksheet.write(f'G{i}',summary_mt4["ZIPCODE"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Summary report (MT4)\n'
        mt4 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
   
Report_ACM = """[Выгрузка промежуточного отчета для ACM](https://team.alfaforex.com/tasks/view/2792)

Отчетный период: """+date_from[8:10]+"""-"""+date_to[8:10]+""" """+month+""" """+date_to[0:4]+""".

#ACM_summary"""

#telegram_bot(Report_ACM)
print(Report_ACM)

URL_TW = "https://team.alfaforex.com/tasks/view/2792"
message_text = ''

#TW_text_file(URL_TW,message_text)




