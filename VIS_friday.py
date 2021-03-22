import requests
import sys
import os
import calendar
import datetime
from datetime import timedelta
import xlsxwriter
import pymysql
import psycopg2
from psycopg2.extras import DictCursor
from pymysql.cursors import DictCursor

def telegram_bot(Report: str):
    api_token = '1362203438:AAFNp5tXRWi6Pn5RkIgqq_7ELHdGTbY9CUs'
    requests.get('https://api.telegram.org/bot{}/sendMessage'.format(api_token), params=dict(
        chat_id='-1001156138635',
        parse_mode= 'Markdown',
        text=Report 
))
    
my_username = 'kcherkasov'
my_password = '6ne6H7O3ikVUvmDc570AMfmIgTSXZkcOI'
my_connection = pymysql.connect(
    host='172.16.1.42',
    port=3307,
    user=my_username,
    password=my_password,
    db='my',
    charset='utf8mb4',
    cursorclass=DictCursor
)
postgre_username = 'kcherkasov'
postgre_password = 'fg8GerFulLmDdWw4PhDjy4u5iIDLc7mW7rTUJBRNkCDcSGCs'
Postgre_connection = psycopg2.connect(
    host='172.16.1.42',
    port=5433,
    user=postgre_username,
    password=postgre_password,
    dbname='finance'
)
month_number_dict = {"1":'январь',"2":'февраль',"3":'март',"4":'апрель',"5":'май',"6":'июнь',"7":'июль',"8":'август',"9":'сентябрь',"10":'октябрь',"11":'ноябрь',"12":'декабрь'} 
now = datetime.datetime.now()
wday = calendar.weekday(now.year, now.month, now.day)
if wday in [4,5,6]:
    report_date = now - timedelta(days=(calendar.weekday(now.year, now.month, now.day)-3))
else:
    report_date = now - timedelta(days=(calendar.weekday(now.year, now.month, now.day)+4))
month = month_number_dict[str(report_date.month)]
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
date_from = str(report_date.year)+'-'+sql_month+'-01 00:00:00'
date_to = str(report_date.year)+'-'+sql_month+'-'+str(report_date.day)+' 23:59:59'
direction = 'C:/Users/Kirill_Cherkasov/Documents/Reports/VIS Consulting_weekly/formulas/'
os.mkdir(direction+'01-'+str(report_date.day)+' '+month+' '+str(report_date.year))
direction += '01-'+str(report_date.day)+' '+month+' '+str(report_date.year)+'/'
workbook_ = xlsxwriter.Workbook(direction+'VISconsulting 01-'+str(report_date.day)+' '+month+' '+str(report_date.year)+'.xlsx')
workbook_.formats[0].set_font_size(8.5)
workbook_.formats[0].set_font_name('Tahoma')
bold_blue_ = workbook_.add_format({'bold': True, 'fg_color': '#DDEBF7', 'align': 'center','valign': 'vcenter'})
number = workbook_.add_format({'num_format': '0.00','align': 'right'})
percentage = workbook_.add_format({'num_format': '0.00%','align': 'center','valign': 'vcenter'})
percentage.set_font_size(8.5)
percentage.set_font_name('Tahoma')
worksheet_PL = workbook_.add_worksheet('PL')
#worksheet_PL.set_default_row(10.5)
worksheet_PL.set_row(0, 15)
worksheet_PL.write('A1', 'Login', bold_blue_)
worksheet_PL.write('B1', 'UTM', bold_blue_)
worksheet_PL.write('C1', 'LK', bold_blue_)
worksheet_PL.write('D1', 'Currency', bold_blue_)
worksheet_PL.write('E1', 'Deposit', bold_blue_)
worksheet_PL.write('F1', 'Withdrawal', bold_blue_)
worksheet_PL.write('G1', 'Volume Lots', bold_blue_)
worksheet_PL.set_column(0, 6, 15)
worksheet_PL.write('H1', 'Convertation out', bold_blue_)
worksheet_PL.write('I1', 'Convertation in', bold_blue_)
worksheet_PL.set_column(7, 8, 18)
worksheet_PL.write('J1', 'Equity '+str(report_date.day)+'.'+sql_month, bold_blue_)
worksheet_PL.write('K1', 'Balance 1.'+sql_month, bold_blue_)
worksheet_PL.write('L1', 'Balance '+str(report_date.day)+'.'+sql_month, bold_blue_)
worksheet_PL.set_column(9, 11, 15)
worksheet_PL.write('M1', 'P/L (+Commission)', bold_blue_)
worksheet_PL.set_column(12, 12, 20)
worksheet_Deals = workbook_.add_worksheet('Deals')
#worksheet_Deals.set_default_row(10.5)
worksheet_Deals.set_row(0, 15)
worksheet_Deals.write('A1', 'Deal', bold_blue_)
worksheet_Deals.set_column(0, 0, 12)
worksheet_Deals.write('B1', 'Order', bold_blue_)
worksheet_Deals.set_column(1, 1, 15)
worksheet_Deals.write('C1', 'Login', bold_blue_)
worksheet_Deals.write('D1', 'UTM', bold_blue_)
worksheet_Deals.set_column(2, 3, 12)
worksheet_Deals.write('E1', 'Time', bold_blue_)
worksheet_Deals.set_column(4, 4, 20)
worksheet_Deals.write('F1', 'Type', bold_blue_)
worksheet_Deals.write('G1', 'Entry', bold_blue_)
worksheet_Deals.set_column(5, 6, 8.5)
worksheet_Deals.write('H1', 'Symbol', bold_blue_)
worksheet_Deals.set_column(7, 7, 13)
worksheet_Deals.write('I1', 'Volume', bold_blue_)
worksheet_Deals.set_column(8, 8, 8.5)
worksheet_Deals.write('J1', 'Volume USD', bold_blue_)
worksheet_Deals.set_column(9, 9, 13)
worksheet_Deals.write('K1', 'Price', bold_blue_)
worksheet_Deals.set_column(10, 10, 8.5)
worksheet_Deals.write('L1', 'Reason', bold_blue_)
worksheet_Deals.set_column(11, 11, 13)
worksheet_Deals.write('M1', 'Profit', bold_blue_)
worksheet_Deals.set_column(12, 12, 8.5)
worksheet_Deals.write('N1', 'Dealer', bold_blue_)
worksheet_Deals.set_column(13, 13, 13)
worksheet_Deals.write('O1', 'Currency', bold_blue_)
worksheet_Deals.set_column(14, 14, 8.5)
worksheet_ML = workbook_.add_worksheet('Margin Level')
#worksheet_ML.set_default_row(10.5)
worksheet_ML.set_row(0, 15)
worksheet_ML.write('A1', 'Login', bold_blue_)
worksheet_ML.write('B1', 'UTM', bold_blue_)
worksheet_ML.write('C1', 'LK', bold_blue_)
worksheet_ML.write('D1', 'Currency', bold_blue_)
worksheet_ML.set_column(0, 3, 15)
worksheet_ML.write('E1', 'Margin Level '+str(report_date.day)+'.'+sql_month, bold_blue_)
worksheet_ML.set_column(4, 4, 20)
with my_connection.cursor() as cursor:
    query = """
            SELECT 
            CONCAT("'",c.universal_id,"',") AS UID_for_Postgre 
            FROM customer_utm cu
            LEFT JOIN customer c ON cu.customer_id = c.id
            LEFT JOIN utm u ON cu.utm_id = u.id
            WHERE u.utm_source IN (
            '77af'
            )
     """
    cursor.execute(query)
    UIDS = cursor.fetchall()
    customer_id = ''
    for UID in UIDS:
        customer_id += UID["UID_for_Postgre"]
with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:    
    query = """
            SELECT a.login, 
            COALESCE(conv_from.amount, 0.00) as volume_out
            ,COALESCE(conv_to.amount, 0.00) AS volume_in
            FROM account a
            LEFT JOIN 
            (SELECT
            a_from.login AS login
            , SUM(ROUND(- c.amount_from / 100.0, 2)) AS amount
            FROM convertation c
            LEFT JOIN account a_from ON c.account_id_from = a_from.id
            WHERE c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND c.status = 3
            GROUP BY a_from.login
            ) AS conv_from ON conv_from.login = a.login
            LEFT JOIN 
            ( SELECT
            a_to.login AS login
            , SUM(ROUND(c.amount_to / 100.0, 2)) AS amount
            FROM convertation c
            LEFT JOIN account a_to ON c.account_id_to = a_to.id
            WHERE c.created_at BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND c.status = 3
            GROUP BY a_to.login
            ) AS conv_to ON conv_to.login = a.login
            WHERE (conv_from.amount IS NOT NULL
            OR conv_to.amount IS NOT NULL
            )
            AND a.customer_id IN (
            -- id клиентов
            """+customer_id[:-1]+"""
            ) 
            ORDER BY a.login
    """
    cursor.execute(query)
    convertations = cursor.fetchall()
    convertation_dict = {}
    for convertation in convertations:
        convertation_dict[str(convertation["login"])] = {"out":convertation["volume_out"], "in":convertation["volume_in"]}
Postgre_connection.close()
with my_connection.cursor() as cursor:
    query = """
            SET @@time_zone = "+3:00";
     """
    cursor.execute(query)
    query = """
            SELECT a.login AS 'Login'
            , CONCAT(ci.last_name_ru,' ',SUBSTRING(ci.first_name_ru,1,1),'.',SUBSTRING(ci.middle_name_ru,1,1),'.') AS 'FIO'
            , u.utm_source AS 'UTM'
            , a.customer_id AS 'LK'
            , c.name AS 'Currency'
            , IFNULL(ROUND(dr.deposit_sum, 2), 0) AS 'Deposit'
            , IFNULL(ROUND(wr.withdrawal_sum, 2), 0) AS 'Withdrawal'
            , IFNULL(ROUND(pmd.volume_sum, 2), 0) AS 'Volume_Lots'
            FROM account a
            LEFT JOIN currency c ON a.currency_id = c.id
            LEFT JOIN customer_individual ci ON a.customer_id = ci.customer_id
            LEFT JOIN customer_utm cu ON a.customer_id = cu.customer_id
            LEFT JOIN customer c1 ON a.customer_id = c1.id
            LEFT JOIN utm u ON cu.utm_id = u.id 
            LEFT JOIN 
            (
            SELECT deposit_request.account_id
            , SUM(deposit_request.amount) AS deposit_sum 
            FROM deposit_request
            WHERE deposit_request.status_id = 10 AND deposit_request.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY deposit_request.account_id
            ) AS dr ON a.id = dr.account_id
            LEFT JOIN 
            (
            SELECT withdrawal_request.account_id
            , SUM(withdrawal_request.amount) AS withdrawal_sum 
            FROM withdrawal_request
            WHERE withdrawal_request.status_id = 17 AND withdrawal_request.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY withdrawal_request.account_id
            ) AS wr ON a.id = wr.account_id
            LEFT JOIN
            (
            SELECT platform_mt5_deal.login
            , SUM(platform_mt5_deal.volume) AS volume_sum
            , SUM(platform_mt5_deal.volume_usd) AS volume_usd_sum
            FROM platform_mt5_deal 
            WHERE platform_mt5_deal.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY platform_mt5_deal.login
            ) AS pmd ON pmd.login = a.login
            WHERE u.utm_source IN (
            '77af'
            )
            ORDER BY Login
     """
    cursor.execute(query)
    PL_all = cursor.fetchall()
    j = 1
    for PL_one in PL_all:
        j += 1
        worksheet_PL.write(f'A{j}', PL_one["Login"])
        worksheet_PL.write(f'B{j}', PL_one["UTM"])
        worksheet_PL.write(f'C{j}', PL_one["LK"])
        worksheet_PL.write(f'D{j}', PL_one["Currency"])
        worksheet_PL.write(f'E{j}', PL_one["Deposit"], number)
        worksheet_PL.write(f'F{j}', PL_one["Withdrawal"], number)
        worksheet_PL.write(f'G{j}', PL_one["Volume_Lots"], number)
        try:
            worksheet_PL.write(f'H{j}', convertation_dict[str(PL_one["Login"])]["out"], number)
            worksheet_PL.write(f'I{j}', convertation_dict[str(PL_one["Login"])]["in"], number)
        except KeyError:
            worksheet_PL.write(f'H{j}', 0.00, number)
            worksheet_PL.write(f'I{j}', 0.00, number)
        worksheet_PL.write(f'J{j}', '=VLOOKUP(A'+str(j)+',[Segregated.xlsx]Sheet1!$A$3:$K$1000000,11,0)', number)
        worksheet_PL.write(f'K{j}', '=VLOOKUP(A'+str(j)+',[Segregated1.xlsx]Sheet1!$A$3:$I$1000000,9,0)', number)
        worksheet_PL.write(f'L{j}', '=VLOOKUP(A'+str(j)+',[Segregated.xlsx]Sheet1!$A$3:$I$1000000,9,0)', number)
        worksheet_PL.write(f'M{j}', '=VLOOKUP(A'+str(j)+',[Segregated.xlsx]Sheet1!$A$3:$G$1000000,7,0)+VLOOKUP(A'+str(j)+',[Segregated.xlsx]Sheet1!$A$3:$E$1000000,5,0)', number)
        worksheet_PL.write(f'N{j}', '=K'+str(j)+'+E'+str(j)+'-F'+str(j)+'+H'+str(j)+'+I'+str(j)+'+M'+str(j)+'-L'+str(j), number)
        worksheet_ML.write(f'A{j}', PL_one["Login"])
        worksheet_ML.write(f'B{j}', PL_one["UTM"])
        worksheet_ML.write(f'C{j}', PL_one["LK"])
        worksheet_ML.write(f'D{j}', PL_one["Currency"])
        worksheet_ML.write(f'E{j}', '=IFERROR(VLOOKUP(A'+str(j)+',\'[Daily Reports.xlsx]Sheet1\'!$B$3:$J$1000000,9,0)/VLOOKUP(A'+str(j)+',\'[Daily Reports.xlsx]Sheet1\'!$B$3:$K$1000000,10,0),0)',percentage)
    query = """
            SELECT
            pmd.id AS 'Deal'
            , pmd.mt5_order_id AS 'Order'
            , pmd.login AS 'Login'
            , u.utm_source AS 'UTM'
            , pmd.created_at AS 'Time'
            , IF(pmd.action = 0, 'buy', 'sell') AS 'Type'
            , IF(pmd.entry = 0, 'in', IF(pmd.entry = 1, 'out', 'in/out')) AS 'Entry'
            , pmd.symbol AS 'Symbol'
            , pmd.volume AS 'Volume'
            , pmd.volume_usd AS 'Volume_USD'
            , pmd.price AS 'Price'
            , CASE
            WHEN pmd.reason = 0 THEN 'Client'
            WHEN pmd.reason = 1 THEN 'Expert'
            WHEN pmd.reason = 2 THEN 'Dealer'
            WHEN pmd.reason = 3 THEN 'Stop loss'
            WHEN pmd.reason = 4 THEN 'Take profit'
            WHEN pmd.reason = 5 THEN 'Stop out'
            WHEN pmd.reason = 16 THEN 'Mobile'
            WHEN pmd.reason = 17 THEN 'Web'
            ELSE pmd.reason
            END AS 'Reason'
            , pmd.profit AS 'Profit'
            , pmd.dealer_id AS 'Dealer'
            , UPPER(c.name) AS 'Currency'
            FROM platform_mt5_deal pmd
            LEFT JOIN account a ON pmd.login = a.login
            LEFT JOIN currency c ON a.currency_id = c.id
            LEFT JOIN customer_utm cu ON a.customer_id = cu.customer_id
            LEFT JOIN utm u ON cu.utm_id = u.id
            WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND (
            u.utm_source IN (
            '77af'
            )
            )
            ORDER BY Deal
    """
    cursor.execute(query)
    Deals = cursor.fetchall()
    m = 1
    for Deal in Deals:
        m += 1
        worksheet_Deals.write(f'A{m}', Deal["Deal"])
        worksheet_Deals.write(f'B{m}', Deal["Order"])
        worksheet_Deals.write(f'C{m}', Deal["Login"])
        worksheet_Deals.write(f'D{m}', Deal["UTM"])
        worksheet_Deals.write(f'E{m}', str(Deal["Time"]))
        worksheet_Deals.write(f'F{m}', Deal["Type"])
        worksheet_Deals.write(f'G{m}', Deal["Entry"])
        worksheet_Deals.write(f'H{m}', Deal["Symbol"])
        worksheet_Deals.write(f'I{m}', Deal["Volume"], number)
        worksheet_Deals.write(f'J{m}', Deal["Volume_USD"], number)
        worksheet_Deals.write(f'K{m}', Deal["Price"])
        worksheet_Deals.write(f'L{m}', Deal["Reason"])
        worksheet_Deals.write(f'M{m}', Deal["Profit"], number)
        worksheet_Deals.write(f'N{m}', Deal["Dealer"])
        worksheet_Deals.write(f'O{m}', Deal["Currency"])
my_connection.close()
workbook_.close()

Report_VIS = """[Отчет по VIS](https://team.alfaforex.com/servicedesk/view/11503)

Отчетная дата: *"""+str(report_date.day)+""" """+month+""" """+str(report_date.year)+"""*.

Счетов: *"""+str(j-1)+"""*
Торговых операций: *"""+str(m-1)+"""*
Конвертирующих счетов: *"""+str(len(convertations))+"""*"""

#telegram_bot(Report_VIS)
#print(Report_VIS)
