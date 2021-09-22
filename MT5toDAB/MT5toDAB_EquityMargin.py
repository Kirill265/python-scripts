import sys
import os
import shutil
import re
import datetime
import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass

class Form(QMainWindow):
    def direct(self,message):
        return QFileDialog.getExistingDirectory(self,message,"./")
    def inform(self,message,information):
        return QMessageBox.information(self, message, information)
    def getid(self,title,message):
        deal_id = QInputDialog.getText(self, title, message)[0]
        while not re.fullmatch(r'\d{10}', deal_id):
            deal_id = QInputDialog.getText(self, title, message)[0]
        return deal_id

app = QApplication(sys.argv)
explorer = Form()
first_deal = explorer.getid("Deal","Первая сделка")
last_deal = explorer.getid("Deal","Последняя сделка")
result_dir = explorer.direct("Укажите путь для сохранения")+'/'
result_dir = os.path.join(result_dir, 'MT5toDAB_EquityMargin_result')
if not os.path.exists(result_dir):
    os.mkdir(result_dir)
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
    Select distinct DATE("TimeMsc") as "date_rep" from public.mt5_deals where "Deal" between """+str(first_deal)+""" AND """+str(last_deal)+""";
    """
    cursor.execute(query)
    deals_date = cursor.fetchall()
    for date_rep in deals_date:
        query = """
                SELECT "Login", "ProfitEquity", "Currency" FROM public.mt5_daily
                WHERE DATE('1970-01-01 00:00:00'::timestamp + "Datetime"*INTERVAL'1 SECOND' - INTERVAL'1 HOUR') = DATE('"""+str(date_rep["date_rep"])+"""')
        -- AND "ProfitEquity" != 0
        """
        cursor.execute(query)
        equity = cursor.fetchall()
        equty_dict = {}
        for login in equity:
            equty_dict[login["Login"]] = {"equity":round(float(login["ProfitEquity"]),2), "currency":login["Currency"]}
        now = datetime.datetime.now()
        print(str(date_rep["date_rep"])+':\tstart\t'+str(datetime.datetime.now()))
        print(str(date_rep["date_rep"])+':\tquery\t'+str(datetime.datetime.now()))
        query = """
                SELECT "for_join".*
        -- , Coalesce("daily"."ProfitEquity",0)
                FROM (
                SELECT "md_over"."Deal"
                , "md_over"."Login" 
                , ROUND(ABS("md_over"."obyaz_after" - "md_over"."buysell"),2) AS "obyaz_before"
                , ROUND(ABS("md_over"."obyaz_after"),2) AS "obyaz_after"
                , ROUND("md_over"."obyaz",2) AS "obyaz"
                , ROUND("md_over"."equitydeal",2) AS "equitydeal"
                , ROUND("md_over"."deltaEquity",2) AS "deltaEquity"
                , ROUND("md_over"."deltaBalance",2) AS "deltaBalance"
                , "md_over"."TimeMsc"
                , DATE("md_over"."TimeMsc") AS date_dw
                FROM (
                SELECT "md_prev".*,
                SUM("md_prev"."buysell") OVER(PARTITION BY "md_prev"."Login" ORDER BY "md_prev"."TimeMsc") AS "obyaz_after",
                SUM("md_prev"."profitOut") OVER(PARTITION BY "md_prev"."Login", DATE("md_prev"."TimeMsc") ORDER BY "md_prev"."TimeMsc" DESC) AS "deltaBalance"
                FROM (
                SELECT "Deal", "Login", "TimeMsc", "Action",
                CASE
                WHEN md."Action" = 0 THEN ROUND((md."Volume"*10*md."RateMargin")::numeric,2)
                WHEN md."Action" = 1 THEN ROUND((md."Volume"*(-10)*md."RateMargin")::numeric,2)
                END AS "buysell",
                ROUND((md."Volume"*10*md."RateMargin")::numeric,2) as "obyaz",
                CASE
                WHEN md."Symbol" = 'USDMXNrfd' THEN ROUND((md."Volume"*10*md."RateMargin"/20)::numeric,2)
                WHEN md."Symbol" = 'USDZARrfd' THEN ROUND((md."Volume"*10*md."RateMargin"/20)::numeric,2)
                WHEN md."Symbol" = 'USDDKKrfd' THEN ROUND((md."Volume"*10*md."RateMargin"/10)::numeric,2)
                WHEN md."Symbol" = 'EURDKKrfd' THEN ROUND((md."Volume"*10*md."RateMargin"/10)::numeric,2)
                WHEN md."Symbol" = 'USDSGDrfd' THEN ROUND((md."Volume"*10*md."RateMargin"/10)::numeric,2)
                ELSE ROUND((md."Volume"*10*md."RateMargin"/40)::numeric,2)
                END AS "equitydeal",
                CASE
                WHEN md."Action" not in (1,0) or md."Entry" = 1 THEN 0
                ELSE ROUND((md."Volume"*(md."MarketAsk"-md."MarketBid")*md."RateMargin"/md."Price")::numeric,2)
                END AS "deltaEquity",
                CASE
                WHEN md."Action" in (2,7) THEN ROUND((md."Profit")::numeric,2)
                ELSE 0
                END AS "profitOut"
                FROM mt5_deals md
        -- WHERE md."Deal" <= 1006273403
                WHERE DATE(md."TimeMsc") <= DATE('"""+str(date_rep["date_rep"])+"""')
                ORDER BY md."Deal" DESC			
                ) AS "md_prev"
                ) AS "md_over"
        -- WHERE "md_over"."Deal" BETWEEN 1006273399 AND 1006273403
        -- WHERE "md_over"."TimeMsc" < '2021-08-19' and "md_over"."TimeMsc" >= '2021-08-18'
                WHERE DATE("md_over"."TimeMsc") = DATE('"""+str(date_rep["date_rep"])+"""')
                AND "md_over"."Deal" BETWEEN """+str(first_deal)+""" AND """+str(last_deal)+"""
                AND "md_over"."Action" in (0,1)
                ) as "for_join"		
        /*
                left join (
                SELECT mdaily."Datetime", mdaily."Login", mdaily."ProfitEquity"
                from public.mt5_daily mdaily
                WHERE DATE('1970-01-01 00:00:00'::timestamp + mdaily."Datetime"*INTERVAL'1 SECOND' - INTERVAL'1 HOUR') >= DATE('2021-08-18')
                and DATE('1970-01-01 00:00:00'::timestamp + mdaily."Datetime"*INTERVAL'1 SECOND' - INTERVAL'1 HOUR') < DATE('2021-08-19')
                and mdaily."ProfitEquity" != 0
                ) as "daily" on "for_join"."Login"="daily"."Login" AND DATE("for_join"."TimeMsc") = DATE('1970-01-01 00:00:00'::timestamp + "daily"."Datetime"*INTERVAL'1 SECOND' - INTERVAL'1 HOUR')
        */
                ORDER BY "for_join"."Deal" ASC;
        """
        cursor.execute(query)
        deals = cursor.fetchall()
        #df = pd.DataFrame(columns=['Ticket', 'Number', 'Login', 'obyaz_before', 'obyaz_after', 'obyaz', 'equity_before', 'equity_after', 'equitydeal', 'deltaEquity', 'deltaBalance', 'update'])
        df = pd.DataFrame(columns=['Ticket', 'Number', 'Login', 'Currency', 'total_debt_before (обязательства до)', 'total_debt (обязательтства после)', 'oper_debt (обязательства)', 'total_go_before (обеспечение до)', 'total_go (обеспечение после)', 'oper_go (обеспечение)', 'update'])
        i = 1
        print(str(date_rep["date_rep"])+':\twrite\t'+str(datetime.datetime.now()))
        with open(result_dir+'/query_'+str(date_rep["date_rep"])+'.txt','w',encoding='utf-8') as fquery:
            for deal in deals:
                i+=1
                #df.loc[len(df)] = [int(deal["Deal"]), '', int(deal["Login"]), '{:.2f}'.format(round(float(deal["obyaz_before"]),2)), '{:.2f}'.format(round(float(deal["obyaz_after"]),2)), '{:.2f}'.format(round(float(deal["obyaz"]),2)), '{:.2f}'.format(round(float(equty_dict.get(deal["Login"],str(0))),2)-round(float(deal["deltaBalance"]),2)), '{:.2f}'.format(round(float(equty_dict.get(deal["Login"],str(0))),2)-round(float(deal["deltaBalance"]),2)-round(float(deal["deltaEquity"]),2)), '{:.2f}'.format(round(float(deal["equitydeal"]),2)), '{:.2f}'.format(round(float(deal["deltaEquity"]),2)), '{:.2f}'.format(round(float(deal["deltaBalance"]),2)), """="UPDATE [dbo].[FXOperLog] SET oper_go="&J"""+str(i)+"""&", total_go="&I"""+str(i)+"""&", total_go_before="&H"""+str(i)+"""&", total_debt="&F"""+str(i)+"""&", total_debt_before="&E"""+str(i)+"""&" WHERE [number]='"&C"""+str(i)+"""&"' AND [ticket]="&B"""+str(i)+"""&";\""""]
                df.loc[len(df)] = [int(deal["Deal"]), '', int(deal["Login"]), equty_dict[deal["Login"]]["currency"], deal["obyaz_before"], deal["obyaz_after"], deal["obyaz"], '{:.2f}'.format(round(float(equty_dict[deal["Login"]]["equity"]),2)-round(float(deal["deltaBalance"]),2)), '{:.2f}'.format(round(float(equty_dict[deal["Login"]]["equity"]),2)-round(float(deal["deltaBalance"]),2)-round(float(deal["deltaEquity"]),2)), deal["equitydeal"], """="UPDATE [dbo].[FXOperLog] SET oper_go="&K"""+str(i)+"""&", total_go="&J"""+str(i)+"""&", total_go_before="&I"""+str(i)+"""&", total_debt="&G"""+str(i)+"""&", total_debt_before="&F"""+str(i)+"""&" WHERE [number]='"&C"""+str(i)+"""&"' AND [ticket]="&B"""+str(i)+"""&";\""""]
                fquery.write("UPDATE [dbo].[FXOperLog] SET oper_go="+str(deal["equitydeal"])+", total_go="+'{:.2f}'.format(round(float(equty_dict[deal["Login"]]["equity"]),2)-round(float(deal["deltaBalance"]),2)-round(float(deal["deltaEquity"]),2))+", total_go_before="+'{:.2f}'.format(round(float(equty_dict[deal["Login"]]["equity"]),2)-round(float(deal["deltaBalance"]),2))+", total_debt="+str(deal["obyaz_after"])+", total_debt_before="+str(deal["obyaz_before"])+" WHERE [ticket]="+str(deal["Deal"])+";\n")
        print(str(date_rep["date_rep"])+':\texcel\t'+str(datetime.datetime.now()))
        with pd.ExcelWriter(result_dir+'/deals_'+str(date_rep["date_rep"])+'.xlsx') as writer:
            df.to_excel(writer)
        print(str(date_rep["date_rep"])+':\tfinish\t'+str(datetime.datetime.now())+'\n')
Postgre_connection.close()
