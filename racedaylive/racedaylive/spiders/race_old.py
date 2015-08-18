# import re

# import scrapy
# from scrapy import log
# from racedaylive import items
# from datetime import datetime

# class RaceSpider(scrapy.Spider):

#     name = 'race'
#     allowed_domains = ['racing.scmp.com', 'hkjc.com']
#     count_all_horse_requests = 0
#     count_unique_horse_request = 0
#     code_set = set()
    
#     def __init__(self, racedate, coursecode, *args, **kwargs):
#         assert coursecode in ['ST', 'HV']
#         assert len(racedate) == 8 and racedate[:2] == '20'
        
#         super(RaceSpider, self).__init__(*args, **kwargs)
#         self.hkjc_domain = 'racing.hkjc.com'
#         self.after_login_url = 'http://{domain}/racing/Info/Meeting/RaceCard'\
#             '/English/Local/{racedate}/{coursecode}/1'.format(
#                 domain=self.hkjc_domain,
#                 racedate=racedate, 
#                 coursecode=coursecode,
#         )
#         self.start_urls = [
#             'http://racing.scmp.com/login.asp'
#         ]

#     def parse(self, response):
#         return scrapy.http.FormRequest.from_response(
#             response,
#             formdata={'Login': 'luckyvince', 'Password': 'invader'},
#             callback=self.after_login,
#         )

#     def after_login(self, response):
#         return scrapy.Request(self.after_login_url, callback=self.parse_races)

#     def parse_races(self, response):
#         race_paths = response.xpath('//td[@nowrap="nowrap" and @width="24px"]'
#             '/a/@href').extract()
#         urls = ['http://{domain}{path}'.format(
#                 domain=self.hkjc_domain,
#                 path=path,
#             ) for path in race_paths
#         ] + [response.url]
#         for url in urls:
#             if int(url.split('/')[-1]) > 9:
#                 racenumber = '{}'.format(url.split('/')[-1])
#             else:
#                 racenumber = '0{}'.format(url.split('/')[-1])
#             request = scrapy.Request(url, callback=self.parse_race)
#             request.meta['racenumber'] = racenumber
#             yield request

#     def parse_race(self, response):

#         racename_ = response.xpath('//table[@class="font13 lineH20 tdAlignL"]'
#             '//span[@class="bold"]/text()').extract()[0]
#         racename = re.match(r'^Race \d+.{3}(?P<name>.+)$', racename_
#             ).groupdict()['name']

#         for tr in response.xpath('(//table[@class="draggable hiddenable"]//tr)'
#                 '[position() > 1]'):

#             horsenumber = tr.xpath('td[1]/text()').extract()[0]
#             horsename = tr.xpath('td[4]/a/text()').extract()[0]

#             horsecode_ = tr.xpath('td[4]/a/@href').extract()[0]
#             horsecode = re.match(r"^[^\?]+\?horseno=(?P<code>\w+)'.*$",
#                 horsecode_).groupdict()['code']
#             self.code_set.add(horsecode)
#             log.msg('-------------------------------------------------', level=log.INFO)
#             log.msg('code_set', level=log.INFO)
#             log.msg(str(len(self.code_set)), level=log.INFO)

#             jockeycode_ = tr.xpath('td[7]/a/@href').extract()[0]
#             jockeycode = re.match(r"^[^\?]+\?jockeycode=(?P<code>\w+)'.*",
#                 jockeycode_).groupdict()['code']

#             request = scrapy.Request('http://www.hkjc.com/english/racing/horse.'
#                 'asp?horseno={}'.format(horsecode), callback=self.parse_horse)
#             request.meta.update(response.meta)
#             request.meta.update(
#                 racename=racename,
#                 horsenumber=horsenumber,
#                 horsename=horsename,
#                 horsecode=horsecode,
#                 jockeycode=jockeycode,
#             )

#             yield request

#         tips_url = 'http://racing.scmp.com/racecardpro/racecardpro{}.asp'
#         request = scrapy.Request(tips_url.format(response.meta['racenumber']),
#             callback=self.parse_tips)
#         request.meta.update(response.meta)

#         yield request

#     def parse_horse(self, response):
#         RaceSpider.count_unique_horse_request += 1
#         log.msg('RaceSpider.count_unique_horse_request', level=log.INFO)
#         log.msg(str(RaceSpider.count_unique_horse_request), level=log.INFO)
        
#         totalstakes = response.xpath('//td[preceding-sibling::td[1]/font['
#             'text() = "Total Stakes*"]]/font/text()').extract()[0]

#         yield items.HorseItem(
#             racename=response.meta['racename'],
#             horsenumber=response.meta['horsenumber'],
#             horsename=response.meta['horsename'],
#             horsecode=response.meta['horsecode'],
#             jockeycode=response.meta['jockeycode'],
#             totalstakes=totalstakes,
#         )

#     def parse_tips(self, response):

#         tips = {}
#         for tip_ in response.xpath('//table//font/select/option[contains('
#                 'text(), "--")]/text()').extract():
#             tip = re.match(r'^(?P<val>[^-].+\d)[^\d]*--[^A-Z]*(?P<name>.+)\r\n',
#                 tip_).groupdict()
#             tips.update({tip['name']: tip['val'].replace(u'\xa0', u'')})

#         comments_url = 'http://racing.scmp.com/RaceCardPro/comment{}.asp'.format(
#             response.meta['racenumber'])

#         for horsename in response.xpath('//tr//tr//table[@bgcolor="#A70E13"]'
#                 '//tr[@bgcolor="white"]/td[4]//a/text()').extract():

#             request = scrapy.Request(comments_url, callback=self.parse_comments)
#             request.meta.update(response.meta)
#             request.meta.update(tips=tips)
#             request.meta.update(horsename=horsename)
    
#             yield request

#     def parse_comments(self, response):

#         comment_ = response.xpath('//td[font[contains(text(), "{}")]]/'
#             'following-sibling::td/font/text()'.format(
#             response.meta['horsename'])).extract()
#         comment = comment_ and comment_[0]

#         workouts_url = 'http://racing.scmp.com/Trackwork/Summary/Summary{}.asp'.format(
#             response.meta['racenumber'])
#         request = scrapy.Request(workouts_url, callback=self.parse_workouts)
#         request.meta.update(response.meta)
#         request.meta.update(comment=comment)

#         return request

#     '''
#     http://racing.scmp.com/Trackwork/Summary/Summary{}.asp
#     1> L1_days 31-60 workout today <= 7 days?
#     2> L1_days 61+ TW= 1000m+ <=14d?
#     3> WIN TW? (BT) 
#     '''
#     def parse_workouts(self, response):


#         tr = response.xpath('//tr[td[2]//a[text() = "{}"]]'.format(
#             response.meta['horsename']))

#         font = tr.xpath('td[8]/font')

#         #get column headers
#         # headertexts_ = response.xpath("//table[@bgcolor='#A70E13']//tr[@bgcolor='#A70E13']//td[@valign='TOP']/center/b/font//text()")
#         # raceday = self.racedate[-2:]
        


#         ##WORKOUTS HERE
#         totaljump_ = font.xpath('font[1]/text()').extract()[0]
#         totaljump = re.match(r'^Jump:[^\d]+(?P<num>\d+)$', totaljump_
#             ).groupdict()['num']


#         totalcanter_ = font.xpath('text()[2]').extract()[0][3:]
#         totalcanter = re.match(r'^.*Canter: (?P<num>\d+)$', totalcanter_
#             ).groupdict()['num']

#         ##DID H WIN?
#         totalbarrier_ = font.xpath('font[2]/text()').extract()[0]
#         totalbarrier = re.match(r'^Barrier: (?P<num>\d+)$', totalbarrier_
#             ).groupdict()['num']

#         # totalswim_ = font.xpath('text()[3]').extract()[0][7:]
#         # totalswim = re.match(r'^.*Swim: (?P<num>\d+)$', totalswim_
#         #     ).groupdict()['num']

#         BTNumber_url = tr.xpath('td[4]//a/@href').extract()
#         BTNumber = None
#         if BTNumber_url:
#             BTNumber_re = re.match(r'../../Trackwork/barrier/2015/(?P<num>\d+).asp',
#                 BTNumber_url[0])
#             BTNumber = BTNumber_re and BTNumber_re.groupdict()['num']

#         best_url = 'http://racing.scmp.com/statistic_chart/bestfinish{}.asp'
#         request = scrapy.Request(best_url.format(response.meta['racenumber']),
#             callback=self.parse_best)
#         request.meta.update(response.meta)
#         request.meta.update(totaljump=totaljump)
#         request.meta.update(totalcanter=totalcanter)
#         request.meta.update(totalbarrier=totalbarrier)
#         # request.meta.update(totalswim=totalswim)
#         request.meta.update(BTNumber=BTNumber)

#         yield request

#     def parse_best(self, response):

#         # log bestfinishes
#         scrapy.log.msg(response.url, level=scrapy.log.INFO)

#         tr_selector = '//tr[td/font/b[text()="{horsename}"]] | //tr[td/font/b'\
#             '[text()="{horsename}"]]/following-sibling::tr'.format(
#             horsename=response.meta['horsename'])
#         besttimes = []
#         for i, tr in enumerate(response.xpath(tr_selector)):
#             if i > 0 and (tr.xpath('td/font/b/text()').extract() or
#                     not tr.xpath('td[1][not(font) and not(@colspan)]').extract()):
#                 break
#             besttimes_ = tr.xpath('td[3]/font/text()').extract()[0]
#             besttimes.append(re.match(r'^.*\((?P<time>.+)\)$', besttimes_
#                 ).groupdict()['time'])

#         return items.RaceItem(
#             besttimes=besttimes,
#             tips=response.meta['tips'],
#             comment=response.meta['comment'],
#             totaljump=response.meta['totaljump'],
#             totalcanter=response.meta['totalcanter'],
#             totalbarrier=response.meta['totalbarrier'],
#             # totalswim=response.meta['totalswim'],
#             BTNumber=response.meta['BTNumber'],
#             horsename=response.meta['horsename'],
#         )