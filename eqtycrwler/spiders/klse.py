# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.selector import Selector
from eqtycrwler.items import EqtycrwlerItem


class KlseSpider(scrapy.Spider):
    name = 'klse'
    allowed_domains = ['bursamalaysia.com',
                       'finance.yahoo.com',
                       'msn.com']
    curr_page = 1
    tbl_url = 'http://ws.bursamalaysia.com/market/securities/equities/prices/prices_f.html?page=%d'
    yhoo_suffix = 'KL'
    yhoo_url = 'http://finance.yahoo.com/q/pr?s=%s+Profile'
    # details of fallback url if yahoo does not have a profile
    fb_suffix = 'KLS'
    fb_url = 'http://www.msn.com/en-us/money/stockdetails/company/fi-135.1.%s'

    def start_requests(self):
        return [scrapy.Request(self.tbl_url % 1, callback=self.parse_table_rows)]

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
        profile = response.xpath('//*[(@id = "yfncsumtab")]//p/text()').extract_first()
        if not ('There is no Profile data available' in profile):
            item['yhoo_profile'] = profile
            yield item
        else:
            self.logger.info("No profile found for %s on Yahoo" % item['short_name'])
            yield scrapy.Request(self.fb_url % '.'.join([item['code'], self.fb_suffix]),
                                 callback=self.fallback_profile,
                                 meta={'item': item})

    def fallback_profile(self, response):
        item = response.meta['item']
        item['yhoo_profile'] = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "toggle-text", " " ))]/text()').extract_first()
        yield item
