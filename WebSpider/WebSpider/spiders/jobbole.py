 # -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse

from WebSpider.items import JobboleItemLoader
from WebSpider.utils import common
from WebSpider.items import JobboleItem

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1. get all articles in current page and parse 
        '''
        post_nodes=response.css("#archive .floated-thumb .post-thumb a")
        for node in post_nodes:
            img_url=node.css("img::attr(src)").extract_first("")
            post_url=node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":img_url}, callback=self.parse_detail)
        '''
        2. get the url of next page and repeat parsing
        '''
        # next_url = response.css(".next.page-numbers::attr(href)").extract_first("")        
        # if next_url:
        #     yield Request(url=arse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):

        '''extract details of an article'''
        front_image_url = response.meta.get("front_image_url", "") 
        item_loader=JobboleItemLoader(item=JobboleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", common.md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item=item_loader.load_item()

        yield article_item
