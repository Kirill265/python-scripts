import sys
import os
import shutil
import requests
import xlsxwriter
import psycopg2
from psycopg2.extras import DictCursor
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass


SQL_DB = 'PotgreSQL DB PROD'
#SQL_DB = 'PostgreSQL DB TRUNK'
Postgre_taxes = psycopg2.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    dbname='taxes'
)
Postgre_customer = psycopg2.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    dbname='customer'
)
Postgre_banking = psycopg2.connect(
    host=key_pass(SQL_DB).url[:-5],
    port=int(key_pass(SQL_DB).url[-4:]),
    user=key_pass(SQL_DB).username,
    password=key_pass(SQL_DB).password,
    dbname='banking'
)
year='2021'
direction = os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts"
direction = os.path.join(direction, 'Reports')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction = os.path.join(direction, 'Taxes')
if not(os.path.exists(direction)):
    os.mkdir(direction)
direction += '\\'
workbook = xlsxwriter.Workbook(direction+'Tax_return_'+year+'.xlsx')
workbook.formats[0].set_font_size(8.5)
workbook.formats[0].set_font_name('Tahoma')
wrap_format = workbook.add_format()
wrap_format.set_text_wrap()
wrap_format.set_font_size(8.5)
wrap_format.set_font_name('Tahoma')
worksheet = workbook.add_worksheet()
worksheet.set_default_row(22)
worksheet.set_row(0, 20)
#print("login\tname\tstatus\tamount\tcreated\tsigned\tfile")
worksheet.write('A1', 'Логин')
worksheet.set_column(0, 0, 15)
worksheet.write('B1', 'ФИО')
worksheet.set_column(1, 1, 25)
worksheet.write('C1', 'статус')
worksheet.set_column(2, 2, 10)
worksheet.write('D1', 'сумма')
worksheet.set_column(3, 3, 15)
worksheet.write('E1', 'создано')
worksheet.set_column(4, 4, 18)
worksheet.write('F1', 'подписано')
worksheet.set_column(5, 5, 18)
worksheet.write('G1', 'заявление')
worksheet.set_column(6, 6, 30)
worksheet.write('H1', 'ТС')
worksheet.write('I1', 'кастомер')
worksheet.write('J1', 'СР')
worksheet.write('K1', 'НС')
worksheet.write('L1', 'состояние')
worksheet.write('M1', 'закрыт в')
worksheet.write('N1', 'тип счета')
worksheet.write('O1', 'кастомер')
with Postgre_taxes.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
    query = """
            SELECT
            tp.value, ct.customer_id, ctd.tax_amount, cts.name, ct.created_at, ct.signed_at, file_id, ctd.account_id
            FROM public.customer_tax ct
            join public.customer_tax_detail ctd on ctd.customer_tax_id = ct.id
            join public.tax_period tp on ct.tax_period_id = tp.id
            join public.customer_tax_status cts on cts.id = ct.status_id
            where value = """+year+""";
     """
    cursor.execute(query)
    taxes = cursor.fetchall()
Postgre_taxes.close()
customer_list = ''
account_list = ''
for tax in taxes:
    customer_list += "'" + tax["customer_id"] + "',"
    account_list += "'" + tax["account_id"] + "',"
with Postgre_customer.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
    query = """
            SELECT c.id, c.login, p.last_name, p.first_name, p.middle_name
            FROM public.customer c
            JOIN public.person p ON p.id = c.id
            WHERE c.id in ("""+customer_list[:-1]+""");
     """
    cursor.execute(query)
    customers = cursor.fetchall()
Postgre_customer.close()
with Postgre_banking.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
    query = """
            SELECT na.trading_account_id, na.trading_account_login, na.customer_id, na.nominal_section, ac.account_number, na.state, na.nominal_section_closed_at, account_type
            FROM public.nominal_account na
            join public.bank_account ba on ba.id = na.bank_account_id
            join public.account ac on ac.id = na.bank_account_id 
            where na.trading_account_id in ("""+account_list[:-1]+""")
            AND account_type = 'MAIN';
     """
    cursor.execute(query)
    accounts = cursor.fetchall()
Postgre_banking.close()
tax_dict = {}
customer_dict = {}
account_dict = {}
for customer in customers:
    customer_dict[customer["id"]] = {"login":customer["login"], "name":customer["last_name"]+" "+customer["first_name"]+" "+customer["middle_name"]}
for account in accounts:
    account_dict[account["trading_account_id"]] = {"login":account["trading_account_login"], "customer":account["customer_id"], "spec":account["nominal_section"], "nominal":account["account_number"], "state":account["state"], "closed":account["nominal_section_closed_at"], "type":account["account_type"]}

'''
for tax in taxes:
    tax_dict[tax["customer_id"]] = {"amount":tax["tax_amount"], "status":tax["name"], "created":tax["created_at"], "signed":tax["signed_at"], "file":tax["file_id"], "login":customer_dict[tax["customer_id"]]["login"], "name":customer_dict[tax["customer_id"]]["name"]}

print("login\tname\tstatus\tamount\tcreated\tsigned\tfile")
for tax in tax_dict:
    line = str(tax_dict[tax]["login"])+"\t"+tax_dict[tax]["name"]+"\t"+tax_dict[tax]["status"]+"\t"+str(tax_dict[tax]["amount"]/100)+"\t"+str(tax_dict[tax]["created"])+"\t"+str(tax_dict[tax]["signed"])+"\t"+tax_dict[tax]["file"]
    print(line)
'''
j = 1
for tax in taxes:
    j += 1
    worksheet.write(f'A{j}', customer_dict[tax["customer_id"]]["login"])
    worksheet.write(f'B{j}', customer_dict[tax["customer_id"]]["name"], wrap_format)
    worksheet.write(f'C{j}', tax["name"])
    worksheet.write(f'D{j}', tax["tax_amount"])
    worksheet.write(f'E{j}', str(tax["created_at"]).split(".")[0])
    worksheet.write(f'F{j}', str(tax["signed_at"]).split(".")[0])
    worksheet.write(f'G{j}', tax["file_id"])
    worksheet.write(f'H{j}', account_dict[tax["account_id"]]["login"])
    worksheet.write(f'I{j}', account_dict[tax["account_id"]]["customer"])
    worksheet.write(f'J{j}', account_dict[tax["account_id"]]["spec"])
    worksheet.write(f'K{j}', account_dict[tax["account_id"]]["nominal"])
    worksheet.write(f'L{j}', account_dict[tax["account_id"]]["state"])
    worksheet.write(f'M{j}', str(account_dict[tax["account_id"]]["closed"]))
    worksheet.write(f'N{j}', account_dict[tax["account_id"]]["type"])
    worksheet.write(f'O{j}', tax["customer_id"])
workbook.close()
