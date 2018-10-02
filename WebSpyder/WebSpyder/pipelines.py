# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import pymysql
import pymysql.cursors
from scrapy.http import Request

from scrapy.pipelines.images import ImagesPipeline

class WebspyderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()

class MyImagePipeline(ImagesPipeline):
    '''
    pipeline for downloading images
    '''
    def get_media_requests(self, item, info):
        return Request(item['front_image_url'])
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            item['front_image_path']=image_paths[0]
        else:
            item['front_image_path']=""

        return item


class MysqlPipeline(object):
    '''
    pipeline for inserting item into mysql database
    '''
    def __init__(self):
        self.conn = pymysql.connect('localhost', 'root', '12345678', 'search_engine', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        self.insert(self.cursor, item)

    def insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)  
        self.conn.commit() 
        
