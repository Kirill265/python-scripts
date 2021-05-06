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
from Telegram_report import telegram_bot
from keepass import key_pass
from win32com import client
import win32com

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
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
if prev_month_date.month < 10:
    sql_month_prev = '0'+str(prev_month_date.month)
else:
    sql_month_prev = str(prev_month_date.month)
date_from = str(report_date.year)+'-'+sql_month+'-01 00.00.00'
date_to = str(report_date.year)+'-'+sql_month+'-'+str(report_date.day)+' 23.59.59'
date_from_8 = str(report_date.year)+'-'+sql_month+'-'+str(report_date.day)+' 00.00.00'
date_to_prev = str(prev_month_date.year)+'-'+sql_month_prev+'-'+str(prev_month_date.day)+' 23.59.59'
direction = os.path.dirname(os.path.abspath(__file__))
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
    # 1. New Accounts (MT5/MT4)
    log_txt.write('1. New Accounts (MT5/MT4)\n')
    query = """
            select a.login
            ,a.state as customer_id
            ,if(c.is_company=1,cc.contract_number,\"\") as contract_number
            ,a.name
            ,if(c.is_company=1,coun1.name,coun.name) as citizenship_country
            ,a.registration as created_at
            ,a.`group`
            ,IFNULL(cur.name,'null') as currency
            ,IFNULL(acs.name,'null') as status
            from
            (
            select login
            ,state
            ,zipcode
            ,name
            ,registration
            ,mu.`group`
            from report_new.mt5_users_view mu
            where registration between '"""+date_from+"""' and '"""+date_to+"""'
            and mu.`group` not like '%test%'
            and mu.`group` not like '%manager%'
            union 
            select login
            ,state
            ,zipcode
            ,name
            ,regdate as registration
            ,mu.`group`
            from report_new.mt4_users_view mu
            where regdate between '"""+date_from+"""' and '"""+date_to+"""'
            and mu.`group` not like '%test%'
            and mu.`group` not like '%manager%'
            ) as a
            left join af_lk.customer_view c on c.id=a.state
            left join af_lk.customer_company cc on cc.customer_id=c.id
            left join af_lk.customer_individual ci on ci.customer_id=c.id
            left join af_lk.country coun on coun.id=ci.citizenship_country_id
            left join af_lk.country coun1 on coun1.id=cc.country_id
            left join af_lk.account acc on acc.login=a.login
            left join af_lk.currency cur on cur.id=acc.currency_id
            left join af_lk.account_status acs on acs.id=acc.status_id
    """
    cursor.execute(query)
    new_accounts = cursor.fetchall()
    if len(new_accounts) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM_New clients_01-'+str(report_date.day)+' '+month[0:3]+' '+str(report_date.year)+'.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','login', bold_title)
        worksheet.set_column(0, 0, 10)
        worksheet.write('B1','customer_id', bold_title)
        worksheet.set_column(1, 1, 13)
        worksheet.write('C1','contract_number', bold_title)
        worksheet.set_column(2, 2, 18)
        worksheet.write('D1','name', bold_title)
        worksheet.set_column(3, 3, 17)
        worksheet.write('E1','citizenship_country', bold_title)
        worksheet.set_column(4, 4, 21)
        worksheet.write('F1','created_at', bold_title)
        worksheet.set_column(5, 5, 18)
        worksheet.write('G1','group', bold_title)
        worksheet.set_column(6, 6, 19)
        worksheet.write('H1','currency', bold_title)
        worksheet.set_column(7, 7, 10)
        worksheet.write('I1','status', bold_title)
        worksheet.set_column(8, 8, 8)
        i = 1
        for new_account in new_accounts:
            i += 1
            worksheet.write(f'A{i}',new_account["login"])
            worksheet.write(f'B{i}',new_account["customer_id"])
            worksheet.write(f'C{i}',new_account["contract_number"])
            worksheet.write(f'D{i}',new_account["name"])
            worksheet.write(f'E{i}',new_account["citizenship_country"])
            worksheet.write(f'F{i}',str(new_account["created_at"]))
            worksheet.write(f'G{i}',new_account["group"])
            worksheet.write(f'H{i}',new_account["currency"])
            worksheet.write(f'I{i}',new_account["status"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   New Accounts (MT5/MT4)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
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
            ,mu.zipcode
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
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт1_Summary report_MT5.xlsx')
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
            ,mu.zipcode
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
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт1_Summary report_MT4.xlsx')
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
    # 3. Конвертации (MT5)
    log_txt.write('3. Конвертации (MT5)\n')
    query = """
            SELECT mt5_deals.deal as deal
            ,mt5_deals.login as login
            ,mt5_deals.profit as amount
            ,mu.state
            ,mu.zipcode
            ,
            CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            ,mt5_deals.comment
            ,mt5_deals.time
            FROM mt5_deals
            LEFT JOIN mt5_users_view mu ON mt5_deals.login = mu.login
            WHERE mt5_deals.action >1
            and mt5_deals.comment LIKE '%Cnv%'
            AND mt5_deals.time BETWEEN '"""+date_from+"""' and '"""+date_to+"""'
    """
    cursor.execute(query)
    convertation = cursor.fetchall()
    if len(convertation) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт5_конвертации.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','amount', bold_title)
        worksheet.write('D1','State', bold_title)
        worksheet.write('E1','ZipCode', bold_title)
        worksheet.write('F1','currency_id', bold_title)
        worksheet.write('G1','comment', bold_title)
        worksheet.write('H1','time', bold_title)
        i = 1
        for conv in convertation:
            i += 1
            worksheet.write(f'A{i}',conv["deal"])
            worksheet.write(f'B{i}',conv["login"])
            worksheet.write(f'C{i}',conv["amount"])
            worksheet.write(f'D{i}',conv["State"])
            worksheet.write(f'E{i}',conv["ZipCode"])
            worksheet.write(f'F{i}',conv["currency_id"])
            worksheet.write(f'G{i}',conv["comment"])
            worksheet.write(f'H{i}',str(conv["time"]))
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Конвертации (MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 4.1. Драг металлы (MT5)
    log_txt.write('4.1. Драг металлы (MT5)\n')
    query = """
            SELECT mt5_deals.deal
            ,mt5_deals.login
            ,mu.name
            ,mt5_deals.time as time
            ,if(mt5_deals.action=0 ,'buy','sell') as order_type
            ,mt5_deals.symbol
            ,mt5_deals.volume/10000 as volume
            ,mt5_deals.price
            ,mt5_deals.profit as profit
            ,mt5_deals.storage as swap
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,mu.state
            ,mu.zipcode
            FROM mt5_deals
            left join mt5_users_view mu on mt5_deals.login = mu.login
            left join mt5_symbols on mt5_symbols.symbol = mt5_deals.symbol
            where  mt5_deals.time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt5_deals.action <2
            and mt5_symbols.path like '%Metal%';
    """
    cursor.execute(query)
    metals_mt5 = cursor.fetchall()
    if len(metals_mt5) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт2_Отчет по финансовым результатам клиентов (драг металлы).xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.set_column(0, 0, 10)
        worksheet.write('B1','login', bold_title)
        worksheet.set_column(1, 1, 8)
        worksheet.write('C1','Name', bold_title)
        worksheet.set_column(2, 2, 17)
        worksheet.write('D1','time', bold_title)
        worksheet.set_column(3, 3, 18)
        worksheet.write('E1','order_type', bold_title)
        worksheet.set_column(4, 4, 12)
        worksheet.write('F1','symbol', bold_title)
        worksheet.set_column(5, 5, 8)
        worksheet.write('G1','volume', bold_title)
        worksheet.set_column(6, 6, 9)
        worksheet.write('H1','price', bold_title)
        worksheet.write('I1','profit', bold_title)
        worksheet.write('J1','swap', bold_title)
        worksheet.set_column(7, 9, 8)
        worksheet.write('K1','currency', bold_title)
        worksheet.write('L1','State', bold_title)
        worksheet.write('M1','ZipCode', bold_title)
        worksheet.set_column(10, 12, 10)
        i = 1
        for metal_mt5 in metals_mt5:
            i += 1
            worksheet.write(f'A{i}',metal_mt5["deal"])
            worksheet.write(f'B{i}',metal_mt5["login"])
            worksheet.write(f'C{i}',metal_mt5["Name"])
            worksheet.write(f'D{i}',str(metal_mt5["time"]))
            worksheet.write(f'E{i}',metal_mt5["order_type"])
            worksheet.write(f'F{i}',metal_mt5["symbol"])
            worksheet.write(f'G{i}',metal_mt5["volume"])
            worksheet.write(f'H{i}',metal_mt5["price"])
            worksheet.write(f'I{i}',metal_mt5["profit"])
            worksheet.write(f'J{i}',metal_mt5["swap"])
            worksheet.write(f'K{i}',metal_mt5["currency"])
            worksheet.write(f'L{i}',metal_mt5["State"])
            worksheet.write(f'M{i}',metal_mt5["ZipCode"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Драг металлы (MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 4.2. Драг металлы (MT4)
    log_txt.write('4.2. Драг металлы (MT4)\n')
    query = """
            SELECT 
            mt4_trades.ticket
            ,mt4_trades.login
            ,mu.name
            ,mt4_trades.close_time as time
            ,if(mt4_trades.cmd=0,'buy','sell') as order_type
            ,mt4_trades.symbol
            ,mt4_trades.volume/100 as volume
            ,round(mt4_trades.close_price,5) as close_price  
            ,mt4_trades.profit as profit
            ,mt4_trades.swaps as swap
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,mu.state
            ,mu.zipcode
            FROM mt4_trades
            left join mt4_users_view mu on mt4_trades.login = mu.login
            left join mt5_symbols on mt5_symbols.symbol = mt4_trades.symbol
            where  mt4_trades.close_time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt4_trades.cmd <2
            and mt5_symbols.path like '%Metal%';
    """
    cursor.execute(query)
    metals_mt4 = cursor.fetchall()
    if len(metals_mt4) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт2_Отчет по финансовым результатам клиентов (драг металлы) (MT4).xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','ticket', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','NAME', bold_title)
        worksheet.write('D1','time', bold_title)
        worksheet.write('E1','order_type', bold_title)
        worksheet.write('F1','symbol', bold_title)
        worksheet.write('G1','volume', bold_title)
        worksheet.write('H1','price', bold_title)
        worksheet.write('I1','profit', bold_title)
        worksheet.write('J1','swap', bold_title)
        worksheet.write('K1','currency', bold_title)
        worksheet.write('L1','STATE', bold_title)
        worksheet.write('M1','ZIPCODE', bold_title)
        i = 1
        for metal_mt4 in metals_mt4:
            i += 1
            worksheet.write(f'A{i}',metal_mt4["ticket"])
            worksheet.write(f'B{i}',metal_mt4["login"])
            worksheet.write(f'C{i}',metal_mt4["NAME"])
            worksheet.write(f'D{i}',str(metal_mt4["time"]))
            worksheet.write(f'E{i}',metal_mt4["order_type"])
            worksheet.write(f'F{i}',metal_mt4["symbol"])
            worksheet.write(f'G{i}',metal_mt4["volume"])
            worksheet.write(f'H{i}',metal_mt4["price"])
            worksheet.write(f'I{i}',metal_mt4["profit"])
            worksheet.write(f'J{i}',metal_mt4["swap"])
            worksheet.write(f'K{i}',metal_mt4["currency"])
            worksheet.write(f'L{i}',metal_mt4["STATE"])
            worksheet.write(f'M{i}',metal_mt4["ZIPCODE"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Драг металлы (MT4)\n'
        mt4 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 5.1. CFD (MT5)
    log_txt.write('5.1. CFD (MT5)\n')
    query = """
            SELECT mt5_deals.deal
            ,mt5_deals.login
            ,mu.name
            ,mt5_deals.time as time
            ,if(mt5_deals.action=0 ,'buy','sell') as order_type
            ,mt5_deals.symbol
            ,mt5_deals.volume/10000 as volume
            ,mt5_deals.price
            ,mt5_deals.profit as profit
            ,mt5_deals.storage as swap
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,mu.state
            ,mu.zipcode
            FROM mt5_deals
            left join mt5_users_view mu on mt5_deals.login = mu.login
            left join mt5_symbols on mt5_symbols.symbol = mt5_deals.symbol
            where  mt5_deals.time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt5_deals.action <2
            and mt5_symbols.path like '%CFD%';
    """
    cursor.execute(query)
    cfd_report_mt5 = cursor.fetchall()
    if len(cfd_report_mt5) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт3_Отчет по финансовым результатам клиентов (CFD).xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','Name', bold_title)
        worksheet.write('D1','time', bold_title)
        worksheet.write('E1','order_type', bold_title)
        worksheet.write('F1','symbol', bold_title)
        worksheet.write('G1','volume', bold_title)
        worksheet.write('H1','price', bold_title)
        worksheet.write('I1','profit', bold_title)
        worksheet.write('J1','swap', bold_title)
        worksheet.write('K1','currency', bold_title)
        worksheet.write('L1','State', bold_title)
        worksheet.write('M1','ZipCode', bold_title)
        i = 1
        for cfd_mt5 in cfd_report_mt5:
            i += 1
            worksheet.write(f'A{i}',cfd_mt5["deal"])
            worksheet.write(f'B{i}',cfd_mt5["login"])
            worksheet.write(f'C{i}',cfd_mt5["Name"])
            worksheet.write(f'D{i}',str(cfd_mt5["time"]))
            worksheet.write(f'E{i}',cfd_mt5["order_type"])
            worksheet.write(f'F{i}',cfd_mt5["symbol"])
            worksheet.write(f'G{i}',cfd_mt5["volume"])
            worksheet.write(f'H{i}',cfd_mt5["price"])
            worksheet.write(f'I{i}',cfd_mt5["profit"])
            worksheet.write(f'J{i}',cfd_mt5["swap"])
            worksheet.write(f'K{i}',cfd_mt5["currency"])
            worksheet.write(f'L{i}',cfd_mt5["State"])
            worksheet.write(f'M{i}',cfd_mt5["ZipCode"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   CFD (MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 5.2. CFD (MT4)
    log_txt.write('5.2. CFD (MT4)\n')
    query = """
            SELECT mt4_trades.ticket
            ,mt4_trades.login
            ,mu.name
            ,if(mt4_trades.cmd=0,'buy','sell') as order_type
            ,mt4_trades.symbol
            ,mt4_trades.volume/100 as volume
            ,mt4_trades.open_time as open_time
            ,mt4_trades.open_price
            ,mt4_trades.close_time as close_time
            ,mt4_trades.close_price
            ,mt4_trades.profit
            ,mt4_trades.swaps as swap
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,mu.state
            ,mu.zipcode
            FROM mt4_trades
            left join mt4_users_view mu on mt4_trades .login = mu.login
            where  mt4_trades.close_time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt4_trades.cmd <2
            and length(mt4_trades.symbol) <>6;
    """
    cursor.execute(query)
    cfd_report_mt4 = cursor.fetchall()
    if len(cfd_report_mt4) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт3_Отчет по финансовым результатам клиентов (CFD) (MT4).xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','ticket', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','NAME', bold_title)
        worksheet.write('D1','order_type', bold_title)
        worksheet.write('E1','symbol', bold_title)
        worksheet.write('F1','volume', bold_title)
        worksheet.write('G1','open_time', bold_title)
        worksheet.write('H1','open_price', bold_title)
        worksheet.write('I1','close_time', bold_title)
        worksheet.write('J1','close_price', bold_title)
        worksheet.write('K1','profit', bold_title)
        worksheet.write('L1','swap', bold_title)
        worksheet.write('M1','currency', bold_title)
        worksheet.write('N1','STATE', bold_title)
        worksheet.write('O1','ZIPCODE', bold_title)
        i = 1
        for cfd_mt4 in cfd_report_mt4:
            i += 1
            worksheet.write(f'A{i}',cfd_mt4["ticket"])
            worksheet.write(f'B{i}',cfd_mt4["login"])
            worksheet.write(f'C{i}',cfd_mt4["NAME"])
            worksheet.write(f'D{i}',cfd_mt4["order_type"])
            worksheet.write(f'E{i}',cfd_mt4["symbol"])
            worksheet.write(f'F{i}',cfd_mt4["volume"])
            worksheet.write(f'G{i}',str(cfd_mt4["open_time"]))
            worksheet.write(f'H{i}',cfd_mt4["open_price"])
            worksheet.write(f'I{i}',str(cfd_mt4["close_time"]))
            worksheet.write(f'J{i}',cfd_mt4["close_price"])
            worksheet.write(f'K{i}',cfd_mt4["profit"])
            worksheet.write(f'L{i}',cfd_mt4["swap"])
            worksheet.write(f'M{i}',cfd_mt4["currency"])
            worksheet.write(f'N{i}',cfd_mt4["STATE"])
            worksheet.write(f'O{i}',cfd_mt4["ZIPCODE"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   CFD (MT4)\n'
        mt4 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 6. Фактические выплаты партнерам (MT5)
    log_txt.write('6. Фактические выплаты партнерам (MT5)\n')
    query = """
            select mt5_deals.deal
            ,mt5_deals.login
            ,'USD' as currency_id
            ,mu.state as customer_id
            ,mt5_deals.time
            ,round(mt5_deals.profit,2) as profit
            ,mt5_deals.comment
            from mt5_deals
            left join mt5_users_view mu on mt5_deals.login=mu.login
            where mt5_deals.time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt5_deals.action >1
            and mu.`Group` like '%partner%'
            and mt5_deals.comment not like '%transfer%'
    """
    cursor.execute(query)
    partners = cursor.fetchall()
    if len(partners) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт 4_Выплаты партнерам.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','currency_id', bold_title)
        worksheet.write('D1','customer_id', bold_title)
        worksheet.write('E1','time', bold_title)
        worksheet.write('F1','profit', bold_title)
        worksheet.write('G1','comment', bold_title)
        i = 1
        for partner in partners:
            i += 1
            worksheet.write(f'A{i}',partner["deal"])
            worksheet.write(f'B{i}',partner["login"])
            worksheet.write(f'C{i}',partner["currency_id"])
            worksheet.write(f'D{i}',partner["customer_id"])
            worksheet.write(f'E{i}',str(partner["time"]))
            worksheet.write(f'F{i}',partner["profit"])
            worksheet.write(f'G{i}',partner["comment"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Фактические выплаты партнерам (MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 7. ПАММ-счета (MT4/MT5)
    log_txt.write('7. ПАММ-счета (MT4/MT5)\n')
    query = """
            (
            SELECT
            mt4_trades.ticket   AS deal
            ,mt4_trades.login  AS login
            ,mt4_trades.profit AS amount
            ,
            CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END 
            as currency_id
            ,mt4_trades.comment
            ,mt4_trades.close_time as time
            ,mu.`GROUP`
            FROM mt4_trades
            LEFT JOIN mt4_users_view mu ON mt4_trades.login = mu.login
            WHERE mt4_trades.comment LIKE '%PAM%' -- с комментарием памм
            and mt4_trades.cmd > 5      -- сделка балансовая
            AND mt4_trades.close_time BETWEEN '"""+date_from+"""' and '"""+date_to+"""'
            )
            Union
            (
            SELECT
            mt5_deals.deal   AS deal
            , mt5_deals.login  AS login
            , mt5_deals.profit AS amount
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            ,mt5_deals.comment
            ,mt5_deals.time as TIME
            ,mu.`GROUP`
            FROM mt5_deals
            LEFT JOIN mt5_users_view mu ON mt5_deals.login = mu.login
            WHERE mt5_deals.comment LIKE '%PAM%'
            and mt5_deals.Action > 1      
            AND mt5_deals.time BETWEEN '"""+date_from+"""' and '"""+date_to+"""'
            )
    """
    cursor.execute(query)
    pamm_report = cursor.fetchall()
    if len(pamm_report) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт6_Отчет по операциям ПАММ.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','amount', bold_title)
        worksheet.write('D1','currency_id', bold_title)
        worksheet.write('E1','comment', bold_title)
        worksheet.write('F1','time', bold_title)
        worksheet.write('G1','GROUP', bold_title)
        i = 1
        for pamm in pamm_report:
            i += 1
            worksheet.write(f'A{i}',pamm["deal"])
            worksheet.write(f'B{i}',pamm["login"])
            worksheet.write(f'C{i}',pamm["amount"])
            worksheet.write(f'D{i}',pamm["currency_id"])
            worksheet.write(f'E{i}',pamm["comment"])
            worksheet.write(f'F{i}',str(pamm["time"]))
            worksheet.write(f'G{i}',pamm["GROUP"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   ПАММ-счета (MT4/MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 8.1. Open_positions (MT5)
    log_txt.write('8.1. Open_positions (MT5)\n')
    query = """
            SELECT mt5_positions_daily.position_id
            ,mt5_positions_daily.login
            ,CASE
            when mt5_positions_daily.action = 0 then 'buy'
            else 'sell'
            end as type
            ,mt5_positions_daily.symbol
            ,mt5_positions_daily.volume/10000 as volume  
            ,mt5_positions_daily.timecreate
            ,mt5_positions_daily.storage
            ,mt5_positions_daily.profit
            ,if( mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,mu.state
            ,mu.zipcode
            ,mu.`Group`
            ,round(mt5_positions_daily.priceopen,5) as priceopen
            ,round(mt5_positions_daily.pricecurrent,5) as pricecurrent
            ,mt5_positions_daily.snapshot_at
            FROM custom.mt5_positions_daily
            left join report_new.mt5_users_view mu on mu.login=mt5_positions_daily.login
            where mt5_positions_daily.snapshot_at BETWEEN '"""+date_from_8+"""' and '"""+date_to+"""'
            and mu.`Group` not LIKE '%TEST%';
    """
    cursor.execute(query)
    open_positons_mt5 = cursor.fetchall()
    if len(open_positons_mt5) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт8_открытые позиции (MT5).xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','position_id', bold_title)
        worksheet.set_column(0, 0, 12)
        worksheet.write('B1','login', bold_title)
        worksheet.set_column(1, 1, 8)
        worksheet.write('C1','type', bold_title)
        worksheet.set_column(2, 2, 6)
        worksheet.write('D1','symbol', bold_title)
        worksheet.write('E1','volume', bold_title)
        worksheet.set_column(3, 4, 9)
        worksheet.write('F1','timecreate', bold_title)
        worksheet.set_column(5, 5, 18)
        worksheet.write('G1','storage', bold_title)
        worksheet.write('H1','profit', bold_title)
        worksheet.write('I1','currency', bold_title)
        worksheet.write('J1','State', bold_title)
        worksheet.write('K1','ZipCode', bold_title)
        worksheet.set_column(6, 10, 10)
        worksheet.write('L1','Group', bold_title)
        worksheet.set_column(11, 11, 19)
        worksheet.write('M1','priceopen', bold_title)
        worksheet.set_column(12, 12, 12)
        worksheet.write('N1','pricecurrent', bold_title)
        worksheet.set_column(13, 13, 13)
        worksheet.write('O1','snapshot_at', bold_title)
        worksheet.set_column(14, 14, 18)
        i = 1
        for openpos_mt5 in open_positons_mt5:
            i += 1
            worksheet.write(f'A{i}',openpos_mt5["position_id"])
            worksheet.write(f'B{i}',openpos_mt5["login"])
            worksheet.write(f'C{i}',openpos_mt5["type"])
            worksheet.write(f'D{i}',openpos_mt5["symbol"])
            worksheet.write(f'E{i}',openpos_mt5["volume"])
            worksheet.write(f'F{i}',str(openpos_mt5["timecreate"]))
            worksheet.write(f'G{i}',openpos_mt5["storage"])
            worksheet.write(f'H{i}',openpos_mt5["profit"])
            worksheet.write(f'I{i}',openpos_mt5["currency"])
            worksheet.write(f'J{i}',openpos_mt5["State"])
            worksheet.write(f'K{i}',openpos_mt5["ZipCode"])
            worksheet.write(f'L{i}',openpos_mt5["Group"])
            worksheet.write(f'M{i}',openpos_mt5["priceopen"])
            worksheet.write(f'N{i}',openpos_mt5["pricecurrent"])
            worksheet.write(f'O{i}',str(openpos_mt5["snapshot_at"]))
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Open_positions (MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 8.2. Open_positions (MT4)
    log_txt.write('8.2. Open_positions (MT4)\n')
    query = """
            SELECT mt4_open_positions_daily.ticket
            ,mt4_open_positions_daily.login
            ,  case 
            when mt4_open_positions_daily.cmd = 0 then 'buy'
            when mt4_open_positions_daily.cmd = 1 then 'sell'
            WHEN mt4_open_positions_daily.cmd = 2 then 'buy limit'
            when mt4_open_positions_daily.cmd = 3 then 'sell limit'
            when mt4_open_positions_daily.cmd = 4 then 'buy stop'      
            else 'sell stop'          
            end as type
            ,mt4_open_positions_daily.symbol
            ,mt4_open_positions_daily.volume/100 as volume
            , mt4_open_positions_daily.open_time
            ,mt4_open_positions_daily.swaps
            ,mt4_open_positions_daily.profit
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,mu.state
            ,mu.zipcode
            ,mt4_open_positions_daily.open_price
            ,mt4_open_positions_daily.close_price as current_price
            ,mt4_open_positions_daily.snapshot_at
            from custom.mt4_open_positions_daily
            left join report_new.mt4_users_view mu on mu.login=mt4_open_positions_daily.login
            where mt4_open_positions_daily.snapshot_at BETWEEN '"""+date_from_8+"""' and '"""+date_to+"""'
            and mu.`GROUP` not like '%Arch%'
            and mu.`GROUP` not like '%TEST%'
    """
    cursor.execute(query)
    open_positions_mt4 = cursor.fetchall()
    if len(open_positions_mt4) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт8_открытые позиции (MT4).xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','ticket', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','type', bold_title)
        worksheet.write('D1','symbol', bold_title)
        worksheet.write('E1','volume', bold_title)
        worksheet.write('F1','open_time', bold_title)
        worksheet.write('G1','swaps', bold_title)
        worksheet.write('H1','profit', bold_title)
        worksheet.write('I1','currency', bold_title)
        worksheet.write('J1','STATE', bold_title)
        worksheet.write('K1','ZIPCODE', bold_title)
        worksheet.write('L1','open_price', bold_title)
        worksheet.write('M1','current_price', bold_title)
        worksheet.write('N1','snapshot_at', bold_title)
        i = 1
        for openpos_mt4 in open_positions_mt4:
            i += 1
            worksheet.write(f'A{i}',openpos_mt4["ticket"])
            worksheet.write(f'B{i}',openpos_mt4["login"])
            worksheet.write(f'C{i}',openpos_mt4["type"])
            worksheet.write(f'D{i}',openpos_mt4["symbol"])
            worksheet.write(f'E{i}',openpos_mt4["volume"])
            worksheet.write(f'F{i}',str(openpos_mt4["open_time"]))
            worksheet.write(f'G{i}',openpos_mt4["swaps"])
            worksheet.write(f'H{i}',openpos_mt4["profit"])
            worksheet.write(f'I{i}',openpos_mt4["currency"])
            worksheet.write(f'J{i}',openpos_mt4["STATE"])
            worksheet.write(f'K{i}',openpos_mt4["ZIPCODE"])
            worksheet.write(f'L{i}',openpos_mt4["open_price"])
            worksheet.write(f'M{i}',openpos_mt4["current_price"])
            worksheet.write(f'N{i}',str(openpos_mt4["snapshot_at"]))
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Open_positions (MT4)\n'
        mt4 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 9. Cash Back (MT5)
    log_txt.write('9. Cash Back (MT5)\n')
    query = """
            SELECT
            mt5_deals.deal as deal
            ,mu.state
            ,mu.zipcode
            ,mt5_deals.login as login
            ,mt5_deals.profit as amount
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            , mt5_deals.comment
            , mt5_deals.time
            FROM mt5_deals
            LEFT JOIN mt5_users_view mu ON mt5_deals.login = mu.login
            WHERE mt5_deals.comment LIKE '%Cash%'
            and mt5_deals.Action > 1
            AND mt5_deals.time BETWEEN '"""+date_from+"""' and '"""+date_to+"""'
    """
    cursor.execute(query)
    cash_back_report = cursor.fetchall()
    if len(cash_back_report) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт9_Отчет по операциям CASH BACK.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','State', bold_title)
        worksheet.write('C1','ZipCode', bold_title)
        worksheet.write('D1','login', bold_title)
        worksheet.write('E1','amount', bold_title)
        worksheet.write('F1','currency_id', bold_title)
        worksheet.write('G1','comment', bold_title)
        worksheet.write('H1','time', bold_title)
        i = 1
        for cash_back in cash_back_report:
            i += 1
            worksheet.write(f'A{i}',cash_back["deal"])
            worksheet.write(f'B{i}',cash_back["State"])
            worksheet.write(f'C{i}',cash_back["ZipCode"])
            worksheet.write(f'D{i}',cash_back["login"])
            worksheet.write(f'E{i}',cash_back["amount"])
            worksheet.write(f'F{i}',cash_back["currency_id"])
            worksheet.write(f'G{i}',cash_back["comment"])
            worksheet.write(f'H{i}',str(cash_back["time"]))
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Cash Back (MT5)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 10.1. Other / Начисление комиссии по SF-счетам (MT5/MT4)
    log_txt.write('10.1. Other / Начисление комиссии по SF-счетам (MT5/MT4)\n')
    query = """
            SELECT mt5_deals.deal
            ,mt5_deals.login
            ,CASE
            when mu.`Group` like '%EUR%' then 'EUR'
            when mu.`Group` like '%RUR%' then 'RUR'
            ELSE 'USD'
            end  as currency
            ,mu.state
            ,mt5_deals.action
            ,mt5_deals.time as time
            ,cast(mt5_deals.profit as DECIMAL(12,2)) as profit
            ,mt5_deals.comment
            ,'5' as platform
            FROM mt5_deals
            left join mt5_users_view mu on mt5_deals.login = mu.login
            where  mt5_deals.time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt5_deals.action =7
            and  mt5_deals.comment like 'SF%'
            UNION
            SELECT mt4_trades.ticket
            ,mt4_trades.login
            ,CASE
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%RUR%' then 'RUR'
            ELSE 'USD'
            end  as currency
            ,mu.state
            ,mt4_trades.cmd
            ,mt4_trades.close_time as time
            ,cast(mt4_trades.profit as DECIMAL(12,2)) as profit
            ,mt4_trades.comment
            ,'4' as platform
            FROM mt4_trades
            left join mt4_users_view mu on mt4_trades.login = mu.login
            where mt4_trades.close_time between '"""+date_from+"""' and '"""+date_to+"""'
            and  mt4_trades.comment like 'SF %';
    """
    cursor.execute(query)
    others_sf = cursor.fetchall()
    if len(others_sf) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_прочие операции (SwapFree).xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','currency', bold_title)
        worksheet.write('D1','State', bold_title)
        worksheet.write('E1','action', bold_title)
        worksheet.write('F1','time', bold_title)
        worksheet.write('G1','profit', bold_title)
        worksheet.write('H1','comment', bold_title)
        worksheet.write('I1','platform', bold_title)
        i = 1
        for other_sf in others_sf:
            i += 1
            worksheet.write(f'A{i}',other_sf["deal"])
            worksheet.write(f'B{i}',other_sf["login"])
            worksheet.write(f'C{i}',other_sf["currency"])
            worksheet.write(f'D{i}',other_sf["State"])
            worksheet.write(f'E{i}',other_sf["action"])
            worksheet.write(f'F{i}',str(other_sf["time"]))
            worksheet.write(f'G{i}',other_sf["profit"])
            worksheet.write(f'H{i}',other_sf["comment"])
            worksheet.write(f'I{i}',other_sf["platform"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Other / Начисление комиссии по SF-счетам (MT5/MT4)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 10.2. Other / Прочие балансовые операции (MT5/MT4)
    log_txt.write('10.2. Other / Прочие балансовые операции (MT5/MT4)\n')
    query = """
            select 
            mt5_deals.deal
            ,mt5_deals.login
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,trim(mu.state) as customer_id
            ,mt5_deals.action
            ,mt5_deals.time
            ,mt5_deals.profit
            ,mt5_deals.comment
            ,5 as platform
            from mt5_deals
            left join mt5_users_view mu on mt5_deals.login=mu.login
            where mt5_deals.time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt5_deals.action >1
            and mt5_deals.comment not LIKE '%Transfer%'
            and mt5_deals.comment not LIKE '%PAM%'
            and mt5_deals.comment not LIKE '%Cash%'
            and mt5_deals.comment not LIKE '%Cnv%'
            and mt5_deals.comment not LIKE '%Deposit%'
            and mt5_deals.comment not LIKE '%Withdrawal%'
            and mt5_deals.comment not LIKE '%Refund%'
            and mt5_deals.comment not LIKE 'SF %'
            and mu.`Group` not like '%partner%'
            UNION
            select mt4_trades.ticket
            ,mt4_trades.login
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,trim(mu.state) as customer_id
            ,mt4_trades.cmd
            ,close_time
            ,mt4_trades.profit
            ,mt4_trades.comment
            ,4 as platform
            from mt4_trades
            left join mt4_users_view mu on mu.login=mt4_trades.login
            where mt4_trades.close_time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt4_trades.cmd >5
            and mt4_trades.comment not LIKE '%Transfer%'
            and mt4_trades.comment not LIKE '%PAM%'
            and mt4_trades.comment not LIKE 'SF %';
    """
    cursor.execute(query)
    others_balance = cursor.fetchall()
    if len(others_balance) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_прочие операции.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','currency', bold_title)
        worksheet.set_column(0, 2, 10)
        worksheet.write('D1','customer_id', bold_title)
        worksheet.set_column(3, 3, 15)
        worksheet.write('E1','action', bold_title)
        worksheet.set_column(4, 4, 8)
        worksheet.write('F1','time', bold_title)
        worksheet.set_column(5, 5, 20)
        worksheet.write('G1','profit', bold_title)
        worksheet.set_column(6, 6, 10)
        worksheet.write('H1','comment', bold_title)
        worksheet.set_column(7, 7, 12)
        worksheet.write('I1','platform', bold_title)
        worksheet.set_column(8, 8, 10)
        i = 1
        for other_balance in others_balance:
            i += 1
            worksheet.write(f'A{i}',other_balance["deal"])
            worksheet.write(f'B{i}',other_balance["login"])
            worksheet.write(f'C{i}',other_balance["currency"])
            worksheet.write(f'D{i}',other_balance["customer_id"])
            worksheet.write(f'E{i}',other_balance["action"])
            worksheet.write(f'F{i}',str(other_balance["time"]))
            worksheet.write(f'G{i}',other_balance["profit"])
            worksheet.write(f'H{i}',other_balance["comment"])
            worksheet.write(f'I{i}',other_balance["platform"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Other / Прочие балансовые операции (MT5/MT4)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 11. Выплата дивидендов (MT5/MT4)
    log_txt.write('11. Выплата дивидендов (MT5/MT4)\n')
    query = """
            select 
            mt5_deals.deal
            ,mt5_deals.login
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,trim(mu.state) as customer_id
            ,mt5_deals.action
            ,mt5_deals.time
            ,mt5_deals.profit
            ,mt5_deals.comment
            ,5 as platform
            from mt5_deals
            left join mt5_users_view mu on mt5_deals.login=mu.login
            where mt5_deals.time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt5_deals.action >1
            and mt5_deals.comment LIKE 'Dividend adjustment%'
            and mu.`Group` not like '%partner%'
            UNION
            select mt4_trades.ticket
            as deal  
            ,mt4_trades.login
            ,if(mu.`GROUP` like '%EUR%','EUR'
            ,if( mu.`GROUP` like '%RUR%','RUR'
            ,if( mu.`GROUP` like '%CHF%','CHF'
            ,if( mu.`GROUP` like '%GBP%','GBP'
            ,if( mu.`GROUP` like '%JPY%','JPY'
            ,'USD'))))) as currency
            ,trim(mu.state) as customer_id
            ,mt4_trades.cmd as action
            ,close_time as time
            ,mt4_trades.profit
            ,mt4_trades.comment
            ,4 as platform
            from mt4_trades
            left join mt4_users_view mu on mu.login=mt4_trades.login
            where mt4_trades.close_time between '"""+date_from+"""' and '"""+date_to+"""'
            and mt4_trades.cmd >5
            and mt4_trades.comment LIKE 'Dividend adjustment%';
    """
    cursor.execute(query)
    dividends = cursor.fetchall()
    if len(dividends) != 0:
        workbook = xlsxwriter.Workbook(direction+'ACM (margin trading operations)_reports '+str(report_date.year)+'_1-'+str(report_date.day)+' '+month[0:3]+'_пункт 11_dividend adjustment.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        bold_title = workbook.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 25)
        worksheet.write('A1','deal', bold_title)
        worksheet.write('B1','login', bold_title)
        worksheet.write('C1','currency', bold_title)
        worksheet.write('D1','customer_id', bold_title)
        worksheet.write('E1','action', bold_title)
        worksheet.write('F1','time', bold_title)
        worksheet.write('G1','profit', bold_title)
        worksheet.write('H1','comment', bold_title)
        worksheet.write('I1','platform', bold_title)
        i = 1
        for dividend in dividends:
            i += 1
            worksheet.write(f'A{i}',dividend["deal"])
            worksheet.write(f'B{i}',dividend["login"])
            worksheet.write(f'C{i}',dividend["currency"])
            worksheet.write(f'D{i}',dividend["customer_id"])
            worksheet.write(f'E{i}',dividend["action"])
            worksheet.write(f'F{i}',str(dividend["time"]))
            worksheet.write(f'G{i}',dividend["profit"])
            worksheet.write(f'H{i}',dividend["comment"])
            worksheet.write(f'I{i}',dividend["platform"])
        workbook.close()
        log_txt.write('\tотчет готов\n')
        Report_success += '   Выплата дивидендов (MT5/MT4)\n'
        mt5 += 1
    else:
        log_txt.write('\tпо запросу ничего нет\n')
    # 12. Balance (MT4/MT5)
    log_txt.write('12. Balance (MT4/MT5)\n')
    #1 Балансы клиентов на конец месяца
    query = """
            SELECT a1.login
            ,a1.`GROUP`
            ,a1.state
            ,a1.zipcode
            ,ifnull(round(a2.balance,2),0) as balance
            ,a1.currency_id
            from
            (
            SELECT mu.login
            , mu.`GROUP`
            , mu.state
            , mu.zipcode
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            FROM mt4_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login BETWEEN 100000 AND 200000
            UNION
            SELECT 
            mu.login
            , mu.`GROUP`
            , mu.state
            , mu.zipcode
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            FROM mt5_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login > 10000
            ) as a1
            left join
            (
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.swaps) as balance
            FROM mt4_trades mt
            LEFT JOIN mt4_users_view mu on mu.login=mt.login
            where mt.close_time < '"""+date_to+"""'
            and mt.close_time > '1970-01-01 00:00:00'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            group by  mt.login
            union
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.storage) as balance
            FROM mt5_deals mt
            LEFT JOIN mt5_users_view mu on mu.login=mt.login
            where mt.time < '"""+date_to+"""'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            and mu.`GROUP` not LIKE '%manager%'
            group by  mt.login
            ) as a2 on a1.login=a2.login
            LEFT JOIN af_lk.customer_view cv ON a1.State = cv.id
            WHERE cv.is_company !=0
            OR a1.LOGIN IN (815921,815922,815923,815924,815928,815936,815938,815939,815941,815942);
    """
    cursor.execute(query)
    balances = cursor.fetchall()
    workbook_balance = xlsxwriter.Workbook(direction+'ACM_reports__'+str(report_date.day)+'_'+month[0:3]+'_'+str(report_date.year)+'__Balance.xlsx')
    workbook_balance.formats[0].set_font_size(8.5)
    workbook_balance.formats[0].set_font_name('Tahoma')
    bold = workbook_balance.add_format({'bold': True, 'align': 'center','valign': 'vcenter'})
    bold_green = workbook_balance.add_format({'bold': True, 'fg_color': '#C6EFCE', 'align': 'center','valign': 'vcenter'})
    bold_gold = workbook_balance.add_format({'bold': True, 'fg_color': '#FFEB9C', 'align': 'center','valign': 'vcenter'})
    number_format = workbook_balance.add_format({'num_format': '0.00','align': 'right'})
    number_center = workbook_balance.add_format({'num_format': '0.00','align': 'center','valign': 'vcenter'})
    format_center = workbook_balance.add_format({'align': 'center','valign': 'vcenter'})
    currency_format = workbook_balance.add_format({'num_format': '0.0000','align': 'left'})
    percentage = workbook_balance.add_format({'num_format': '0.0%','align': 'center','valign': 'vcenter'})
    worksheet_bylogin = workbook_balance.add_worksheet('by login ')
    worksheet_bylogin.set_default_row(15)
    worksheet_bylogin.set_row(0, 25)
    worksheet_bylogin.write('A1','login', bold)
    worksheet_bylogin.set_column(0, 0, 10)
    worksheet_bylogin.write('B1','GROUP', bold)
    worksheet_bylogin.set_column(1, 1, 23)
    worksheet_bylogin.write('C1','state', bold)
    worksheet_bylogin.write('D1','zipcode', bold)
    worksheet_bylogin.set_column(2, 3, 10)
    worksheet_bylogin.write('E1','balance', bold)
    worksheet_bylogin.write('F1','currency_id', bold)
    worksheet_bylogin.set_column(4, 5, 12)
    worksheet_bylogin.write('G1','open_positions', bold)
    worksheet_bylogin.set_column(6, 6, 17)
    worksheet_bylogin.write('H1','equity', bold)
    worksheet_bylogin.write('I1','balance_usd', bold)
    worksheet_bylogin.write('J1','equity_usd', bold)
    worksheet_bylogin.set_column(7, 9, 14)
    i = 1
    for balance in balances:
        i += 1
        worksheet_bylogin.write(f'A{i}',balance["login"])
        worksheet_bylogin.write(f'B{i}',balance["GROUP"])
        worksheet_bylogin.write(f'C{i}',balance["state"])
        worksheet_bylogin.write(f'D{i}',balance["zipcode"])
        worksheet_bylogin.write(f'E{i}',balance["balance"])
        worksheet_bylogin.write(f'F{i}',balance["currency_id"])
        worksheet_bylogin.write(f'G{i}','=IFERROR(VLOOKUP(A'+str(i)+',V:W,2,0),0)', number_center)
        worksheet_bylogin.write(f'H{i}','=G'+str(i)+'+E'+str(i)+'', number_center)
        worksheet_bylogin.write(f'I{i}','=VLOOKUP(F'+str(i)+',$N$12:$O$17,2,FALSE)*E'+str(i), number_center)
        worksheet_bylogin.write(f'J{i}','=VLOOKUP(F'+str(i)+',$N$12:$O$17,2,FALSE)*H'+str(i), number_center)
    #2 Подитог по валютам
    worksheet_bylogin.set_column(10, 12, 5)
    worksheet_bylogin.write('N1','currency', bold)
    worksheet_bylogin.set_column(13, 13, 10)
    worksheet_bylogin.write('O1','balance, '+str(report_date.day)+' '+month[0:3]+' (ACM)', bold)
    worksheet_bylogin.write('P1','balance, '+str(prev_month_date.day)+' '+month_prev[0:3]+' (ACM)', bold)
    worksheet_bylogin.set_column(14, 15, 24)
    worksheet_bylogin.write('Q1','change, %', bold)
    worksheet_bylogin.write('R1','equity, '+month[0:3], bold)
    worksheet_bylogin.set_column(16, 17, 12)
    worksheet_bylogin.write('S1','equity/balance', bold)
    worksheet_bylogin.set_column(18, 18, 16)
    worksheet_bylogin.write('N2','USD')
    worksheet_bylogin.write('N3','EUR')
    worksheet_bylogin.write('N4','RUR')
    worksheet_bylogin.write('N5','CHF')
    worksheet_bylogin.write('N6','GBP')
    worksheet_bylogin.write('N7','JPY')
    worksheet_bylogin.write('N9','USD')
    for i in range(6):
        worksheet_bylogin.write(f'O{i+2}','=SUMIF(F:F,N'+str(i+2)+',E:E)', number_center)
        worksheet_bylogin.write(f'P{i+2}',0, number_center)
        worksheet_bylogin.write(f'Q{i+2}','=IFERROR((O'+str(i+2)+'-P'+str(i+2)+')/P'+str(i+2)+',"")', percentage)
        worksheet_bylogin.write(f'R{i+2}','=SUMIF(F:F,N'+str(i+2)+',H:H)', number_center)
        worksheet_bylogin.write(f'S{i+2}','=IFERROR(R'+str(i+2)+'/O'+str(i+2)+',0)', percentage)
    worksheet_bylogin.write('O9','=O2+O3*$O$13+O4*$O$12+O5*$O$14+O6*$O$15+O7*$O$16', number_center)
    worksheet_bylogin.write('Q9','=(O9-P9)/P9', percentage)
    worksheet_bylogin.write('R9','=R2+R3*$O$13+R4*$O$12+R5*$O$14+R6*$O$15+R7*$O$16', number_center)
    worksheet_bylogin.write('S9','=R9/O9', percentage)
    query = """
            SELECT a1.currency_id
            , SUM(ifnull(round(a2.balance,2),0)) as balance
            from
            (
            SELECT mu.login
            , mu.state
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            FROM mt4_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login BETWEEN 100000 AND 200000
            UNION
            SELECT 
            mu.login
            , mu.state
            ,CASE
            when mu.`GROUP` like '%RUR%' then 'RUR'
            when mu.`GROUP` like '%EUR%' then 'EUR'
            when mu.`GROUP` like '%CHF%' then 'CHF'
            when mu.`GROUP` like '%GBP%' then 'GBP'
            when mu.`GROUP` like '%JPY%' then 'JPY'
            else 'USD'
            END as currency_id
            FROM mt5_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login > 10000
            ) as a1
            left join
            (
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.swaps) as balance
            FROM mt4_trades mt
            LEFT JOIN mt4_users_view mu on mu.login=mt.login
            where mt.close_time < '"""+date_to_prev+"""'
            and mt.close_time > '1970-01-01 00:00:00'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            group by  mt.login
            union
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.storage) as balance
            FROM mt5_deals mt
            LEFT JOIN mt5_users_view mu on mu.login=mt.login
            where mt.time < '"""+date_to_prev+"""'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            and mu.`GROUP` not LIKE '%manager%'
            group by  mt.login
            ) as a2 on a1.login=a2.login
            LEFT JOIN af_lk.customer_view cv ON a1.State = cv.id
            WHERE cv.is_company !=0
            OR a1.LOGIN IN (815921,815922,815923,815924,815928,815936,815938,815939,815941,815942)
            GROUP BY a1.currency_id
            ORDER BY FIELD(a1.currency_id, 'USD', 'EUR', 'RUR', 'CHF', 'GBP', 'JPY');
    """
    cursor.execute(query)
    currency_balances = cursor.fetchall()
    i = 1
    for currency_balance in currency_balances:
        i += 1
        worksheet_bylogin.write(f'P{i}', currency_balance["balance"], number_center)
    query = """
            SELECT SUM(ifnull(round(a2.balance*af_lk.currency_convert(a1.currency_id, 1, '"""+date_to_prev+"""'),2),0)) as balance
            from
            (
            SELECT mu.login
            , mu.state
            ,CASE
            when mu.`GROUP` like '%RUR%' then 3
            when mu.`GROUP` like '%EUR%' then 2
            when mu.`GROUP` like '%CHF%' then 4
            when mu.`GROUP` like '%GBP%' then 5
            when mu.`GROUP` like '%JPY%' then 6
            else 1
            END as currency_id
            FROM mt4_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login BETWEEN 100000 AND 200000
            UNION
            SELECT 
            mu.login
            , mu.state
            ,CASE
            when mu.`GROUP` like '%RUR%' then 3
            when mu.`GROUP` like '%EUR%' then 2
            when mu.`GROUP` like '%CHF%' then 4
            when mu.`GROUP` like '%GBP%' then 5
            when mu.`GROUP` like '%JPY%' then 6
            else 1
            END as currency_id
            FROM mt5_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login > 10000
            ) as a1
            left join
            (
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.swaps) as balance
            FROM mt4_trades mt
            LEFT JOIN mt4_users_view mu on mu.login=mt.login
            where mt.close_time < '"""+date_to_prev+"""'
            and mt.close_time > '1970-01-01 00:00:00'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            group by  mt.login
            union
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.storage) as balance
            FROM mt5_deals mt
            LEFT JOIN mt5_users_view mu on mu.login=mt.login
            where mt.time < '"""+date_to_prev+"""'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            and mu.`GROUP` not LIKE '%manager%'
            group by  mt.login
            ) as a2 on a1.login=a2.login
            LEFT JOIN af_lk.customer_view cv ON a1.State = cv.id
            WHERE cv.is_company !=0
            OR a1.LOGIN IN (815921,815922,815923,815924,815928,815936,815938,815939,815941,815942);
    """
    cursor.execute(query)
    currency_sum_balance = cursor.fetchone()
    worksheet_bylogin.write('P9', currency_sum_balance["balance"], number_center)
    #3 Профит и свопы на конец месяца
    query = """
            SELECT 
            mt5_positions_daily.login
            ,SUM(mt5_positions_daily.storage) + SUM(mt5_positions_daily.profit) AS sum_profit_storage
            ,mu.state 
            FROM custom.mt5_positions_daily
            left join report_new.mt5_users_view mu on mu.login=mt5_positions_daily.login
            where mt5_positions_daily.snapshot_at BETWEEN '"""+date_from_8+"""' and '"""+date_to+"""'
            and mu.`Group` not LIKE '%TEST%'
            GROUP BY mt5_positions_daily.login
    """
    cursor.execute(query)
    open_pos_sum = cursor.fetchall()
    worksheet_bylogin.set_column(19, 20, 5)
    worksheet_bylogin.write('V1','login', bold)
    worksheet_bylogin.set_column(21, 21, 10)
    worksheet_bylogin.write('W1','profit+storage', bold)
    worksheet_bylogin.set_column(22, 22, 15)
    worksheet_bylogin.set_column(23, 24, 3)
    worksheet_bylogin.write('Z1','State', bold)
    worksheet_bylogin.set_column(25, 25, 10)
    i = 1
    for openpos_sum in open_pos_sum:
        i += 1
        worksheet_bylogin.write(f'V{i}',openpos_sum["login"])
        worksheet_bylogin.write(f'W{i}',openpos_sum["sum_profit_storage"], number_format)
        worksheet_bylogin.write(f'Z{i}',openpos_sum["State"])
    #4 Клиенты, у которых баланс не нулевой на конец месяца
    query = """
            SELECT DISTINCT a1.state
            ,a1.zipcode
            from
            (
            SELECT mu.login
            , mu.state
            , mu.zipcode
            FROM mt4_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login BETWEEN 100000 AND 200000
            UNION
            SELECT 
            mu.login
            , mu.state
            , mu.zipcode
            FROM mt5_users_view mu
            WHERE mu.`GROUP` NOT LIKE '%TEST%'
            AND mu.`GROUP` NOT LIKE '%Arch%'
            AND mu.`GROUP` NOT LIKE '%manager%'
            AND mu.login > 10000
            ) as a1
            left join
            (
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.swaps) as balance
            FROM mt4_trades mt
            LEFT JOIN mt4_users_view mu on mu.login=mt.login
            where mt.close_time < '"""+date_to+"""'
            and mt.close_time > '1970-01-01 00:00:00'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            group by  mt.login
            union
            SELECT mt.login
            ,sum(mt.profit) + sum(mt.storage) as balance
            FROM mt5_deals mt
            LEFT JOIN mt5_users_view mu on mu.login=mt.login
            where mt.time < '"""+date_to+"""'
            and mu.`GROUP` not like '%TEST%'
            and mu.`GROUP` not like '%Arch%'
            and mu.`GROUP` not LIKE '%manager%'
            group by  mt.login
            ) as a2 on a1.login=a2.login
            LEFT JOIN af_lk.customer_view cv ON a1.State = cv.id
            WHERE ( cv.is_company !=0
            OR a1.LOGIN IN (815921,815922,815923,815924,815928,815936,815938,815939,815941,815942))
            AND (ifnull(round(a2.balance,2),0) != 0);
    """
    cursor.execute(query)
    not_null_balance = cursor.fetchall()
    worksheet_bycustomer = workbook_balance.add_worksheet('by customer')
    worksheet_bycustomer.set_default_row(15)
    worksheet_bycustomer.set_row(0, 25)
    worksheet_bycustomer.write('A1','FIO', bold)
    worksheet_bycustomer.set_column(0, 0, 47)
    worksheet_bycustomer.write('B1','type', bold)
    worksheet_bycustomer.write('C1','State', bold)
    worksheet_bycustomer.write('D1','ZipCode', bold)
    worksheet_bycustomer.write('E1','USD', bold_green)
    worksheet_bycustomer.write('F1','EUR', bold_green)
    worksheet_bycustomer.set_column(2, 5, 12)
    worksheet_bycustomer.write('G1','RUR', bold_green)
    worksheet_bycustomer.write('H1','CHF', bold_green)
    worksheet_bycustomer.write('I1','GBP', bold_green)
    worksheet_bycustomer.write('J1','JPY', bold_green)
    worksheet_bycustomer.write('K1','баланс USD', bold_green)
    worksheet_bycustomer.write('L1','USD', bold_gold)
    worksheet_bycustomer.write('M1','EUR', bold_gold)
    worksheet_bycustomer.set_column(10, 12, 12)
    worksheet_bycustomer.write('N1','RUR', bold_gold)
    worksheet_bycustomer.write('O1','CHF', bold_gold)
    worksheet_bycustomer.write('P1','GBP', bold_gold)
    worksheet_bycustomer.write('Q1','JPY', bold_gold)
    worksheet_bycustomer.write('R1','equity_USD', bold_gold)
    worksheet_bycustomer.set_column(17, 17, 12)
    worksheet_bycustomer.write('S1','Residence country', bold)
    worksheet_bycustomer.set_column(18, 18, 20)
    worksheet_bycustomer.write('T1','статус', bold)
    worksheet_bycustomer.set_column(19, 19, 10)
    worksheet_bycustomer.write('U1','citizenship_country', bold)
    worksheet_bycustomer.set_column(20, 20, 24)
    i = 1
    for notnull_balance in not_null_balance:
        i += 1
        worksheet_bycustomer.write(f'A{i}','=VLOOKUP(C'+str(i)+',X:AE,3,0)',format_center)
        worksheet_bycustomer.write(f'B{i}','=VLOOKUP(C'+str(i)+',X:AE,2,0)',format_center)
        worksheet_bycustomer.write(f'C{i}',notnull_balance["state"],format_center)
        worksheet_bycustomer.write(f'D{i}',notnull_balance["zipcode"],format_center)
        worksheet_bycustomer.write(f'E{i}','=SUMIFS(\'by login \'!$E:$E,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!E$1)', number_format)
        worksheet_bycustomer.write(f'F{i}','=SUMIFS(\'by login \'!$E:$E,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!F$1)', number_format)
        worksheet_bycustomer.write(f'G{i}','=SUMIFS(\'by login \'!$E:$E,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!G$1)', number_format)
        worksheet_bycustomer.write(f'H{i}','=SUMIFS(\'by login \'!$E:$E,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!H$1)', number_format)
        worksheet_bycustomer.write(f'I{i}','=SUMIFS(\'by login \'!$E:$E,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!I$1)', number_format)
        worksheet_bycustomer.write(f'J{i}','=SUMIFS(\'by login \'!$E:$E,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!J$1)', number_format)
        worksheet_bycustomer.write(f'K{i}','=SUMIF(\'by login \'!C:C,\'by customer\'!C'+str(i)+',\'by login \'!I:I)', number_center)
        worksheet_bycustomer.write(f'L{i}','=SUMIFS(\'by login \'!$H:$H,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!L$1)', number_format)
        worksheet_bycustomer.write(f'M{i}','=SUMIFS(\'by login \'!$H:$H,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!M$1)', number_format)
        worksheet_bycustomer.write(f'N{i}','=SUMIFS(\'by login \'!$H:$H,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!N$1)', number_format)
        worksheet_bycustomer.write(f'O{i}','=SUMIFS(\'by login \'!$H:$H,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!O$1)', number_format)
        worksheet_bycustomer.write(f'P{i}','=SUMIFS(\'by login \'!$H:$H,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!P$1)', number_format)
        worksheet_bycustomer.write(f'Q{i}','=SUMIFS(\'by login \'!$H:$H,\'by login \'!$C:$C,\'by customer\'!$C'+str(i)+',\'by login \'!$F:$F,\'by customer\'!Q$1)', number_format)
        worksheet_bycustomer.write(f'R{i}','=SUMIF(\'by login \'!C:C,\'by customer\'!C'+str(i)+',\'by login \'!J:J)', number_center)
        worksheet_bycustomer.write(f'S{i}','=VLOOKUP(C'+str(i)+',X:AE,4,0)',format_center)
        worksheet_bycustomer.write(f'T{i}','=VLOOKUP(C'+str(i)+',X:AE,6,0)',format_center)
        worksheet_bycustomer.write(f'U{i}','=VLOOKUP(C'+str(i)+',X:AE,5,0)',format_center)
connection.close()
connection = pymysql.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    db='af_lk',
    charset='utf8mb4',
    cursorclass=DictCursor
)
with connection.cursor() as cursor:
    #5 Курс на конец месяца
    query = """
            select c.code, crh.value
            from currency_rate_history crh
            LEFT JOIN currency c ON crh.from_id = c.id
            where crh.to_id = 1
            and date = DATE('"""+date_to+"""')
            AND crh.from_id !=12
            ORDER BY FIELD(crh.from_id, 3, 2, 4, 5, 6);
    """
    cursor.execute(query)
    currencys = cursor.fetchall()
    worksheet_bylogin.write('N11','RATES:', bold)
    worksheet_bylogin.write('N17','USD')
    i = 11
    for currency in currencys:
        i += 1
        worksheet_bylogin.write(f'N{i}',currency["code"])
        worksheet_bylogin.write(f'O{i}',currency["value"], currency_format)
    worksheet_bylogin.write('O17',1, currency_format )
    #6 Данные по компаниям
    query = """
            select c.id as customer_id
            ,if(c.is_company=1,"le","ind") as entity_type
            ,if(c.is_company=0,concat(ci.last_name_en," ",ci.first_name_en," ",ifnull(ci.middle_name_en,"")),cc.name) as FIO
            ,if(c.is_company=0,coun.name,coun2.name) as residence_country
            ,if(c.is_company=0,coun3.name,coun2.name) as citizenship_country
            ,cs.name as status
            ,if(c.is_company=0,0,cc.contract_number) as contract_number
            from customer_view c
            inner join customer_agreement ca on ca.customer_id=c.id
            left join customer_individual ci on ci.customer_id=c.id
            left join customer_company cc on cc.customer_id=c.id
            left join country coun on coun.id=ci.country_id
            left join country coun2 on coun2.id=cc.country_id
            left join country coun3 on coun3.id=ci.citizenship_country_id
            left join customer_status cs on cs.id=c.status_id
            left join customer_info cin on cin.customer_id=c.id
            where c.is_deleted = 0
            UNION 
            SELECT  muv.State as customer_id
            ,'le' as entity_type
            , muv.Name as FIO
            , muv.Country as residence_country
            , muv.Country as citizenship_country
            , 'checked' as status 
            , muv.State as contract_number
            FROM report_new.mt5_users_view muv
            WHERE muv.Login IN (815921,815922,815923,815924,815928,815936,815938,815939,815941,815942)
    """
    cursor.execute(query)
    companys = cursor.fetchall()
    worksheet_bycustomer.write('X1','customer_id', bold)
    worksheet_bycustomer.set_column(23, 23, 13.5)
    worksheet_bycustomer.write('Y1','entity_type', bold)
    worksheet_bycustomer.set_column(24, 24, 13)
    worksheet_bycustomer.write('Z1','FIO', bold)
    worksheet_bycustomer.set_column(25, 25, 53)
    worksheet_bycustomer.write('AA1','residence_country', bold)
    worksheet_bycustomer.set_column(26, 26, 25)
    worksheet_bycustomer.write('AB1','citizenship_country', bold)
    worksheet_bycustomer.set_column(27, 27, 41)
    worksheet_bycustomer.write('AC1','status', bold)
    worksheet_bycustomer.set_column(28, 28, 22)
    worksheet_bycustomer.write('AD1','contract_number', bold)
    worksheet_bycustomer.set_column(29, 29, 19)
    i = 1
    for company in companys:
        i += 1
        worksheet_bycustomer.write(f'X{i}',company["customer_id"])
        worksheet_bycustomer.write(f'Y{i}',company["entity_type"])
        worksheet_bycustomer.write(f'Z{i}',company["FIO"])
        worksheet_bycustomer.write(f'AA{i}',company["residence_country"])
        worksheet_bycustomer.write(f'AB{i}',company["citizenship_country"])
        worksheet_bycustomer.write(f'AC{i}',company["status"])
        worksheet_bycustomer.write(f'AD{i}',company["contract_number"])
connection.close()
workbook_balance.close()
xl = win32com.client.DispatchEx('Excel.Application')
xl.Visible = False
wb = xl.Workbooks.Open(direction+"ACM_reports__"+str(report_date.day)+"_"+month[0:3]+"_"+str(report_date.year)+"__Balance.xlsx")
wb.Close(True)
log_txt.write('\tотчет готов\n')
Report_success += '   Balance (MT4/MT5)\n'
mt5 += 1
log_txt.write('из MT5 выгружено '+str(mt5)+' отчетов из 13 (всего '+str(mt4+mt5)+' отчетов из 17)')
log_txt.write('конец расчета: '+str(datetime.datetime.now()))
log_txt.close()

Report_ACM = """*Выгрузка отчетов для ACM*

Отчетный месяц: *"""+month+""" """+str(report_date.year)+"""*.

Выгружено из MT5 *"""+str(mt5)+""" / 13* отчетов (всего: *"""+str(mt4+mt5)+""" / 17*):
*"""+Report_success+"""*"""

telegram_bot(Report_ACM)
#print(Report_ACM)
