from collections import OrderedDict

from Bot_generator import \
    inn_entity, inn_individual, ogrn_entity, ogrn_individual, \
    snils, full_name, birdthay, login, mail, phone, uuid, guid, oms, \
    okpo, okpo_individual, address, passport, birthplace

actions = OrderedDict([
    #('ИНН', inn_entity),
    ('ИНН', inn_individual),
    #('ОГРН', ogrn_entity),
    #('ОГРН ИП', ogrn_individual),
    ('СНИЛС', snils),
    ('ФИО', full_name),
    ('Дата рождения', birdthay),
    ('Место рождения', birthplace),
    #('Логин', login),
    ('E-mail', mail),
    ('Телефон', phone),
    #('GUID', guid),
    #('UUID', uuid),
    #('ЕНП ОМС', oms),
    #('ОКПО', okpo),
    #('ОКПО ИП', okpo_individual),
    ('Адрес', address),
    ('Паспорт', passport),
])
