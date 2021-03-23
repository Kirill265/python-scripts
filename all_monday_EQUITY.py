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
Postgre_connection_2 = psycopg2.connect(
    host='172.16.1.42',
    port=5433,
    user=postgre_username,
    password=postgre_password,
    dbname='mt5_report'
)
month_number_dict = {"1":'январь',"2":'февраль',"3":'март',"4":'апрель',"5":'май',"6":'июнь',"7":'июль',"8":'август',"9":'сентябрь',"10":'октябрь',"11":'ноябрь',"12":'декабрь'} 
now = datetime.datetime.now()
#report_date = now - timedelta(days=now.day)
monday = now - timedelta(days=calendar.weekday(now.year, now.month, now.day))
report_date = monday - timedelta(days=3) + timedelta(days=3)
month = month_number_dict[str(report_date.month)]
if report_date.month < 10:
    sql_month = '0'+str(report_date.month)
else:
    sql_month = str(report_date.month)
date_from = str(report_date.year)+'-'+sql_month+'-01 00:00:00'
date_to = str(report_date.year)+'-'+sql_month+'-'+str(report_date.day)+' 23:59:59'
direction = 'C:/Users/Kirill_Cherkasov/Documents/Reports/weekly_EQUITY/new/'
os.mkdir(direction+'01-'+str(report_date.day)+' '+month+' '+str(report_date.year))
direction += '01-'+str(report_date.day)+' '+month+' '+str(report_date.year)+'/'
workbook_26 = xlsxwriter.Workbook(direction+'01-'+str(report_date.day)+' '+month+' '+str(report_date.year)+'_equity.xlsx')
workbook_26.formats[0].set_font_size(8.5)
workbook_26.formats[0].set_font_name('Tahoma')
bold_blue_26 = workbook_26.add_format({'bold': True, 'fg_color': '#DDEBF7', 'align': 'center','valign': 'vcenter'})
number26 = workbook_26.add_format({'num_format': '0.00','align': 'right'})
percentage26 = workbook_26.add_format({'num_format': '0.00%','align': 'center','valign': 'vcenter'})
percentage26.set_font_size(8.5)
percentage26.set_font_name('Tahoma')
worksheet_26PL = workbook_26.add_worksheet('PL')
#worksheet_26PL.set_default_row(10.5)
worksheet_26PL.set_row(0, 15)
worksheet_26PL.write('A1', 'Login', bold_blue_26)
worksheet_26PL.write('B1', 'UTM', bold_blue_26)
worksheet_26PL.write('C1', 'LK', bold_blue_26)
worksheet_26PL.write('D1', 'Currency', bold_blue_26)
worksheet_26PL.write('E1', 'Deposit', bold_blue_26)
worksheet_26PL.write('F1', 'Withdrawal', bold_blue_26)
worksheet_26PL.write('G1', 'Volume Lots', bold_blue_26)
worksheet_26PL.set_column(0, 6, 15)
worksheet_26PL.write('H1', 'Convertation out', bold_blue_26)
worksheet_26PL.write('I1', 'Convertation in', bold_blue_26)
worksheet_26PL.set_column(7, 8, 18)
worksheet_26PL.write('J1', 'Equity '+str(report_date.day)+'.'+sql_month, bold_blue_26)
worksheet_26PL.write('K1', 'Balance 1.'+sql_month, bold_blue_26)
worksheet_26PL.write('L1', 'Balance '+str(report_date.day)+'.'+sql_month, bold_blue_26)
worksheet_26PL.set_column(9, 11, 15)
worksheet_26PL.write('M1', 'P/L (+Commission)', bold_blue_26)
worksheet_26PL.set_column(12, 12, 20)
worksheet_26Deals = workbook_26.add_worksheet('Deals')
#worksheet_26Deals.set_default_row(10.5)
worksheet_26Deals.set_row(0, 15)
worksheet_26Deals.write('A1', 'Deal', bold_blue_26)
worksheet_26Deals.set_column(0, 0, 12)
worksheet_26Deals.write('B1', 'Order', bold_blue_26)
worksheet_26Deals.set_column(1, 1, 15)
worksheet_26Deals.write('C1', 'Login', bold_blue_26)
worksheet_26Deals.write('D1', 'UTM', bold_blue_26)
worksheet_26Deals.set_column(2, 3, 12)
worksheet_26Deals.write('E1', 'Time', bold_blue_26)
worksheet_26Deals.set_column(4, 4, 20)
worksheet_26Deals.write('F1', 'Type', bold_blue_26)
worksheet_26Deals.write('G1', 'Entry', bold_blue_26)
worksheet_26Deals.set_column(5, 6, 8.5)
worksheet_26Deals.write('H1', 'Symbol', bold_blue_26)
worksheet_26Deals.set_column(7, 7, 13)
worksheet_26Deals.write('I1', 'Volume', bold_blue_26)
worksheet_26Deals.set_column(8, 8, 8.5)
worksheet_26Deals.write('J1', 'Volume USD', bold_blue_26)
worksheet_26Deals.set_column(9, 9, 13)
worksheet_26Deals.write('K1', 'Price', bold_blue_26)
worksheet_26Deals.set_column(10, 10, 8.5)
worksheet_26Deals.write('L1', 'Reason', bold_blue_26)
worksheet_26Deals.set_column(11, 11, 13)
worksheet_26Deals.write('M1', 'Profit', bold_blue_26)
worksheet_26Deals.set_column(12, 12, 8.5)
worksheet_26Deals.write('N1', 'Dealer', bold_blue_26)
worksheet_26Deals.set_column(13, 13, 13)
worksheet_26Deals.write('O1', 'Currency', bold_blue_26)
worksheet_26Deals.set_column(14, 14, 8.5)
worksheet_26ML = workbook_26.add_worksheet('Margin Level')
#worksheet_26ML.set_default_row(10.5)
worksheet_26ML.set_row(0, 15)
worksheet_26ML.write('A1', 'Login', bold_blue_26)
worksheet_26ML.write('B1', 'UTM', bold_blue_26)
worksheet_26ML.write('C1', 'LK', bold_blue_26)
worksheet_26ML.write('D1', 'Currency', bold_blue_26)
worksheet_26ML.set_column(0, 3, 15)
worksheet_26ML.write('E1', 'Margin Level '+str(report_date.day)+'.'+sql_month, bold_blue_26)
worksheet_26ML.set_column(4, 4, 20)
with my_connection.cursor() as cursor:
    query = """
            SELECT 
            CONCAT("'",c.universal_id,"',") AS UID_for_Postgre 
            FROM customer c
/*
            SELECT 
            CONCAT("'",c.universal_id,"',") AS UID_for_Postgre 
            FROM customer_utm cu
            LEFT JOIN customer c ON cu.customer_id = c.id
            LEFT JOIN utm u ON cu.utm_id = u.id
*/
     """
    cursor.execute(query)
    UIDS = cursor.fetchall()
    customer_id = ''
    for UID in UIDS:
        customer_id += UID["UID_for_Postgre"]
    query = """
            SELECT CONCAT(a.login,',') AS login_comma
            FROM account a
            LEFT JOIN customer_utm cu ON a.customer_id = cu.customer_id
            LEFT JOIN utm u ON cu.utm_id = u.id
            ORDER BY Login
     """
    cursor.execute(query)
    logins_comma = cursor.fetchall()
    login_for_mt5 = ''
    for login_comma in logins_comma:
        login_for_mt5 += login_comma["login_comma"]
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
with Postgre_connection_2.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:    
    query = """
            SELECT mt5a."Login"
            , ROUND(COALESCE(Dps.Deposit,0)::NUMERIC,2) AS Deposit
            , ROUND(COALESCE(-Wth.Withdrawal,0)::NUMERIC,2) AS Withdrawal
            , ROUND(COALESCE(PL.profit,0)::NUMERIC,2) AS Profit
            FROM mt5_accounts mt5a
            LEFT JOIN (
            SELECT "Login", SUM("Profit") AS profit FROM mt5_deals
            WHERE "Action" IN (0,1,7)
            AND "TimeMsc" BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            GROUP BY "Login") AS PL ON mt5a."Login" = PL."Login"
            LEFT JOIN (
            SELECT "Login", SUM("Profit") AS Deposit FROM mt5_deals
            WHERE "Action" = 2
            AND  "TimeMsc" BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND (
            "Comment" = ''
            OR
            "Comment" LIKE '%Deposit%'
            OR
            "Comment" LIKE '%Возврат%'
            OR
            "Comment" LIKE '%Refund%'
            )
            GROUP BY "Login") AS Dps ON Dps."Login" = mt5a."Login"
            LEFT JOIN (
            SELECT "Login", SUM("Profit") AS Withdrawal FROM mt5_deals
            WHERE "Action" = 2
            AND  "TimeMsc" BETWEEN \'"""+date_from+"""\' AND \'"""+date_to+"""\'
            AND (
            "Comment" LIKE '%Withdrawal%'
            OR
            "Comment" LIKE '%Удержание%'
            OR
            "Comment" LIKE '%удержание%'
            )
            GROUP BY "Login") AS Wth ON Wth."Login" = mt5a."Login" 
            WHERE mt5a."Login" IN (
            """+login_for_mt5[:-1]+"""
            );
    """
    cursor.execute(query)
    OPRDS_plus_PL = cursor.fetchall()
    OPRDS_PL_dict = {}
    for OPRDS_PL in OPRDS_plus_PL:
        OPRDS_PL_dict[str(OPRDS_PL["Login"])] = {"deposit":OPRDS_PL["deposit"], "withdrawal":OPRDS_PL["withdrawal"], "profit":OPRDS_PL["profit"]}
Postgre_connection_2.close()
with my_connection.cursor() as cursor:
    query = """
            SET @@time_zone = "+3:00";
     """
    cursor.execute(query)
    query = """
            SELECT a.login AS 'Login'
            , u.utm_source AS 'UTM'
            , a.customer_id AS 'LK'
            , c.name AS 'Currency'
            , IFNULL(ROUND(pmd.volume_sum, 2), 0) AS 'Volume_Lots'
            , IFNULL(ROUND(EquityTo.Equity,2),0) AS Equity_to
            , IFNULL(ROUND(EquityFrom.Balance,2),0) AS Balance_from
            , IFNULL(ROUND(EquityTo.Balance,2),0) AS Balance_to
            , IFNULL(ROUND(EquityTo.MarginLevel/100,4),0) AS Margin_Level
            FROM account a
            LEFT JOIN currency c ON a.currency_id = c.id
            LEFT JOIN customer_utm cu ON a.customer_id = cu.customer_id
            LEFT JOIN utm u ON cu.utm_id = u.id 
            LEFT JOIN
            (
            SELECT platform_mt5_deal.login
            , SUM(platform_mt5_deal.volume) AS volume_sum
            FROM platform_mt5_deal 
            WHERE platform_mt5_deal.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            GROUP BY platform_mt5_deal.login
            ) AS pmd ON pmd.login = a.login
              LEFT JOIN
            (
            SELECT
            m5ad1.login
            , m5ad1.MarginLevel
            , m5ad1.Balance
            , m5ad1.Equity
            FROM mt5_events.mt5accountdaily m5ad1
            WHERE DATE(DATE_ADD("1970-01-01 00:00:00", INTERVAL ROUND(m5ad1.TimestampMS/1000 - 3600, 0) SECOND)) = DATE(\""""+date_to+"""\")
            ) AS EquityTo ON a.login = EquityTo.login
            LEFT JOIN
            (
            SELECT
            m5ad2.login
            , m5ad2.Balance
            FROM mt5_events.mt5accountdaily m5ad2
            WHERE DATE(DATE_ADD("1970-01-01 00:00:00", INTERVAL ROUND(m5ad2.TimestampMS/1000 - 3600, 0) SECOND)) = DATE(DATE_ADD(\""""+date_from+"""\", INTERVAL -1 DAY))
            ) AS EquityFrom ON a.login = EquityFrom.login
            ORDER BY Login
     """
    cursor.execute(query)
    PL_all = cursor.fetchall()
    i = 1
    for PL_one in PL_all:
        i += 1
        worksheet_26PL.write(f'A{i}', PL_one["Login"])
        worksheet_26PL.write(f'B{i}', PL_one["UTM"])
        worksheet_26PL.write(f'C{i}', PL_one["LK"])
        worksheet_26PL.write(f'D{i}', PL_one["Currency"])
        worksheet_26PL.write(f'E{i}', OPRDS_PL_dict[str(PL_one["Login"])]["deposit"], number26)
        worksheet_26PL.write(f'F{i}', OPRDS_PL_dict[str(PL_one["Login"])]["withdrawal"], number26)
        worksheet_26PL.write(f'G{i}', PL_one["Volume_Lots"], number26)
        try:
            worksheet_26PL.write(f'H{i}', convertation_dict[str(PL_one["Login"])]["out"], number26)
            worksheet_26PL.write(f'I{i}', convertation_dict[str(PL_one["Login"])]["in"], number26)
        except KeyError:
            worksheet_26PL.write(f'H{i}', 0.00, number26)
            worksheet_26PL.write(f'I{i}', 0.00, number26)
        worksheet_26PL.write(f'J{i}', PL_one["Equity_to"], number26)
        worksheet_26PL.write(f'K{i}', PL_one["Balance_from"], number26)
        worksheet_26PL.write(f'L{i}', PL_one["Balance_to"], number26)
        worksheet_26PL.write(f'M{i}', OPRDS_PL_dict[str(PL_one["Login"])]["profit"], number26)
        worksheet_26PL.write(f'N{i}', '=K'+str(i)+'+E'+str(i)+'-F'+str(i)+'+H'+str(i)+'+I'+str(i)+'+M'+str(i)+'-L'+str(i), number26)
        worksheet_26ML.write(f'A{i}', PL_one["Login"])
        worksheet_26ML.write(f'B{i}', PL_one["UTM"])
        worksheet_26ML.write(f'C{i}', PL_one["LK"])
        worksheet_26ML.write(f'D{i}', PL_one["Currency"])
        worksheet_26ML.write(f'E{i}', PL_one["Margin_Level"],percentage26)
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
            ORDER BY Deal
    """
    cursor.execute(query)
    Deals = cursor.fetchall()
    l = 1
    for Deal in Deals:
        l += 1
        worksheet_26Deals.write(f'A{l}', Deal["Deal"])
        worksheet_26Deals.write(f'B{l}', Deal["Order"])
        worksheet_26Deals.write(f'C{l}', Deal["Login"])
        worksheet_26Deals.write(f'D{l}', Deal["UTM"])
        worksheet_26Deals.write(f'E{l}', str(Deal["Time"]))
        worksheet_26Deals.write(f'F{l}', Deal["Type"])
        worksheet_26Deals.write(f'G{l}', Deal["Entry"])
        worksheet_26Deals.write(f'H{l}', Deal["Symbol"])
        worksheet_26Deals.write(f'I{l}', Deal["Volume"], number26)
        worksheet_26Deals.write(f'J{l}', Deal["Volume_USD"], number26)
        worksheet_26Deals.write(f'K{l}', Deal["Price"])
        worksheet_26Deals.write(f'L{l}', Deal["Reason"])
        worksheet_26Deals.write(f'M{l}', Deal["Profit"], number26)
        worksheet_26Deals.write(f'N{l}', Deal["Dealer"])
        worksheet_26Deals.write(f'O{l}', Deal["Currency"])
my_connection.close()
workbook_26.close()

Report_24_26 = """[Отчет по агенту 24](https://team.alfaforex.com/servicedesk/view/11160)

Отчетная дата: *"""+str(report_date.day)+""" """+month+""" """+str(report_date.year)+"""*.

26 агент: *"""+str(i-1)+"""* счетов
Конвертирующих счетов: *"""+str(len(convertations))+"""*"""

#telegram_bot(Report_24_26)
#print(Report_24_26)