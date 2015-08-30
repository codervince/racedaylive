# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
#FIRST
class HorseItem(scrapy.Item):
    ### to rd_race
    racedate = scrapy.Field() 
    racecoursecode = scrapy.Field()
    raceclass = scrapy.Field()
    racerating = scrapy.Field()
    racegoing = scrapy.Field()
    racesurface = scrapy.Field()
    trackvariant= scrapy.Field()
    racedistance=scrapy.Field()
    racenumber = scrapy.Field()
    racename = scrapy.Field()
    localracetime = scrapy.Field()
    utcracetime = scrapy.Field()
    #####
    ### to rd_runner
    horsename = scrapy.Field() #to rdhorse and id to rd_runner
    horsenumber = scrapy.Field() #to rdhorse
    horsecode = scrapy.Field() #to rdhorse
    jockeycode = scrapy.Field()
    jockeyname = scrapy.Field()
    trainercode = scrapy.Field()
    trainername = scrapy.Field()
    seasonstakes = scrapy.Field()
    todaysrating = scrapy.Field()
    lastwonat = scrapy.Field()
    isMaiden = scrapy.Field()
    ownername = scrapy.Field()
    gear = scrapy.Field()
    placing = scrapy.Field()
    finish_time = scrapy.Field()
    marginsbehindleader = scrapy.Field()
    positions = scrapy.Field()
    timelist = scrapy.Field()
    priority = scrapy.Field()
#SECOND
class RaceItem(scrapy.Item):
    #to rd_Race
    racedate = scrapy.Field() #rd_raceid
    racenumber = scrapy.Field()
    racecoursecode =scrapy.Field()
   
    horsename = scrapy.Field() #rd_horse_id
    tips = scrapy.Field()
    naps = scrapy.Field() 
    scmp_runner_comment = scrapy.Field()
    totaljump = scrapy.Field()
    totalcanter = scrapy.Field()
    totalbarrier = scrapy.Field()
    barriertimes = scrapy.Field()
    jumptimes = scrapy.Field()
    totalswim = scrapy.Field()






   