# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re
import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from WebSpider.models.es_models import ArticleType, JobType
from elasticsearch_dsl.connections import connections


class WebSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

def clean_date(value):
    return value.replace('·','').strip()

def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value

class JobboleItemLoader(ItemLoader):
    default_output_processor=TakeFirst()

def gen_suggests(es, index, info_tuple):
    # generate search suggestion array
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})

    return suggests

class JobboleItem(scrapy.Item):
    title=scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(clean_date)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, create_date, fav_nums, front_image_url, front_image_path,
            praise_nums, comment_nums, tags, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(fav_nums)
        """

        params = (self["title"], self["url"], self["url_object_id"], self["create_date"], self["fav_nums"],
                  self["front_image_url"], self["front_image_path"], self["praise_nums"], self["comment_nums"],
                  self["tags"], self["content"])

        return insert_sql, params   

    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self["create_date"]
        article.content = remove_tags(self["content"])
        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.praise_nums = self["praise_nums"]
        article.fav_nums = self["fav_nums"]
        article.comment_nums = self["comment_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.meta.id = self["url_object_id"]

        es = connections.create_connection(ArticleType._doc_type.using)
        article.suggest = gen_suggests(es, ArticleType._doc_type.index, ((article.title,10),(article.tags, 7)))

        article.save()

        return


def drop_splash(value):
    return value.replace("/","")

def clean_addr(addr_list):
    new_addr_list=[addr.strip() for addr in addr_list if addr.strip()!="查看地图"]
    return ",".join(new_addr_list)

class LogouItemLoader(ItemLoader):
    default_output_processor=TakeFirst()

class LagouItem(scrapy.Item):
    # lagou job information
    url=scrapy.Field()
    url_object_id=scrapy.Field()
    title=scrapy.Field()
    salary=scrapy.Field()
    city=scrapy.Field(
        input_processor=MapCompose(drop_splash)
    )
    work_years=scrapy.Field(
        input_processor=MapCompose(drop_splash)
    )
    degree=scrapy.Field(
        input_processor=MapCompose(drop_splash)
    )
    type=scrapy.Field()
    publish_time=scrapy.Field()
    tags=scrapy.Field(
        input_processor=Join(",")
    )
    advantage=scrapy.Field()
    description=scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    address=scrapy.Field(
        input_processor=clean_addr
    )
    company_url=scrapy.Field()
    company_name=scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert ignore into lagou_job(title, url, url_object_id, salary, city, work_years, degree, tags, 
            type, publish_time, advantage, description, address, company_url, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params=(self["title"], self["url"], self["url_object_id"], self["salary"], self["city"], self["work_years"], self["degree"], self["tags"],
                  self["type"], self["publish_time"], self["advantage"], self["description"], self["address"], self["company_url"],
                  self["company_name"])

        return insert_sql, params

    def save_to_es(self):
        job=JobType()
        job.title=self["title"]
        job.url=self["url"]
        job.url_object_id=self["url_object_id"]
        job.salary=self["salary"]
        job.degree=self["degree"]
        job.city=self["city"]
        job.work_years=self["work_years"]
        job.type=self["type"]
        job.publish_time=self["publish_time"]
        job.tags=self["tags"]
        job.description=self["description"]
        job.address=self["address"]
        job.company_name=self["company_name"]
        job.company_url=self["company_url"]

        es = connections.create_connection(JobType._doc_type.using)
        job.suggest = gen_suggests(es, JobType._doc_type.index, ((job.title,10),(job.tags, 7)))

        job.save()

        return