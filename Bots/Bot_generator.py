import random, re
from mimesis import Person
from mimesis import Address
from mimesis.enums import Gender
from datetime import date
import datetime
from datetime import timedelta
from uuid import uuid4
from dadata import Dadata
import json
from keepass import key_pass
import os
import shutil

token = key_pass('DaData API').password
secret = key_pass('DaData secret').password

direction = os.path.dirname(os.path.abspath(__file__))+'\\'
#Место рождения
def birthplace(): return Address('ru').city()

#Пасспорт
def passport():
    with Dadata(token, secret) as dadata:
        now1 = datetime.datetime.now()
        now = now1 - timedelta(days=1)
        if now.month < 10:
            passport_month = '0'+str(now.month)
        else:
            passport_month = str(now.month)
        if now.day < 10:
            passport_day = '0'+str(now.day)
        else:
            passport_day = str(now.day)
        cod = 0
        while cod != 1:
            ser1 = random.randint(1, 99)
            if ser1 < 10:
                ser1 = '0'+str(ser1)
            else:
                ser1 = str(ser1)
            num6 = ''
            for i in range(0,6):
                num6 += str(random.randint(1, 9))
            try:
                series = dadata.clean(name="passport", source=ser1+str(now.year)[-2:]+num6)
                check = series["series"].replace(' ', '')
                cod = 1
            except:
                cod = 0
        cod = 0
        while cod != 1:
            path = direction+"my_person.json"
            with open(path, encoding="utf-8") as fjson:
                data = json.load(fjson)
            ufms_code = random.choice(data["ufms_codes"])
            try:
                fms = dadata.suggest(name="fms_unit", query=ufms_code)
                check = fms[0]["value"]
                cod = 1
            except:
                cod = 0
    return series["series"].replace(' ', '')+" "+series["number"]+"`\n`"+passport_day+"."+passport_month+"."+str(now.year)+"`\n`"+ufms_code+"`\n`"+fms[0]["value"]

# Адресс
def address(how = 'full'):
    if how == 'split':
            return Address('ru').city()+" "+Address('ru').street_name()
    if how == 'all_data':
        new_address = {"flat":None}
        while new_address["flat"] == None or new_address["postal_code"] == None or new_address["region_kladr_id"] == None or new_address["region_with_type"] == None or new_address["street_with_type"] == None or new_address["house"] == None:
            with Dadata(token, secret) as dadata:
                new_address = dadata.clean(name="address", source=Address('ru').city()+" "+Address('ru').street_name()+" "+str(random.randint(1, 130))+" "+str(random.randint(1, 99)))
        return new_address
    with Dadata(token, secret) as dadata:
        new_address = dadata.clean(name="address", source=Address('ru').city()+" "+Address('ru').street_name()+" "+str(random.randint(1, 130))+" "+str(random.randint(1, 99)))
    return new_address["result"]

# Логин
def login(): return Person('ru').username()

# E-mail
def mail(): return Person('ru').email()

# Номер телефона
def phone(): return Person('ru').telephone('89#########')

# UUID
def uuid(): return uuid4().hex

# GUID
def guid(): return str(uuid4()).upper()

# ИНН ЮЛ
def inn_entity(): return inn(10)

# ИНН ИП
def inn_individual(): return inn(12)

# ФИО
def full_name(how = 'only_fio'):
    gend = random.randint(0, 1)
    path = direction+"my_person.json"
    result = ""
    with open(path, encoding="utf-8") as fjson:
        data = json.load(fjson)
    if gend == 0:
        FIO = re.findall(r'\S+|\s+', Person('ru').full_name(gender=Gender.MALE))
        result = FIO[2] + "`\n`" + FIO[0] + "`\n`" + random.choice(data["middlenames"]["male"])
    else:
        FIO = re.findall(r'\S+|\s+', Person('ru').full_name(gender=Gender.FEMALE))
        result = FIO[2] + "`\n`" + FIO[0] + "`\n`" + random.choice(data["middlenames"]["female"])
    if how == 'and_sex':
        if gend == 0:
            result += "`\n`MALE"
        else:
            result += "`\n`FEMALE"
    return result

# Дата рождения
def birdthay():
    random_day = date.fromordinal(random.randint(date.today().replace(year=1950).toordinal(),
                                                 date.today().replace(year=1990).toordinal())).strftime('%d.%m.%Y')
    return random_day

# Рандомная дата
def randomday(date1,date2):
    random_day = date.fromordinal(random.randint(date.today().replace(year=int(date1)).toordinal(),
                                                 date.today().replace(year=int(date2)).toordinal())).strftime('%d.%m.%Y')
    return random_day

# Проверка на контрольную сумму
def ctrl_summ(nums, type):
    ctrl_type = {
        'n2_12': [7, 2, 4, 10, 3, 5, 9, 4, 6, 8],
        'n1_12': [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8],
        'n1_10': [2, 4, 10, 3, 5, 9, 4, 6, 8],
    }
    n = 0
    l = ctrl_type[type]
    for i in range(0, len(l)):
        n += nums[i] * l[i]
    return n % 11 % 10
'''
# СНИЛС
def snils():
    nums = [
        random.randint(1, 1) if x == 0
        else '-' if x == 3
        else '-' if x == 7
        else ' ' if x == 11
        else random.randint(0, 9)
        for x in range(0, 12)
    ]

    cont = (nums[10] * 1) + (nums[9] * 2) + (nums[8] * 3) + \
           (nums[6] * 4) + (nums[5] * 5) + (nums[4] * 6) + \
           (nums[2] * 7) + (nums[1] * 8) + (nums[0] * 9)

    if cont in (100, 101):
        cont = '00'

    elif cont > 101:
        cont = (cont % 101)
        if cont in (100, 101): cont = '00'
        elif cont < 10: cont = '0' + str(cont)

    elif cont < 10: cont = '0' + str(cont)

    nums.append(cont)
    return ''.join([str(x) for x in nums])
'''

# СНИЛС
def snils():
    nums = [
        random.randint(1, 1) if x == 0
        else random.randint(0, 9)
        for x in range(0, 9)
    ]

    cont = (nums[8] * 1) + (nums[7] * 2) + (nums[6] * 3) + \
           (nums[5] * 4) + (nums[4] * 5) + (nums[3] * 6) + \
           (nums[2] * 7) + (nums[1] * 8) + (nums[0] * 9)

    if cont in (100, 101):
        cont = '00'

    elif cont > 101:
        cont = (cont % 101)
        if cont in (100, 101): cont = '00'
        elif cont < 10: cont = '0' + str(cont)

    elif cont < 10: cont = '0' + str(cont)

    nums.append(cont)
    return ''.join([str(x) for x in nums])

# Создание ИНН
def inn(l):
    nums = [
        random.randint(9, 9) if x == 0
        else random.randint(6, 6) if x == 1
        else random.randint(0, 9)
        for x in range(0, 9 if l == 10 else 10)
    ]

    if l == 10:
        n1 = ctrl_summ(nums, 'n1_10')
        nums.append(n1)

    elif l == 12:
        n2 = ctrl_summ(nums, 'n2_12')
        nums.append(n2)
        n1 = ctrl_summ(nums, 'n1_12')
        nums.append(n1)

    return ''.join([str(x) for x in nums])

# ОГРН ЮЛ
def ogrn_entity():
    nums = [
        1 if x == 0
        else random.randint(1, 9) if x == 4
        else random.randint(0, 9)
        for x in range(0, 11)
    ]

    nums.append(ctrl_summ(nums, 'n1_12'))
    ogrn = (int(''.join(str(x) for x in nums)) % 11)
    nums.append(0) if ogrn == 10 else nums.append(ogrn)
    return ''.join([str(x) for x in nums])

# ОГРН ИП
def ogrn_individual():
    while True:
        nums = [
            random.randint(3, 4) if x == 0
            else random.randint(1, 9) if x == 4
            else random.randint(0, 9)
            for x in range(0, 13)
        ]

        nums.append(ctrl_summ(nums, 'n1_12'))
        ogrn = (int(''.join(str(x) for x in nums)) % 13)

        if ogrn > 10:
            continue

        nums.append(0) if ogrn == 10 else nums.append(ogrn)
        return ''.join([str(x) for x in nums])


def luhn_residue(digits):
    return sum(sum(divmod(int(d)*(1 + i%2), 10))
                 for i, d in enumerate(digits[::-1])) % 10


def oms():
    part = ''.join(str(random.randrange(0, 9)) for _ in range(16 - 1))
    res = luhn_residue('{}{}'.format(part, 0))
    return '{}{}'.format(part, -res % 10)


def okpo():
    return get_okpo(False)


def okpo_individual():
    return get_okpo(True)


def get_okpo(infividual):
    nums = [
        random.randint(0, 9)
        for _ in range(0, 9 if infividual else 7)
    ]

    summ = 0

    for index, i in enumerate(nums):
        summ += (index+1)* i

    control = summ % 11

    if control == 10:
        summ = 0

        for index, i in enumerate(nums):
            j = index + 3

            if j > 10:
                j = j % 10

            summ += j * i

        control = summ % 11

        if control == 10:
            control = 0

    nums.append(control)

    return ''.join([str(x) for x in nums])

def gen_all():
    all_data = '`'
    all_data += '__ФИО__:\n`' + full_name() + '`\n\n'
    all_data += '__Дата рождения__:\n`' + birdthay() + '`\n\n'
    all_data += '__Место рождения__:\n`' + birthplace() + '`\n\n'
    all_data += '__E\-mail__:\n`' + mail() + '`\n\n'
    all_data += '__Телефон__:\n`' + phone() + '`\n\n'
    all_data += '__Паспорт__:\n`' + passport() + '`\n\n'
    all_data += '__СНИЛС__:\n`' + snils() + '`\n\n'
    all_data += '__ИНН__:\n`' + inn_individual() + '`\n\n'
    all_data += '__Адрес__:\n`' + address()
    return all_data
