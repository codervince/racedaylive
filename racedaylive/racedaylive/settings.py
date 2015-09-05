# -*- coding: utf-8 -*-

# Scrapy settings for racedaylive project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
from datetime import datetime

BOT_NAME = 'racedaylive'

ITEM_PIPELINES = {
	
	"racedaylive.pipelines.RacedaylivePipeline":100,
	# "racedaylive.pipeline2.SQLAlchemyPipeline":50
}

SPIDER_MODULES = ['racedaylive.spiders']
NEWSPIDER_MODULE = 'racedaylive.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'racedaylive (+http://www.yourdomain.com)'

DUPEFILTER_CLASS = 'racedaylive.utils.DoNotFilter'
LOG_FILE = "scrapy_%s_%s.log" % ('racedaylive', datetime.now().date())
# LOG_FILE = 'C:/Users/Simon/RACING/SCRAPY/racedaylive/racedaylive/log.txt'

DOWNLOAD_DELAY = 0.25    # 250 ms of delay

AUTOTHROTTLE_ENABLED = True

SCMP_USER = 'luckyvince'
SCMP_PASSWORD = 'invader'

#LOCALHOST
DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': 'vmac',
    'password': '',
    'database': 'hkraces_aug15'
}
