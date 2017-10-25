import re

import pymysql
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bsp
from config import *

browser = webdriver.PhantomJS(DRIVER_PATH)
browser.set_window_size(1400, 900)
wait = WebDriverWait(browser, 10)
conn = pymysql.connect(**CONNECTION)
cur = conn.cursor()
cur.execute('USE scraping')
try:
    cur.execute(CREATE_TABLE)
except pymysql.InternalError:
    cur.execute('DROP TABLE IF EXISTS taobaoPage')
    cur.execute(CREATE_TABLE)


def search():
    print("正在搜索")
    try:
        browser.get('https://www.taobao.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys('美食')
        submit.click()
        pages_num = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        pages_num = int(re.compile('.*?(\d+)').search(pages_num.text).groups(1)[0])
        get_products()
        return pages_num
    except TimeoutException:
        search()


def next_page(page_num):
    print("正在翻第%s页" % page_num)
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_num)
        submit.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_num)))
        get_products()
    except TimeoutException:
        next_page(page_num)


def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = bsp(html, 'lxml')
    items = doc.findAll("div", {"class": re.compile("item J_MouserOnverReq.*?")})
    for item in items:
        product = {
            'name': item.find("img").attrs['alt'],
            'image': item.find("img").attrs['data-src'],
            'price': item.find("strong").get_text(),
            'location': item.find("", {"class": "location"}).get_text(),
            'deal': item.find("", {"class": "deal-cnt"}).get_text()[:-3],
            'shop': item.find("", {"class": "shop"}).findAll("span")[4].get_text()
        }
        save_to_mysql(product)


def save_to_mysql(result):
    try:
        cur.execute(INSERT_DATA.format(result['name'], result['image'], result['price'],
                                       result['location'], result['deal'], result['shop']))
        cur.connection.commit()
        print(result['name'], '储存到mysql数据库成功')
    except pymysql.DatabaseError as e:
        print('储存到mysql数据库失败', e)


def main():
    pages_num = search()
    for i in range(2, pages_num + 1):
        next_page(i)
    cur.close()
    conn.close()
    browser.close()

if __name__ == "__main__":
    main()
