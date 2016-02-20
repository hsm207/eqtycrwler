# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.selector import Selector
from eqtycrwler.items import EqtycrwlerItem


class KlseSpider(scrapy.Spider):
    name = 'klse'
    allowed_domains = ['bursamalaysia.com',
                       'finance.yahoo.com']
    start_urls = [
        'http://ws.bursamalaysia.com/market/securities/equities/prices/prices_f.html?page=1'
    ]
    yhoo_suffix = 'KL'
    yhoo_url = 'http://finance.yahoo.com/q/pr?s=%s+Profile'
    tbl_url = 'http://ws.bursamalaysia.com/market/securities/equities/prices/prices_f.html?page='

    def parse(self, response):
        max_page = 0
        current_page = 1

        # Get the json portion of response
        resp_json = json.loads(response.body)
        max_page = int(Selector(text=resp_json['pagination']).xpath('//span/text()').extract_first())

        while current_page <= max_page:
            yield scrapy.Request(self.tbl_url + str(current_page), callback=self.parse_table)
            current_page += 1

    def parse_table(self, response):
        self.logger.info("Visiting %s", response.url)
        tbl = json.loads(response.body)['html']
        for row in Selector(text=tbl).xpath('//tbody/tr'):
            item = EqtycrwlerItem()
            item['code'] = row.xpath('(./td)[2]/text()').extract_first()
            item['short_name'] = row.xpath('(./td)[3]/a/text()').extract_first()
            item['bursa_profile'] = response.urljoin(row.xpath('(./td)[3]/a/@href').extract_first())
            yield scrapy.Request(self.yhoo_url % '.'.join([item['code'], self.yhoo_suffix]),
                                 callback=self.parse_profile,
                                 meta={'item': item}
                                 )

    def parse_profile(self, response):
        self.logger.info("Visiting %s", response.url)
        item = response.meta['item']
        item['yhoo_profile'] = response.xpath('//*[(@id = "yfncsumtab")]//p/text()').extract_first()
        yield item
