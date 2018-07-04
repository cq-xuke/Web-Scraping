import requests
import json
import re
import pymysql
from collections import OrderedDict
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from config import *

browser = webdriver.PhantomJS(DRIVER_PATH, service_args=SERVICE_ARGS)
browser.set_window_size(1400, 900)
wait = WebDriverWait(browser, 10)
conn = pymysql.connect(**CONNECTION)
cur = conn.cursor()
cur.execute('USE scraping')
try:
    cur.execute(CREATE_TABLE)
except pymysql.InternalError:
    cur.execute('DROP TABLE IF EXISTS music163Page')
    cur.execute(CREATE_TABLE)

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '518',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'JSESSIONID-WYYY=tvpsMewpAqK9Hu4tQftAb3MvM8d3WiPZze3w'
              '%2FhzZ1QEl54sOs9bF5CQsUvErDkbJXdjeVUppKfEuWPQNDP8eVybahbHyaqfM42jIb6VGvtMSBnUjAnlqBPRtkmNf0jqW4t4UzuMhj8rEvZh%2B1mRU9biVb6SI3rg8gj9anqlkC3Mh%5C8yF%3A1509195464062; _iuqxldmzr_=32; _ntes_nnid=7f1400070e7f96fa4ac2f1ba14d2bc6f,1509193664102; _ntes_nuid=7f1400070e7f96fa4ac2f1ba14d2bc6f; _ngd_tid=ZAvQy7dFY%2F45YV6c%2Bg9P174N4pm6%2B%2F6H; MUSIC_U=3b9481272105936099f477a64bdec1665053be85f4706fa6c3eb1e91f8eb902b4dc279941d3b2925c347fabe0fc7ff2278c393f604c6f9c3af9e62a8590fd08a; __remember_me=true; __csrf=57ed70f9bec0feca55b719d448152890; __utma=94650624.853422703.1509193665.1509193665.1509193665.1; __utmb=94650624.6.10.1509193665; __utmc=94650624; __utmz=94650624.1509193665.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic',
    'Host': 'music.163.com',
    'Origin': 'http://music.163.com',
    'Referer': 'http://music.163.com/my/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 '
                  'Safari/537.36 '
}


def get_list_id():
    data = {
        'params': 'b9NREZGBUskV86T5Mu8EY6chbZOBcrrCNUmzz + '
                  'Fc6XBrcC2HxlAQxvr5UflGYtltd909qIrU1j1pi3rdH5amq3yri5RJDbSET3kPrUBxKLsvLyw / K3tfvynH / '
                  'Ej3dOBjz7zcyxXIMDCHG6ytN0y2Y7Eb5DSnEojroJFftHuo3v7mPFPyWWLwGUWhlJJYQbxbr6SisaQxf90MLdjvxAMuy7FaoiYSjiM0NRir4fCk1yQ =',
        'encSecKey': 'bfb092e6b6d56728b444d845407b1c0202588999db488f5ece210751236d0d5086928e8b9a1553310d0c75a88a6ab0839cd9f14003d4f8984d3a75920a0629a17a53607103e6f0d3dde63bcedc17bee9741d67263faa9ad260f7d646842218f60029a6ea4b609276b6f7d634752415cac6ae2f7c7863daba4a0cdcaa5e4ca1cf '
    }
    url = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token=57ed70f9bec0feca55b719d448152890'
    J = requests.post(url, data=data, headers=headers).text
    Jdic = json.loads(J)
    print(Jdic['playlist']['trackIds'])
    return Jdic['playlist']['trackIds']


def get_song_detail(song_ids):
    for item in song_ids:
        ID = item['id']
        url = "http://music.163.com/#/song?id=%s" % ID
        browser.get(url)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#g_iframe')))
        except TimeoutException:
            print('正在重新请求网页', url)
            get_song_detail(song_ids)
        browser.switch_to.frame('contentFrame')
        song_name = browser.find_element_by_class_name("f-ff2").text
        patten = re.compile('.*?(<h3 class="u-hd4">精彩评论.*?<h3 class="u-hd4">最新评论.*?>)', re.S)
        result = re.search(patten, browser.page_source)
        if result:
            page = re.search(patten, browser.page_source).groups(1)[0]
            html = BeautifulSoup(page, 'lxml')
            total = html.findAll("h3")[1].get_text()[5:-1]
            comments = html.findAll("", {"class": "cntwrap"})
            for comment in comments:
                like_item = comment.find("", {"data-type": "like"})
                if like_item:
                    likes = re.search(".*?(\d+万*).*", like_item.get_text()).group(1)
                else:
                    continue
                comment_data = OrderedDict(
                    song=song_name,
                    song_id=ID,
                    reviewer=comment.find("a").get_text(),
                    reviewer_home="http://music.163.com/#/" + comment.find("", {"class": "s-fc7"}).attrs['href'],
                    comment=comment.find("", {"class": "cnt f-brk"}).get_text(),
                    likes=likes,
                    time=comment.find("", {"class": "time s-fc4"}).get_text(),
                    comment_nums=total
                )
                save_to_mysql(comment_data)


def save_to_mysql(result):
    try:
        print(list(result.values()))
        cur.execute(INSERT_DATA.format(*list(result.values())))
        cur.connection.commit()
        print(result['comment'], '储存到mysql数据库成功')
    except pymysql.DatabaseError as e:
        print('储存到mysql数据库失败', e)


def main():
    ids = get_list_id()
    get_song_detail(ids)


if __name__ == '__main__':
    main()
    cur.close()
    conn.close()
