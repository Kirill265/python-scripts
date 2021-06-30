from collections import OrderedDict

from check_service import \
    check_mt, check_communication, check_customer, check_account, \
    check_sites, check_site, check_all, check_monitoring, \
    site_for_check

from New_client_report import New_client
from Active_client_report import Active_client
from Checked_cust_report import Check_client
from Convertation_report import Convert_period
from USD_14_report import PL_14
from Volume_USD_report import Volume_period

actions_check = OrderedDict([
    ('Проверить все', check_all),
    ('МТ5', check_mt),
    ('Регистрации', check_customer),
    ('Коммуникации', check_communication),
    ('Счета', check_account),
    ('Интернет - ресурсы', check_sites),
])

actions_report = OrderedDict([
    ('Новые активные клиенты', New_client),
    ('Количество активных ТС', Active_client),
    ('Проверенные клиенты', Check_client),
    ('Конвертации', Convert_period),
    ('PL по 14 инструментам', PL_14),
    ('Оборот в USD', Volume_period),
])

