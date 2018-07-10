# -*- coding: utf-8 -*-
import re
import requests
import scrapy
from pythonbooks.items import PythonbooksItem


class JdbooksSpider(scrapy.Spider):
    name = "JDbooks"
    base_urls = 'https://search.jd.com/Search?keyword=python&page='
    headers = {
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-language': 'zh - CN, zh;q = 0.9',
        'Cache-Control': 'max - age = 0',
        'Connection': 'keep - alive',
        'Host': 'search.jd.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/62.0.3202.75 Safari/537.36'
    }

    def start_requests(self):
        for page in range(1, 200, 2):
            url = self.base_urls + str(page)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.Idparse)

    def Idparse(self, response):
        h = self.headers.copy()
        h.pop('Host')
        h['referer'] = response.url
        ids = response.xpath('//li[@class="gl-item"]/@data-sku').extract()
        for id_ in ids:
            link = "https://item.jd.com/%s.html" % id_
            yield scrapy.Request(link, headers=h, callback=self.Itemparse)

    def Itemparse(self, response):
        item = PythonbooksItem()
        messages = response.xpath('//div[@class="p-parameter"]/ul')
        publisher = messages.xpath('./li[contains(@clstag,"shangpin")][1]/@title').extract_first()
        publish_time = messages.xpath('./li[contains(@title,"-")]/@title').extract_first()
        name = response.xpath('//h1/text()').extract_first()
        aus = re.search("imageAndVideoJson:.*?authors: \[(.*?)\].*skuid:", response.text, re.S).group(1)
        aus = aus.replace('"', '').split(",")
        author = aus[0]
        if len(aus) > 1:
            translator = str(aus[1:]).strip("[").strip("]")
        else:
            translator = None
        id_ = re.search("https.*?(\d+).html", response.url).group(1)
        link = 'https://p.3.cn/prices/get?type=1&skuid=J_%s&callback=cnp' % id_
        h = self.headers.copy()
        h['Host'] = 'p.3.cn'
        p_dict = requests.get(link, headers=h)
        price = re.match('cnp.*?op":"(.*?)",', p_dict.text).group(1)
        link2 = 'https://sclub.jd.com/comment/productCommentSummaries.action?referenceIds=%s' % id_
        h.pop('Host')
        cnt = requests.get(link2, headers=h).text
        cnt = re.search('CommentCount.*?"CommentCount":(\d+),.*?"GoodRate":(.*?),"', cnt)
        comments_num = cnt.group(1)
        good_cnt_ratio = cnt.group(2)
        item['name'] = name
        item['price'] = price
        item['author'] = author
        item['translator'] = translator
        item['publisher'] = publisher
        item['publish_time'] = publish_time
        item['comments_num'] = comments_num
        item['good_cnt_ratio'] = good_cnt_ratio
        yield item
