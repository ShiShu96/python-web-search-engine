# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request

from WebSpider.items import LogouItemLoader
from WebSpider.items import LagouItem
from WebSpider.utils import common


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/zhaopin/Java/']

    headers={        
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",        
        "HOST": "www.lagou.com",
        "Referer": "https://www.lagou.com/",
        "Connection": "keep-alive"
    }

    rules = (
        #Rule(LinkExtractor(allow="zhaopin/.*"), process_request='add_headers'),
        Rule(LinkExtractor(allow=r'https://www.lagou.com/jobs/\d+.html'), process_request='add_headers', callback='parse_job', follow=True),
    )

    def add_headers(self, request):
        new_request=request.replace(headers=self.headers)
        new_request.meta.update(cookiejar=1)
        return new_request

    def start_requests(self):
        yield Request(self.start_urls[0], headers=self.headers)

    def parse_job(self, response):
        # parse job information
        item_loader = LogouItemLoader(item=LagouItem(), response=response)
        item_loader.add_css("title", ".job-name span::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", common.md5(response.url))
        item_loader.add_css("salary", ".salary::text")
        item_loader.add_xpath("city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("type", "//*[@class='job_request']/p/span[5]/text()")
        item_loader.add_css("tags", ".position-label li::text")
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("advantage", ".job-advantage p::text")
        item_loader.add_css("description", ".job_bt div")
        item_loader.add_css("address", ".work_addr a::text")

        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_css("company_name", "#job_company img::attr(alt)") 

        job_item = item_loader.load_item()

        return job_item

