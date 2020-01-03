"""
Crawl one article

"""

import scrapy
from scrapy.crawler import CrawlerProcess
from earther.spiders.earther_spider import EartherSpider
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(get_project_settings())

process.crawl(EartherSpider)
process.start()