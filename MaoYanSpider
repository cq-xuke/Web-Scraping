import json
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from requests.exceptions import RequestException

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 '
                  'Safari/537.36 '
}


def get_one_page(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def pase_one_page(html):
    bp = BeautifulSoup(html, 'lxml')
    dds = bp.findAll("dd")
    for dd in dds:
        yield dict(
            name=dd.find("p", {"class": "name"}).find("a").get_text(),
            star=dd.find("p", {"class": "star"}).get_text().strip()[3:],
            time=dd.find("p", {"class": "releasetime"}).get_text()[5:],
            score=dd.find("i", {"class": "integer"}).get_text() + dd.find("i", {"class": "fraction"}).get_text()
        )


def write_into(content):
    with open(r'C:\Users\cq_xuke\Desktop\Python Learning\movies.text', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(pages):
    html = get_one_page('http://maoyan.com/board/4?offset=%s' % (pages * 10))
    if html:
        for item in pase_one_page(html):
            print(item)
            write_into(item)


if __name__ == '__main__':
    pools = Pool()
    pools.map(main, range(10))
