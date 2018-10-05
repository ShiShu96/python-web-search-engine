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
    start_urls = [
        'https://www.lagou.com/zhaopin/Java/',
        'https://www.lagou.com/zhaopin/PHP/',
        'https://www.lagou.com/zhaopin/C++/'
    ]

    rules = (
        Rule(LinkExtractor(allow=r'https://www.lagou.com/jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def start_requests(self):
        cookies={
            '_ga':'GA1.2.294187429.1538535370',
            '_gat':"1",
            '_gid':'GA1.2.555476700.1538700093',
            'JSESSIONID':'ABAAABAAAFCAAEG457CC9AA82383E12F4689BFA3E883E95',
            'index_location_city':'%E5%8C%97%E4%BA%AC',
            'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6': '1538761761',
            'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6':'1538535371',
            'LGRID':'20181006014920-fcb28fbc-c8c6-11e8-a940-525400f775ce',
            'LGSID':'20181006014841-e57e4bd1-c8c6-11e8-bb68-5254005c3644',
            'LGUID':'20181003105615-e487e4b9-c6b7-11e8-a8c8-525400f775ce',
            'user_trace_token':'20181003105615-e487e19f-c6b7-11e8-a8c8-525400f775ce',
            'PRE_LAND':'https%3A%2F%2Fwww.lagou.com%2F',
            'X_HTTP_TOKEN':'75f8dae8da6ff8041ecf9303fd06b0ec',
        }
        for url in self.start_urls:
            yield Request(url, cookies=cookies)

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

