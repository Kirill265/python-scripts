import sys
import os
import shutil
import requests
import httplib2
from httplib2 import ServerNotFoundError, RedirectMissingLocation, RedirectLimit, RelativeURIError, FailedToDecompressContent, UnimplementedHmacDigestAuthOptionError, UnimplementedDigestAuthOptionError, HttpLib2Error
import ssl
import datetime
import telebot
from telebot import types

all_site_for_check=["alfaforex.ru",
                    "alfaforex.ru/open-account",
                    "my.alfaforex.ru/login",
                    "agent.alfaforex.ru/login",
                    "team.alfaforex.com",
                    "alfaforex.ru/trading-terms",
                    "alfaforex.ru/deposit-withdrawal",
                    "alfaforex.ru/online-trading",
                    "alfaforex.ru/metatrader",
                    "alfaforex.ru/analytics",
                    "alfaforex.ru/currency-exchange",
                    "alfaforex.ru/faq",
                    "alfaforex.ru/agentskaya-programma",
                    "alfaforex.ru/documents",
                    "alfaforex.ru/requisites",
                    "alfaforex.ru/disclosure",
                    "alfaforex.ru/about",
                    "alfaforex.ru/news",
                    "alfaforex.ru/contacts",
                    "alfaforex.ru/economic-calendar",
                    "alfaforex.ru/trading-calc",
                    "alfaforex.ru/analytics/analytics-reviews",
                    "alfaforex.ru/analytics/analytics-currencies",
                    "alfaforex.ru/analytics/analytics-rates",
                    "alfaforex.ru/demo-account",
                    "alfaforex.ru/analytics/education",
                    "alfaforex.ru/analytics/education/archive-daily-reviews"]

def telega_alert(Report: str):
    bot = telebot.TeleBot('1362203438:AAFNp5tXRWi6Pn5RkIgqq_7ELHdGTbY9CUs')
    answer = bot.send_message(chat_id = -1001409956540, text = Report, parse_mode= 'Markdown', disable_web_page_preview = True)
    return answer

def check_site(site: str, name = ""):
    try:
        http = httplib2.Http()
        now = datetime.datetime.now()
        if now.hour == 3 and site == "team.alfaforex.com" :
            return ''
        try:
            response = http.request("https://"+site, 'HEAD')
            if not (response[0]["status"] == '200' or ((now.hour == 2 or now.hour == 3 or now.hour == 4 or now.hour == 5) and site == "team.alfaforex.com" and response[0]["status"] == '502')):
                Report = '['+site+'](https://'+site+') - '+response[0]["status"]
                telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
                return Report
            return '['+site+'](https://'+site+') - OK'
        except ssl.SSLCertVerificationError:
            Report = '['+site+'](https://'+site+') - '+'Certificate Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except AttributeError:
            Report = '['+site+'](https://'+site+') - '+'SSL Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except TimeoutError:
            Report = '['+site+'](https://'+site+') - '+'Timeout Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except httplib2.RedirectMissingLocation:
            Report = '['+site+'](https://'+site+') - '+'RedirectMissingLocation Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except httplib2.RedirectLimit:
            Report = '['+site+'](https://'+site+') - '+'RedirectLimit Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        except httplib2.ServerNotFoundError:
            Report = '['+site+'](https://'+site+') - '+'ServerNotFound Error'
            telega_alert(u'\U0000274C'+' '+Report+'\n\n#site')
            return Report
        '''
        except httplib2.RelativeURIError:
            Report = '['+site+'](https://'+site+') - '+'RelativeURI Error'
            return Report
        except httplib2.FailedToDecompressContent:
            Report = '['+site+'](https://'+site+') - '+'Decompression algorithm failed'
            return Report
        except httplib2.UnimplementedHmacDigestAuthOptionError:
            Report = '['+site+'](https://'+site+') - '+'Uknown HMACDigest authentication'
            return Report
        except httplib2.UnimplementedDigestAuthOptionError:
            Report = '['+site+'](https://'+site+') - '+'Uknown Digest authentication'
            return Report
        except httplib2.HttpLib2Error:
            Report = '['+site+'](https://'+site+') - '+'HttpLib2 Error'
            return Report
        '''
    except:
        Report = '\n\nОшибка в функции *check_site* для: '+site
        return Report

def check_sites(name = ""):
    try:
        Report = ''
        for site_check in all_site_for_check:
            Report += check_site(site_check,name) + '\n'
        return Report
    except:
        return '\n\nОшибка в функции *check_sites*'

if __name__ == '__main__':
    check_sites()
