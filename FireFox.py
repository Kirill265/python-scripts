from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

driver = webdriver.Firefox()
driver.get("https://team.alfaforex.com/servicedesk/view/11136")
#driver.get("https://team.alfaforex.com/tasks/view/2649")
login_func = driver.find_element_by_id("id_login")
login_func.send_keys("Kirill Cherkasov")
pass_func = driver.find_element_by_name("password")
pass_func.send_keys("Qwerty123")
pass_func.send_keys(Keys.RETURN)
load_checked = 0
while load_checked == 0:
    try:
        iframe = driver.find_elements_by_tag_name('iframe')[0]
        load_checked = 1
    except IndexError:
        time.sleep(2)
driver.switch_to.frame(iframe)
new_comment = driver.find_element_by_link_text("Новый комментарий").click()
SD_message = driver.find_element_by_name("content")
SD_message.send_keys("Проверка связи")
#Task_message = driver.find_element_by_name("comment_body")
#Task_message.send_keys("Проверка связи")
attach_files = driver.find_element_by_link_text("Прикрепить файл").click()
attach_file = driver.find_element_by_xpath("//input[@type='file']").send_keys("C:\\Users\\Kirill_Cherkasov\\Documents\\Reports\\Оно работает.txt")
send_button = driver.find_element_by_xpath("//input[@value='Добавить']").click()
load_checked = 0
while load_checked == 0:
    try:
        find_button = driver.find_element_by_xpath("//input[@value='Добавить']")
        time.sleep(2)
    except NoSuchElementException:
        load_checked = 1
driver.quit()
