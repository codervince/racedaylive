# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RaceItem(scrapy.Item):
    racedate = scrapy.Field()
    racenumber = scrapy.Field()
    localracetime = scrapy.Field()
    utcracetime = scrapy.Field()
    racetype = scrapy.Field()
    racecourse =scrapy.Field()
    racecoursecode =scrapy.Field()
    racedistance =scrapy.Field()
    racesurface = scrapy.Field()
    horsename = scrapy.Field()
    tips = scrapy.Field()
    comment = scrapy.Field()
    totaljump = scrapy.Field()
    totalcanter = scrapy.Field()
    totalbarrier = scrapy.Field()
    totalswim = scrapy.Field()
    BTNumber = scrapy.Field()
    besttimes = scrapy.Field()
    standard_deviation = scrapy.Field()
    avgdistance = scrapy.Field()
    internalraceindex = scrapy.Field()


class HorseItem(scrapy.Item):
    horsename = scrapy.Field()
    racename = scrapy.Field()
    racedate = scrapy.Field()
    racenumber = scrapy.Field()
    horsenumber = scrapy.Field()
    horsecode = scrapy.Field()
    jockeycode = scrapy.Field()
    totalstakes = scrapy.Field()
    lastwonat = scrapy.Field()
    isMaiden = scrapy.Field()
    invalid_dates = scrapy.Field()
