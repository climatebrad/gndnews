# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import datetime

class EartherPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('earther_items.json', 'w')
        self.file.write("[\n")
        
    def close_spider(self, spider):
        self.file.write("{}]\n")
        self.file.close()
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + ",\n"
        self.file.write(line)
        return item

encoding='utf-8'
# with open('earther_items.json') as f:
#     for line in f:
#         data.append(json.loads(line))

import pymongo

class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_port, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.collection_name = collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_SERVER'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            collection_name=crawler.settings.get('MONGO_COLLECTION', 'scrapy_items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
        self.db = self.client[self.mongo_db]
        
        
    def close_spider(self, spider):
        query = { "last_scraped" : 1}
        update = { "last_scraped" : datetime.datetime.now().timestamp() }
        self.db[self.collection_name].replace_one(query, {"$set" : update}, upsert=True )
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
    
