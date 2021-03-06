# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# TODO insert attribute for trading exchange
class EqtycrwlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    code = scrapy.Field()
    short_name = scrapy.Field()
    # text describing company
    yhoo_profile = scrapy.Field()
    # link to Bursa Malaysia's website with summary of latest quote, AGMs, CAs, etc
    bursa_profile = scrapy.Field()
    profile_link = scrapy.Field()
    # store the row number of a security for comparison purposes
    row_num = scrapy.Field()
    scrape_time = scrapy.Field()
