import os
from hashlib import md5
from urllib.parse import urlencode
import re
from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import pymysql
import json
from config import *

headers = {
    'Connection': 'keep-alive',
    'Content-Encoding': 'gzip',
    'Content-Type': 'application/json',
    'Host': 'www.toutiao.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 '
                  'Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3
    }
    url = 'http://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引出错')
        return None


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


def get_page_detail(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print(('请求详情页出错', url))
        return None


def parse_page_detail(html, url):
    bp = BeautifulSoup(html, 'lxml')
    title = bp.find("title").get_text()
    pattern = re.compile('gallery: (.*?)]},', re.S)
    result = re.search(pattern, html)
    if result:
        data = json.loads(result.group(1) + ']}')
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images:
                save_image(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }


def save_image(url):
    print('正在下载', url)
    content = None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content
    except RequestException:
        print(('请求详情页出错', url))
    if content:
        file_path = '{0}\\{1}.{2}'.format(os.path.join(os.getcwd(), 'images'), 
                                          md5(content).hexdigest(), 'jpg')
        if not os.path.exists(file_path):
            with open(file_path, 'wb', ) as f:
                f.write(content)
    else:
        print('下载失败')


def save_to_mysql(result):
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='xk200900330022', db='mysql')
    cur = conn.cursor()
    cur.execute('USE scraping')
    try:
        cur.execute(INSERT_DATA.format(result['title'].encode('utf-8'),
                                       result['url'],
                                       str(result['images'])))
        cur.connection.commit()
        print('储存到mysql数据库成功')
    except pymysql.DatabaseError as e:
        print('储存到mysql数据库失败', e)
    cur.close()
    conn.close()

def save_to_file(result):
    with open(os.path.join(os.getcwd(), 'data.txt'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')
        print("写入文件成功")


def main(offset, keywords=KEYWORDS):
    html = get_page_index(offset, keywords)
    if html:
        for url in parse_page_index(html):
            html = get_page_detail(url)
            if html:
                result = parse_page_detail(html, url)
                if result: save_to_mysql(result)


if __name__ == '__main__':
    groups = [x * 20 for x in range(GROUP_START, GROUP_END + 1)]
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='xk200900330022', db='mysql')
    cur = conn.cursor()
    cur.execute('USE scraping')
    try:
        cur.execute(CREATE_TABLR)
    except pymysql.InternalError:
        cur.execute('DROP TABLE IF EXISTS ToutiaoPage')
        cur.execute(CREATE_TABLR)
    cur.close()
    conn.close()
    '''
    for x in groups:
        main(x)
    '''
    pool = Pool()
    pool.map(main, groups)
