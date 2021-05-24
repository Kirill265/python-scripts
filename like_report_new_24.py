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
    worksheet_OpenP = workbook_.add_worksheet('Opened positions')
    #worksheet_OpenP.set_default_row(10.5)
    worksheet_OpenP.set_row(0, 15)
    worksheet_OpenP.write('A1', 'Position', bold_blue_)
    worksheet_OpenP.write('B1', 'Login', bold_blue_)
    worksheet_OpenP.set_column(0, 1, 12)
    worksheet_OpenP.write('C1', 'UTM', bold_blue_)
    worksheet_OpenP.set_column(2, 2, 10)
    worksheet_OpenP.write('D1', 'Opened', bold_blue_)
    worksheet_OpenP.write('E1', 'Last updated', bold_blue_)
    worksheet_OpenP.set_column(3, 4, 20)
    worksheet_OpenP.write('F1', 'Action', bold_blue_)
    worksheet_OpenP.write('G1', 'Symbol', bold_blue_)
    worksheet_OpenP.write('H1', 'Volume', bold_blue_)
    worksheet_OpenP.write('I1', 'Price', bold_blue_)
    worksheet_OpenP.write('J1', 'Reason', bold_blue_)
    worksheet_OpenP.set_column(5, 9, 12)
    worksheet_OpenP.write('K1', 'Floating PL', bold_blue_)
    worksheet_OpenP.set_column(10, 10, 15)
    worksheet_OpenP.write('L1', 'Dealer', bold_blue_)
    worksheet_OpenP.write('M1', 'Currency', bold_blue_)
    worksheet_OpenP.set_column(11, 12, 12)
    worksheet_CloseP = workbook_.add_worksheet('Closed positions')
    #worksheet_CloseP.set_default_row(10.5)
    worksheet_CloseP.set_row(0, 15)
    worksheet_CloseP.write('A1', 'Position', bold_blue_)
    worksheet_CloseP.write('B1', 'Login', bold_blue_)
    worksheet_CloseP.set_column(0, 1, 12)
    worksheet_CloseP.write('C1', 'UTM', bold_blue_)
    worksheet_CloseP.set_column(2, 2, 10)
    worksheet_CloseP.write('D1', 'Opened', bold_blue_)
    worksheet_CloseP.write('E1', 'Closed', bold_blue_)
    worksheet_CloseP.set_column(3, 4, 20)
    worksheet_CloseP.write('F1', 'Action', bold_blue_)
    worksheet_CloseP.write('G1', 'Symbol', bold_blue_)
    worksheet_CloseP.write('H1', 'Volume', bold_blue_)
    worksheet_CloseP.write('I1', 'Price', bold_blue_)
    worksheet_CloseP.write('J1', 'Reason', bold_blue_)
    worksheet_CloseP.set_column(5, 9, 15)
    worksheet_CloseP.write('K1', 'Profit', bold_blue_)
    worksheet_CloseP.set_column(10, 10, 15)
    worksheet_CloseP.write('L1', 'Dealer', bold_blue_)
    worksheet_CloseP.write('M1', 'Currency', bold_blue_)
    worksheet_CloseP.set_column(11, 12, 12)
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
                SET SQL_BIG_SELECTS = 1;
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
                select
                mtp.PositionId as 'PositionId',
                mtp.Login as 'Login',
                u.utm_source as 'UTM',
                DATE_ADD("1970-01-01 00:00:00", INTERVAL ROUND(mtp.TimeCreateMs/1000 - 3600, 0) SECOND) as 'Opened',
                DATE_ADD("1970-01-01 00:00:00", INTERVAL ROUND(mtp.TimeUpdateMs/1000 - 3600, 0) SECOND) as 'Updated',
                IF(mtp.Action = 1, "sell", "buy") as 'Action',
                mtp.Symbol as 'Symbol',
                Round(mtp.Vol/10000,2) as 'Volume_Lots',
                mtp.PriceOpen AS 'Price',
                CASE
                WHEN mtp.Reason = 0 THEN 'Client'
                WHEN mtp.Reason = 1 THEN 'Expert'
                WHEN mtp.Reason = 2 THEN 'Dealer'
                WHEN mtp.Reason = 3 THEN 'Stop loss'
                WHEN mtp.Reason = 4 THEN 'Take profit'
                WHEN mtp.Reason = 5 THEN 'Stop out'
                WHEN mtp.Reason = 16 THEN 'Mobile'
                WHEN mtp.Reason = 17 THEN 'Web'
                ELSE mtp.Reason
                END AS 'Reason',
                ROUND(mtp.Profit,2) AS 'Profit',
                mtp.Dealer AS 'Dealer',
                UPPER(c.name) AS 'Currency'
                from mt5_events.mt5positiondaily mtp
                left join account a on a.login = mtp.Login
                left join currency c on c.id = a.currency_id
                left join customer_utm cu on cu.customer_id = a.customer_id
                left join utm u on u.id = cu.utm_id
                left join mt5_events.mt5events mte on mte.HKey = mtp.HKey and mte.LKey = mtp.LKey
                Where u.utm_source in ("""+sources_utm+""")
                and DATE(DATE_ADD("1970-01-01 00:00:00", INTERVAL ROUND(mte.TimestampMs/1000 - 3600, 0) SECOND)) = DATE(\""""+date_to+"""\")
                order by mtp.Login desc
        """
        cursor.execute(query)
        OpenPos = cursor.fetchall()
        m = 1
        for OpenP in OpenPos:
            m += 1
            worksheet_OpenP.write(f'A{m}', OpenP["PositionId"])
            worksheet_OpenP.write(f'B{m}', OpenP["Login"])
            worksheet_OpenP.write(f'C{m}', OpenP["UTM"])
            worksheet_OpenP.write(f'D{m}', str(OpenP["Opened"]))
            worksheet_OpenP.write(f'E{m}', str(OpenP["Updated"]))
            worksheet_OpenP.write(f'F{m}', OpenP["Action"])
            worksheet_OpenP.write(f'G{m}', OpenP["Symbol"])
            worksheet_OpenP.write(f'H{m}', OpenP["Volume_Lots"], number)
            worksheet_OpenP.write(f'I{m}', OpenP["Price"])
            worksheet_OpenP.write(f'J{m}', OpenP["Reason"])
            worksheet_OpenP.write(f'K{m}', OpenP["Profit"], number)
            worksheet_OpenP.write(f'L{m}', OpenP["Dealer"])
            worksheet_OpenP.write(f'M{m}', OpenP["Currency"])
        query = """
                select pmd_l.expert_position_id as 'position', 
                pmd_l.created_at as 'Closed' 
                from (
                select max(pmd_last.id) as 'deal' from platform_mt5_deal pmd_last
                group by pmd_last.expert_position_id) as last_id
                join platform_mt5_deal pmd_l on pmd_l.id = last_id.deal
                left join account a_l on a_l.login = pmd_l.login
                LEFT JOIN customer_utm cu_l ON a_l.customer_id = cu_l.customer_id
                LEFT JOIN utm u_l ON cu_l.utm_id = u_l.id
                WHERE u_l.utm_source IN ("""+sources_utm+""")
                and pmd_l.created_at between \""""+date_from+"""\" and \""""+date_to+"""\"
        """
        cursor.execute(query)
        last_deals = cursor.fetchall()
        LD_str = ''
        LD_dict = {}
        for last_deal in last_deals:
            LD_str += str(last_deal["position"])+','
            LD_dict[str(last_deal["position"])] = {"Closed":str(last_deal["Closed"])}
        query = """
                select pmd_f.expert_position_id as 'position',
                pmd_f.created_at as 'Opened',
                IF(pmd_f.action = 1, "sell", "buy") as 'Action',
                u_f.utm_source as 'UTM',
                pmd_f.login as 'Login',
                pmd_f.Symbol as 'Symbol',
                pmd_f.price as 'PriceOpen',
                CASE
                WHEN pmd_f.Reason = 0 THEN 'Client'
                WHEN pmd_f.Reason = 1 THEN 'Expert'
                WHEN pmd_f.Reason = 2 THEN 'Dealer'
                WHEN pmd_f.Reason = 3 THEN 'Stop loss'
                WHEN pmd_f.Reason = 4 THEN 'Take profit'
                WHEN pmd_f.Reason = 5 THEN 'Stop out'
                WHEN pmd_f.Reason = 16 THEN 'Mobile'
                WHEN pmd_f.Reason = 17 THEN 'Web'
                ELSE pmd_f.Reason 
                END AS 'Reason',
                pmd_f.dealer_id as 'Dealer',
                UPPER(c_f.name) as 'Currency'
                from (
                select min(pmd_first.id) as 'deal' from platform_mt5_deal pmd_first
                group by pmd_first.expert_position_id) as first_id
                join platform_mt5_deal pmd_f on pmd_f.id = first_id.deal
                left join account a_f on a_f.login = pmd_f.login
                LEFT JOIN currency c_f ON a_f.currency_id = c_f.id
                LEFT JOIN customer_utm cu_f ON a_f.customer_id = cu_f.customer_id
                LEFT JOIN utm u_f ON cu_f.utm_id = u_f.id
                WHERE u_f.utm_source IN ("""+sources_utm+""")
                and pmd_f.expert_position_id in ("""+LD_str[:-1]+""")
        """
        cursor.execute(query)
        first_deals = cursor.fetchall()
        FD_dict = {}
        for first_deal in first_deals:
            FD_dict[str(first_deal["position"])] =  {"Opened":str(first_deal["Opened"]), "Action":first_deal["Action"], "UTM":first_deal["UTM"], "Login":first_deal["Login"], "Symbol":first_deal["Symbol"], "PriceOpen":first_deal["PriceOpen"], "Reason":first_deal["Reason"], "Dealer":first_deal["Dealer"], "Currency":first_deal["Currency"]}
        query = """
                select pmd_cl.expert_position_id as 'PositionId',
                ROUND(SUM(pmd_cl.volume)/2,2) as 'Volume_Lots',
                ROUND(SUM(pmd_cl.profit),2) as 'Profit'
                from platform_mt5_deal pmd_cl
                left join account a_cl on a_cl.login = pmd_cl.login
                LEFT JOIN customer_utm cu_cl ON a_cl.customer_id = cu_cl.customer_id
                LEFT JOIN utm u_cl ON cu_cl.utm_id = u_cl.id
                WHERE u_cl.utm_source IN ("""+sources_utm+""")
                and pmd_cl.created_at <= \""""+date_to+"""\"
                and pmd_cl.expert_position_id in ("""+LD_str[:-1]+""")
                group by pmd_cl.expert_position_id
                HAVING SUM(pmd_cl.volume*IF(pmd_cl.action = 0, 1, -1)) = 0
        """
        cursor.execute(query)
        ClosePos = cursor.fetchall()
        l = 1
        for CloseP in ClosePos:
            l += 1
            worksheet_CloseP.write(f'A{l}', CloseP["PositionId"])
            worksheet_CloseP.write(f'B{l}', FD_dict[str(CloseP["PositionId"])]["Login"])
            worksheet_CloseP.write(f'C{l}', FD_dict[str(CloseP["PositionId"])]["UTM"])
            worksheet_CloseP.write(f'D{l}', str(FD_dict[str(CloseP["PositionId"])]["Opened"]))
            worksheet_CloseP.write(f'E{l}', str(LD_dict[str(CloseP["PositionId"])]["Closed"]))
            worksheet_CloseP.write(f'F{l}', FD_dict[str(CloseP["PositionId"])]["Action"])
            worksheet_CloseP.write(f'G{l}', FD_dict[str(CloseP["PositionId"])]["Symbol"])
            worksheet_CloseP.write(f'H{l}', CloseP["Volume_Lots"], number)
            worksheet_CloseP.write(f'I{l}', FD_dict[str(CloseP["PositionId"])]["PriceOpen"])
            worksheet_CloseP.write(f'J{l}', FD_dict[str(CloseP["PositionId"])]["Reason"])
            worksheet_CloseP.write(f'K{l}', CloseP["Profit"], number)
            worksheet_CloseP.write(f'L{l}', FD_dict[str(CloseP["PositionId"])]["Dealer"])
            worksheet_CloseP.write(f'M{l}', FD_dict[str(CloseP["PositionId"])]["Currency"])
    my_connection.close()
    workbook_.close()
    xl = win32com.client.DispatchEx('Excel.Application')
    xl.Visible = False
    wb = xl.Workbooks.Open(direction+agent+" 01-"+msg_to_day+" "+month+" "+str(report_date.year)+".xlsx")
    wb.Close(True)
    to_return = {}
    to_return["conv_count"] = str(len(convertations))
    to_return["acc_count"] = str(j-1)
    to_return["open_count"] = str(m-1)
    return to_return
