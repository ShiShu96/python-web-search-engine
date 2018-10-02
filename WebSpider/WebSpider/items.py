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