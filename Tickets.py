import requests
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
import xlsxwriter
import datetime
#import calendar
from datetime import timedelta
from TeamWox import TW_text_file

def telegram_bot(Report: str):
    api_token = '1362203438:AAFNp5tXRWi6Pn5RkIgqq_7ELHdGTbY9CUs'
    requests.get('https://api.telegram.org/bot{}/sendMessage'.format(api_token), params=dict(
        chat_id='-1001156138635',
        parse_mode= 'Markdown',
        text=Report 
))

hostname='172.16.1.42'
portnum = 3307
username = 'kcherkasov'
password = '6ne6H7O3ikVUvmDc570AMfmIgTSXZkcOI'
connection = pymysql.connect(
    host=hostname,
    port=portnum,
    user=username,
    password=password,
    db='my',
    charset='utf8mb4',
    cursorclass=DictCursor
)
now = datetime.datetime.now()
report_date = now - timedelta(days=now.day)
report_month_start = report_date.month - 2
qarte = int(report_date.month/3)
if report_month_start < 10:
    msg_from_month = '0'+str(report_month_start)
else:
    msg_from_month = str(report_month_start)

if report_date.month < 10:
    msg_to_month = '0'+str(report_date.month)
else:
    msg_to_month = str(report_date.month)
date_from = str(report_date.year)+'-'+msg_from_month+'-01 00.00.00'
date_to = str(report_date.year)+'-'+msg_to_month+'-'+str(report_date.day)+' 23.59.59'
direction = 'C:/Users/Kirill_Cherkasov/Documents/Reports/Tickets/'
workbook = xlsxwriter.Workbook(direction+'Тикеты '+str(qarte)+' квартал '+str(report_date.year)+' года.xlsx')
workbook.formats[0].set_font_size(8.5)
workbook.formats[0].set_font_name('Tahoma')
border = workbook.add_format({'border': 1,'align': 'center','valign': 'vcenter'})
border.set_font_size(8.5)
border.set_font_name('Tahoma')
border_left = workbook.add_format({'border': 1,'align': 'left','valign': 'vcenter'})
border_left.set_font_size(8.5)
border_left.set_font_name('Tahoma')
border_right = workbook.add_format({'border': 1,'align': 'right','valign': 'vcenter'})
border_right.set_font_size(8.5)
border_right.set_font_name('Tahoma')
worksheet = workbook.add_worksheet()
worksheet.set_default_row(10)
worksheet.set_row(0, 15)
worksheet.write('A1', 'login')
worksheet.set_column(0, 0, 15)
worksheet.write('B1', 'id')
worksheet.set_column(1, 1, 6)
worksheet.write('C1', 'time')
worksheet.set_column(2, 2, 12)
worksheet.write('D1', 'rate')
worksheet.set_column(3, 3, 7)
worksheet.write('F2', 'Всего тикетов',border_left)
worksheet.set_column(5, 5, 18)
worksheet.write('G1', 'Тикеты',border)
worksheet.set_column(6, 6, 7)
worksheet.write('H1', 'Среднее время (мин)',border)
worksheet.set_column(7, 7, 19)
worksheet.write('I1', 'Средняя оценка',border)
worksheet.set_column(8, 8, 15)
worksheet.write('K1', 'login')
worksheet.set_column(10, 10, 15)
worksheet.write('L1', 'id')
worksheet.set_column(11, 11, 6)
worksheet.write('M1', 'time')
worksheet.set_column(12, 12, 12)
worksheet.write('N1', 'rate')
worksheet.set_column(13, 13, 7)
with connection.cursor() as cursor:
    query = """
            SET @@time_zone = \"+3:00\";
    """
    cursor.execute(query)
    query = """
            SELECT
            m.login
            , t.id
            ,  CASE
            WHEN TIMEDIFF(tc.created_at, t.created_at) < 0 THEN TIMEDIFF(t.created_at, tc.created_at)
            ELSE TIMEDIFF(tc.created_at, t.created_at)
            END AS 'Time_answer'
            ,  CASE
            WHEN TIMEDIFF(tc.created_at, t.created_at) < 0 THEN '-'
            ELSE '+'
            END AS 'direct'
            , t.rate
            FROM (SELECT tc.ticket_id
            , MIN(tc.id) AS first_tic
            FROM ticket_comment tc
            WHERE tc.is_customer = 0
            GROUP BY tc.ticket_id
            ) AS tcc
            LEFT JOIN ticket_comment tc ON tcc.first_tic = tc.id
            LEFT JOIN ticket t ON tc.ticket_id = t.id
            LEFT JOIN manager m ON tc.manager_id = m.id
            WHERE t.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND tc.manager_id != 107
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60 > 0
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60/60 < 24
            ORDER BY m.login, t.id ;
    """
    cursor.execute(query)
    Tickets_all = cursor.fetchall()
    query = """
            SELECT
            m.login
            , CONCAT(m.last_name,' ',m.first_name) AS FIO
            , COUNT(t.id) AS count_ticket
            , ROUND(AVG(TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))) / 60, 0) AS average_time_of_answer_min
            FROM (SELECT tc.ticket_id
            , MIN(tc.id) AS first_tic
            FROM ticket_comment tc
            WHERE tc.is_customer = 0
            GROUP BY tc.ticket_id
            ) AS tcc
            LEFT JOIN ticket_comment tc ON tcc.first_tic = tc.id
            LEFT JOIN ticket t ON tc.ticket_id = t.id
            LEFT JOIN manager m ON tc.manager_id = m.id
            WHERE t.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND tc.manager_id != 107
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60 > 0
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60/60 < 24
            GROUP BY m.login
    """
    cursor.execute(query)
    Tickets_agr = cursor.fetchall()
    query = """
            SELECT
            m.login
            , t.id
            ,  CASE
            WHEN TIMEDIFF(tc.created_at, t.created_at) < 0 THEN TIMEDIFF(t.created_at, tc.created_at)
            ELSE TIMEDIFF(tc.created_at, t.created_at)
            END AS 'Time_answer'
            ,  CASE
            WHEN TIMEDIFF(tc.created_at, t.created_at) < 0 THEN '-'
            ELSE '+'
            END AS 'direct'
            , t.rate
            FROM (SELECT tc.ticket_id
            , MIN(tc.id) AS first_tic
            FROM ticket_comment tc
            WHERE tc.is_customer = 0
            GROUP BY tc.ticket_id
            ) AS tcc
            LEFT JOIN ticket_comment tc ON tcc.first_tic = tc.id
            LEFT JOIN ticket t ON tc.ticket_id = t.id
            LEFT JOIN manager m ON tc.manager_id = m.id
            WHERE t.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND tc.manager_id != 107
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60 > 0
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60/60 < 24
            HAVING t.rate != 0
            ORDER BY m.login, t.id ;
    """
    cursor.execute(query)
    Tickets_with_rates = cursor.fetchall()
    query = """
            SELECT
            m.login
            , ROUND(AVG(rate),1) AS avg_rate
            FROM (SELECT tc.ticket_id
            , MIN(tc.id) AS first_tic
            FROM ticket_comment tc
            WHERE tc.is_customer = 0
            GROUP BY tc.ticket_id
            ) AS tcc
            LEFT JOIN ticket_comment tc ON tcc.first_tic = tc.id
            LEFT JOIN ticket t ON tc.ticket_id = t.id
            LEFT JOIN manager m ON tc.manager_id = m.id
            WHERE t.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
            AND tc.manager_id != 107
            AND t.rate != 0
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60 > 0
            -- AND TIME_TO_SEC(TIMEDIFF(tc.created_at, t.created_at))/60/60 < 24
            GROUP BY m.login;
    """
    cursor.execute(query)
    Ticets_avg_rates = cursor.fetchall()
    rates_dict = {}
    for avg_rates in Ticets_avg_rates:
        rates_dict[avg_rates["login"]] = avg_rates["avg_rate"]
    j = 1
    for Ticket in Tickets_all:
        j += 1
        worksheet.write(f'A{j}', Ticket["login"])
        worksheet.write(f'B{j}', Ticket["id"])
        worksheet.write(f'C{j}', Ticket["direct"]+str(Ticket["Time_answer"]))
        worksheet.write(f'D{j}', Ticket["rate"])
    i = 2
    for Ticket_avg in Tickets_agr:
        i += 1
        worksheet.write(f'F{i}', Ticket_avg["FIO"],border_left)
        worksheet.write(f'G{i}', Ticket_avg["count_ticket"],border_right)
        worksheet.write(f'H{i}', Ticket_avg["average_time_of_answer_min"],border_right)
        try:
            worksheet.write(f'I{i}', rates_dict[Ticket_avg["login"]],border_right)
        except KeyError:
            worksheet.write(f'I{i}', '=0',border_right)
    worksheet.write(f'G{2}', '='+str(j-1),border_right)
    worksheet.write(f'F{1}', '',border)
    worksheet.write(f'H{2}', '',border)
    worksheet.write(f'I{2}', '',border)
    k = 1
    for Ticket in Tickets_with_rates:
        k += 1
        worksheet.write(f'K{k}', Ticket["login"])
        worksheet.write(f'L{k}', Ticket["id"])
        worksheet.write(f'M{k}', Ticket["direct"]+str(Ticket["Time_answer"]))
        worksheet.write(f'N{k}', Ticket["rate"])
    workbook.close()
connection.close()

Report_Tickets = """[Тикеты](https://team.alfaforex.com/servicedesk/view/11230)

За """+str(qarte)+""" квартал """+str(report_date.year)+""":
01."""+msg_from_month+"""."""+str(report_date.year)+""" - """+str(report_date.day)+"""."""+msg_to_month+"""."""+str(report_date.year)+"""
Всего """+str(j-1)+""" тикетов по """+str(i-2)+""" сотрудникам."""

telegram_bot(Report_Tickets)
#print(Report_Tickets)

URL_TW = "https://team.alfaforex.com/servicedesk/view/11230"
message_text = ''
attached_file = "C:\\Users\\Kirill_Cherkasov\\Documents\\Reports\\Tickets\\"+"Тикеты "+str(qarte)+" квартал "+str(report_date.year)+" года.xlsx"

TW_text_file(URL_TW,message_text,attached_file)
