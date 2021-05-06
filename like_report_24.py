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
import time
from keepass import key_pass
from win32com import client
import win32com

def report_generation(send_info):
    agent = send_info["agent"]
    sources_utm = send_info["sources_utm"]
    direction = send_info["direction"]
    date_from = send_info["date_from"]
    date_to = send_info["date_to"]
    msg_to_day = send_info["msg_to_day"]
    month = send_info["month"]
    sql_month = send_info["sql_month"]
    report_date = send_info["report_date"]
    SQL_DB = 'MySQL DB PROD'
    my_connection = pymysql.connect(
        host=key_pass(SQL_DB).url[:-5],
        port=int(key_pass(SQL_DB).url[-4:]),
        user=key_pass(SQL_DB).username,
        password=key_pass(SQL_DB).password,
        db='my',
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    SQL_DB = 'PotgreSQL DB PROD'
    Postgre_connection = psycopg2.connect(
        host=key_pass(SQL_DB).url[:-5],
        port=int(key_pass(SQL_DB).url[-4:]),
        user=key_pass(SQL_DB).username,
        password=key_pass(SQL_DB).password,
        dbname='finance'
    )
    SQL_DB = 'PotgreSQL DB PROD'
    Postgre_connection_2 = psycopg2.connect(
        host=key_pass(SQL_DB).url[:-5],
        port=int(key_pass(SQL_DB).url[-4:]),
        user=key_pass(SQL_DB).username,
        password=key_pass(SQL_DB).password,
        dbname='mt5_report'
    )
    workbook_ = xlsxwriter.Workbook(direction+agent+' 01-'+msg_to_day+' '+month+' '+str(report_date.year)+'.xlsx')
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
    worksheet_Deals.write('F1', 'Action', bold_blue_)
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
                WHERE u.utm_source IN ("""+sources_utm+""")
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
                WHERE u.utm_source IN ("""+sources_utm+""")
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
                WHERE u.utm_source IN ("""+sources_utm+""")
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
            worksheet_PL.write(f'E{j}', OPRDS_PL_dict[str(PL_one["Login"])]["deposit"], number)
            worksheet_PL.write(f'F{j}', OPRDS_PL_dict[str(PL_one["Login"])]["withdrawal"], number)
            worksheet_PL.write(f'G{j}', PL_one["Volume_Lots"], number)
            try:
                worksheet_PL.write(f'H{j}', convertation_dict[str(PL_one["Login"])]["out"], number)
                worksheet_PL.write(f'I{j}', convertation_dict[str(PL_one["Login"])]["in"], number)
            except KeyError:
                worksheet_PL.write(f'H{j}', 0.00, number)
                worksheet_PL.write(f'I{j}', 0.00, number)
            worksheet_PL.write(f'J{j}', PL_one["Equity_to"], number)
            worksheet_PL.write(f'K{j}', PL_one["Balance_from"], number)
            worksheet_PL.write(f'L{j}', PL_one["Balance_to"], number)
            worksheet_PL.write(f'M{j}', OPRDS_PL_dict[str(PL_one["Login"])]["profit"], number)
            worksheet_ML.write(f'A{j}', PL_one["Login"])
            worksheet_ML.write(f'B{j}', PL_one["UTM"])
            worksheet_ML.write(f'C{j}', PL_one["LK"])
            worksheet_ML.write(f'D{j}', PL_one["Currency"])
            worksheet_ML.write(f'E{j}', PL_one["Margin_Level"],percentage)
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
                u.utm_source IN ("""+sources_utm+""")
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
    xl = win32com.client.DispatchEx('Excel.Application')
    xl.Visible = False
    wb = xl.Workbooks.Open(direction+agent+" 01-"+msg_to_day+" "+month+" "+str(report_date.year)+".xlsx")
    wb.Close(True)
    to_return = {}
    to_return["conv_count"] = str(len(convertations))
    to_return["acc_count"] = str(j-1)
    to_return["oper_count"] = str(m-1)
    return to_return
