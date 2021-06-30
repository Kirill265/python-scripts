import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidArgumentException
import time
from keepass import key_pass

def TW_text_file(URL_TW,message_text,attached_file):
    driver = webdriver.Firefox()
    driver.get(URL_TW)
    login_func = driver.find_element_by_id("id_login")
    login_func.send_keys(key_pass('TW').username)
    pass_func = driver.find_element_by_name("password")
    pass_func.send_keys(key_pass('TW').password)
    pass_func.send_keys(Keys.RETURN)
    load_checked = 0
    while load_checked == 0:
        try:
            iframe = driver.find_elements_by_tag_name('iframe')[0]
            driver.switch_to.frame(iframe)
            load_checked = 1
        except IndexError:
            time.sleep(2)
    load_checked = 0
    while load_checked == 0:
        try:
            new_comment = driver.find_element_by_link_text("Новый комментарий").click()
            load_checked = 1
        except NoSuchElementException:
            time.sleep(2)
    load_checked = 0
    while load_checked == 0:
        try:
            if "servicedesk" in URL_TW:
                Send_message = driver.find_element_by_name("content")
            elif "tasks" in URL_TW:
                Send_message = driver.find_element_by_name("comment_body")
            else:
                driver.quit()
            load_checked = 1
        except NoSuchElementException:
            time.sleep(2)
    Send_message.send_keys(message_text)
    load_checked = 0
    while load_checked == 0:
        try:
            attach_files = driver.find_element_by_link_text("Прикрепить файл").click()
            load_checked = 1
        except NoSuchElementException:
            time.sleep(2)
    try:
        attach_file = driver.find_element_by_xpath("//input[@type='file']").send_keys(attached_file)
    except InvalidArgumentException:
        pass
    send_button = driver.find_element_by_xpath("//input[@value='Добавить']").click()
    load_checked = 0
    while load_checked == 0:
        try:
            find_button = driver.find_element_by_xpath("//input[@value='Добавить']")
            time.sleep(2)
        except NoSuchElementException:
            load_checked = 1
    driver.quit()
