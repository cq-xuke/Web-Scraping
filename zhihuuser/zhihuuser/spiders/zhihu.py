# -*- coding: utf-8 -*-
import json
from zhihuuser.items import UserItem
import scrapy
from scrapy import Spider, Request


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    start_user = 'excited-vczh'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'locations%2Cemployments%2Cgender%2Ceducations%2Cbusiness%2Cvoteup_count%2Cthanked_Count' \
                 '%2Cfollower_count%2Cfollowing_count%2Ccover_url%2Cfollowing_topic_count%2Cfollowing_question_count' \
                 '%2Cfollowing_favlists_count%2Cfollowing_columns_count%2Cavatar_hue%2Canswer_count%2Carticles_count' \
                 '%2Cpins_count%2Cquestion_count%2Ccolumns_count%2Ccommercial_question_count%2Cfavorite_count' \
                 '%2Cfavorited_count%2Clogs_count%2Cincluded_answers_count%2Cincluded_articles_count%2Cincluded_text' \
                 '%2Cmessage_thread_token%2Caccount_status%2Cis_active%2Cis_bind_phone%2Cis_force_renamed' \
                 '%2Cis_bind_sina%2Cis_privacy_protected%2Csina_weibo_url%2Csina_weibo_name%2Cshow_sina_weibo' \
                 '%2Cis_blocking%2Cis_blocked%2Cis_following%2Cis_followed%2Cis_org_createpin_white_user' \
                 '%2Cmutual_followees_count%2Cvote_to_count%2Cvote_from_count%2Cthank_to_count%2Cthank_from_count' \
                 '%2Cthanked_count%2Cdescription%2Chosted_live_count%2Cparticipated_live_count%2Callow_message' \
                 '%2Cindustry_category%2Corg_name%2Corg_homepage%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics '

    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(url=self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)
        yield Request(url=self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20), callback=self.parse_follows)


    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield Request(url=self.follows_url.format(user=result.get('url_token'), include=self.follows_query, limit=20, offset=0), callback=self.parse_follows)


    def parse_follows(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(url=self.user_url.format(user=result.get("url_token"), include=self.user_query), callback=self.parse_user)
        if 'paging' in results.keys() and results.get('paging').get("is_end") == False:
            next_page = results.get('paging').get('next')
            print("请注意",next_page)
            yield Request(url=next_page, callback=self.parse_follows)