# -*- coding: utf-8 -*-
import scrapy
from twitterscraper import query_tweets 

class TwitterSpider(scrapy.Spider):
    name = 'twitter'
    allowed_domains = ['twitter.com']
    start_urls = ['http://twitter.com/']

    def parse(self, response):
        """grab tweets with links"""
        query = "filter:links filter:verified (carbon OR warming OR climate OR wildfire OR epa)"

    
    def parse_link(self):
        
