from collections import OrderedDict

from Bot_generator import \
    inn_entity, inn_individual, ogrn_entity, ogrn_individual, \
    snils, full_name, birdthay, login, mail, phone, uuid, guid, oms, \
    okpo, okpo_individual, address, passport, birthplace, \
    gen_all

from check_service import \
    check_mt, check_communication, check_customer, check_account, \
    check_sites, check_site, check_all, check_monitoring, check_bot, \
    site_for_check

from check_neto import \
     check_all_net, all_exposure, by_exposure, by_login

actions = OrderedDict([
    ('ФИО', full_name),
    ('Дата рождения', birdthay),
    ('Место рождения', birthplace),
    ('E-mail', mail),
    ('Телефон', phone),
    ('Паспорт', passport),
    ('СНИЛС', snils),
    ('ИНН', inn_individual),
    ('Адрес', address),
    ('Сгенерить всё', gen_all)
    #('ИНН ЮЛ', inn_entity),
    #('ОГРН', ogrn_entity),
    #('ОГРН ИП', ogrn_individual),
    #('Логин', login),
    #('GUID', guid),
    #('UUID', uuid),
    #('ЕНП ОМС', oms),
    #('ОКПО', okpo),
    #('ОКПО ИП', okpo_individual),  
])

actions_check = OrderedDict([
    ('Проверить все', check_all),
    ('МТ5', check_mt),
    ('Регистрации', check_customer),
    ('Коммуникации', check_communication),
    ('Счета', check_account),
    ('Мониторинг', check_monitoring),
    ('Бизнес-Бот', check_bot),
    ('Интернет - ресурсы', check_sites),
])

actions_net = OrderedDict([
    ('все лимиты', check_all_net),
    ('по ОВП АФ (USD)', all_exposure),
    ('по ОВП АФ', by_exposure),
    ('по ОВП клиента', by_login),
])
