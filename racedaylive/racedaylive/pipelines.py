# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pprint as pp

class RacedaylivePipeline(object):
    def process_item(self, item, spider):
		pp.pprint(RaceSpider.code_set)        
        return item


## COMMENT SEPARATE TABLE