import paramiko
import sys
import os
import time
import datetime
from datetime import timedelta, date, time
import psycopg2
from psycopg2.extras import DictCursor
if __name__ == '__main__':
    sys.path.insert(1,os.path.dirname(os.path.abspath(__file__)).split("Python_scripts")[0]+"Python_scripts\\Tools")
from keepass import key_pass
from Bot_generator import full_name, birthplace, birdthay, passport, mail, phone, inn_individual, snils, randomday, address

def customer_trunk(botName='',userName='',userId=''):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        result = {}
        result["error"] = ""
        try:
            passphrase = key_pass('PuTTY TRUNC').password
            user = key_pass('PuTTY TRUNC').username
            host = key_pass('PuTTY TRUNC').url
            note = key_pass('PuTTY TRUNC').notes
            ssh_connection = ssh.connect(hostname = host, port=22, username=user, key_filename=note, look_for_keys=False, passphrase=passphrase)
        except:
            result["error"] = "*Auth failed*"
            result["error_msg"] = "Попробуй позднее или [сообщи об ошибке](https://t.me/Kirill_Cherkasov)."
            ssh.close()
            return result
        #except paramiko.AuthenticationException:
        now = datetime.datetime.now()
        acceptedAt = randomday(2015,int(now.year-1))
        fullName = full_name('and_sex')
        result["fio"] = fullName.split("`\n`")[0]+" "+fullName.split("`\n`")[1]+" "+fullName.split("`\n`")[2]
        birtDay = birdthay()
        Passport = passport()
        Adress = address('all_data')
        if Adress["city_with_type"] == None:
            cityName = Adress["region_with_type"]
        else:
            cityName = Adress["city_with_type"]
        Phone = phone()
        curl = """curl --location --request POST 'https://exposure-layer.trunk.alfaforex.dom/external/alfaclick/customers' \
--header 'Content-Type: application/json' \
--data-raw '{
    "acceptedAt": \""""+acceptedAt.split(".")[2]+"""-"""+acceptedAt.split(".")[1]+"""-"""+acceptedAt.split(".")[0]+"""T"""+str(now.time()).split('.')[0]+"""Z",
    "personal": {
      "lastName": \""""+fullName.split("`\n`")[0]+"""\",
      "firstName": \""""+fullName.split("`\n`")[1]+"""\",
      "middleName": \""""+fullName.split("`\n`")[2]+"""\",
      "sex": \""""+fullName.split("`\n`")[3]+"""\",
      "birthDate": \""""+birtDay.split(".")[2]+"""-"""+birtDay.split(".")[1]+"""-"""+birtDay.split(".")[0]+"""\",
      "birthCountry": "RU",
      "birthPlace": \""""+birthplace()+"""\",
      "citizenshipCountry": "RU"
    },
    "document": {
      "seriesAndNumber": \""""+Passport.split("`\n`")[0].replace(" ","")+"""\",
      "issuedAt": \""""+Passport.split("`\n`")[1].split(".")[2]+"""-"""+Passport.split("`\n`")[1].split(".")[1]+"""-"""+Passport.split("`\n`")[1].split(".")[0]+"""\",
      "issuedBy": \""""+Passport.split("`\n`")[3]+"""\",
      "issuerCode": \""""+Passport.split("`\n`")[2]+"""\"
    },
     "contact": {
      "registrationAddress": \""""+Adress["postal_code"]+""", РОССИЯ, """+Adress["result"]+"""\",
      "actualAddress": \""""+Adress["postal_code"]+""", РОССИЯ, """+Adress["result"]+"""\",
      "phone": "+7("""+Phone[1:4]+""")"""+Phone[4:7]+"""-"""+Phone[7:9]+"""-"""+Phone[9:]+"""\",
      "email": \""""+mail()+"""\",
      "actualAddressInfo": {
        "typeCode": "F",
        "typeLabel": "Фактический адрес регистрации /юридич",
        "fullAddress": \""""+Adress["postal_code"]+""", РОССИЯ, """+Adress["result"]+"""\",
        "countryCode": "RU",
        "countryName": "",
        "postcode": \""""+Adress["postal_code"]+"""\",
        "regionCode": \""""+Adress["region_kladr_id"][:2]+"""\",
        "regionName": \""""+Adress["region_with_type"]+"""\",
        "districtTypeCode": "",
        "districtName": "",
        "cityName": \""""+cityName+"""\",
        "settlementTypeCode": "",
        "settlementName":"",
        "streetType": "",
        "streetName": \""""+Adress["street_with_type"]+"""\",
        "houseNumber": \""""+Adress["house"]+"""\",
        "buildingNumber": "",
        "flatNumber": \""""+Adress["flat"]+"""\"
      },
      "registrationAddressInfo": {
        "typeCode": "J",
        "typeLabel": "Подробный адрес регистрации /юридич",
        "fullAddress": \""""+Adress["postal_code"]+""", РОССИЯ, """+Adress["result"]+"""\",
        "countryCode": "RU",
        "countryName": "",
        "postcode": \""""+Adress["postal_code"]+"""\",
        "regionCode": \""""+Adress["region_kladr_id"][:2]+"""\",
        "regionName": \""""+Adress["region_with_type"]+"""\",
        "districtTypeCode": "",
        "districtName": "",
        "cityName": \""""+cityName+"""\",
        "settlementTypeCode": "",
        "settlementName":"",
        "streetType": "",
        "streetName": \""""+Adress["street_with_type"]+"""\",
        "houseNumber": \""""+Adress["house"]+"""\",
        "buildingNumber": "",
        "flatNumber": \""""+Adress["flat"]+"""\"
      }
    },
    "other": {
      "inn": \""""+inn_individual()+"""\",
      "insuranceNumber": \""""+snils()+"""\",
      "additional": {
        "utm_term": \""""+str(userName)+"""\",
        "p": \""""+str(userId)+"""\",
        "utm_campaign": \""""+str(botName)+"""\",
        "utm_medium": "bot",
        "utm_content": "create_customer",
        "utm_source": "telegram"
      },
      "documents": {
        "FOREX_AGREEMENT": \""""+str(now.date())+"""T"""+str(now.time()).split('.')[0]+"""Z"
      }
    }
  }'
"""
        #print(curl)
        ( stdin, stdout, stderr ) = ssh.exec_command(curl)
        resout = str(stdout.read())
        ssh.close()
        if 'errors' in resout:
            resout = resout.split("\\n")[-1]
            if 'customer.already_registered' in resout:
                result["error"] = '*'+resout[:-1]+'*'
                result["error_msg"] = "Такой клиент уже есть. Попробуй снова."
            else:
                result["error"] = '*'+resout[:-1]+'*'
                result["error_msg"] = "Нужно смотреть логи."
            return result
        if resout == "b''":
            result["error"] = '*Empty response*'
            result["error_msg"] = "Проверь клиента:\n_"+result["fio"]+"_.\nВероятно, регистрация завершена."
            return result
        customer_id = resout.split("\"id\":\"")[-1].split("\"}")[0]
        #print(customer_id)
        SQL_DB = 'PostgreSQL DB TRUNK'
        Postgre_connection = psycopg2.connect(
            host=key_pass(SQL_DB).url[:-5],
            port=int(key_pass(SQL_DB).url[-4:]),
            user=key_pass(SQL_DB).username,
            password=key_pass(SQL_DB).password,
            dbname='customer'
        )
        with Postgre_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                    SELECT login
                    FROM customer
                    WHERE id = \'"""+customer_id+"""\'
                    ;
             """
            cursor.execute(query)
            customer_lk = cursor.fetchone()
        result["id"] = customer_id
        result["lk"] = str(customer_lk["login"])
        result["phone"] = str(Phone[1:])
        #print(result["id"])
        #print(result["lk"])
        #print(stdout.read())
        return result
    except:
        result = {"error":"Ошибка в функции *customer_trunk*","error_msg":"[Сообщи об ошибке.](https://t.me/Kirill_Cherkasov)"}
        return result
if __name__ == '__main__':
    customer_trunk()
