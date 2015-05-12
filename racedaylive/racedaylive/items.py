# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RaceItem(scrapy.Item):
    racename = scrapy.Field()
    horsenumber = scrapy.Field()
    horsename = scrapy.Field()
    horsecode = scrapy.Field()
    jockeycode = scrapy.Field()
    totalstakes = scrapy.Field()
    besttimes = scrapy.Field()
    tips = scrapy.Field()
