# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PythonbooksItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    author = scrapy.Field()
    translator = scrapy.Field()
    publisher = scrapy.Field()
    publish_time = scrapy.Field()
    comments_num = scrapy.Field()
    good_cnt_ratio = scrapy.Field()