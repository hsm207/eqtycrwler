# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.selector import Selector
from eqtycrwler.items import EqtycrwlerItem


class KlseSpider(scrapy.Spider):
    name = 'klse'
    allowed_domains = ['bursamalaysia.com',
                       'finance.yahoo.com']
    curr_page = 1
    yhoo_suffix = 'KL'
    yhoo_url = 'http://finance.yahoo.com/q/pr?s=%s+Profile'
    tbl_url = 'http://ws.bursamalaysia.com/market/securities/equities/prices/prices_f.html?page=%d'

    def start_requests(self):
        return [scrapy.Request(self.tbl_url + '1', callback=self.parse_table_rows)]

    def parse_table_rows(self, response):
        # Examine the table rows returned from the jquery call
        self.logger.info("Parsing page %d" % self.curr_page)
        rows = Selector(text=json.loads(response.body)['html']).xpath('//tbody/tr')
        if rows:
            for row in rows:
                item = EqtycrwlerItem()
                item['code'] = row.xpath('(./td)[2]/text()').extract_first()
                item['short_name'] = row.xpath('(./td)[3]/a/text()').extract_first()
                item['bursa_profile'] = response.urljoin(row.xpath('(./td)[3]/a/@href').extract_first())
                yield scrapy.Request(self.yhoo_url % '.'.join([item['code'], self.yhoo_suffix]),
                                     callback=self.parse_profile,
                                     meta={'item': item})
            self.curr_page += 1
            yield scrapy.Request(self.tbl_url % self.curr_page,
                                 callback=self.parse_table_rows)

    def parse_profile(self, response):
        item = response.meta['item']
        item['yhoo_profile'] = response.xpath('//*[(@id = "yfncsumtab")]//p/text()').extract_first()
        yield item
