import sys
import pymysql
from pymysql.cursors import DictCursor
import xlsxwriter
from TeamWox import TW_text_file
import time
import shutil
from keepass import key_pass

def volume_USD(send_info, name=""):
    date_from = send_info["date_from"]
    date_to = send_info["date_to"]
    if name == "":
        direction = send_info["direction"]
        msg_from_day = send_info["msg_from_day"]
        msg_to_day = send_info["msg_to_day"]
        msg_from_month = send_info["msg_from_month"]
        msg_to_month = send_info["msg_to_month"]
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
    if name == "":
        if msg_from_day != '':
            workbook = xlsxwriter.Workbook(direction+'Оборот USD '+msg_from_day+'.'+msg_from_month+' - '+msg_to_day+'.'+msg_to_month+'.xlsx')
        else:
            workbook = xlsxwriter.Workbook(direction+'Оборот USD '+msg_to_day+'.'+msg_to_month+'.xlsx')
        workbook.formats[0].set_font_size(8.5)
        workbook.formats[0].set_font_name('Tahoma')
        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(15)
        worksheet.set_row(0, 17)
        worksheet.write('A1', 'Symbol')
        worksheet.set_column(0, 0, 10)
        worksheet.write('B1', 'Volume USD')
        worksheet.set_column(1, 1, 15)
    with connection.cursor() as cursor:
        
        query = """
                SET @@time_zone = \"+3:00\";
        """
        cursor.execute(query)
        query = """
                SELECT COUNT(DISTINCT pmd.symbol) AS symbols
                FROM platform_mt5_deal pmd
                WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\";
        """
        cursor.execute(query)
        count_symbol = cursor.fetchone()
        query = """
                SELECT SUBSTRING(pmd.symbol,1,6) AS symbol
                , ROUND(SUM(pmd.volume_usd),0) AS volume_usd 
                FROM platform_mt5_deal pmd
                WHERE pmd.created_at BETWEEN \""""+date_from+"""\" AND \""""+date_to+"""\"
                GROUP BY pmd.symbol
                ORDER BY symbol;
        """
        cursor.execute(query)
        Volumes_USD = cursor.fetchall()
        j = 1
        Report = ""
        for Volume_USD in Volumes_USD:
            if name == "":
                j += 1
                worksheet.write(f'A{j}', Volume_USD["symbol"])
                worksheet.write(f'B{j}', Volume_USD["volume_usd"])
            else:
                Report += '\n'+Volume_USD["symbol"]+': \t\t'+str(Volume_USD["volume_usd"])+'.00'
        if name == "":
            workbook.close()
    connection.close()
    return_dict = {}
    return_dict["count_symbol"] = str(count_symbol["symbols"])
    return_dict["report"] = Report
    return return_dict
