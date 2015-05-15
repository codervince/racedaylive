import re

import scrapy
from scrapy import log
from racedaylive import items
from datetime import datetime

class RaceSpider(scrapy.Spider):

    name = 'race'
    allowed_domains = ['racing.scmp.com', 'hkjc.com']
    count_all_horse_requests = 0
    count_unique_horse_request = 0
    code_set = set()
    
    def __init__(self, racedate, coursecode, *args, **kwargs):
        assert coursecode in ['ST', 'HV']
        assert len(racedate) == 8 and racedate[:2] == '20'
        
        super(RaceSpider, self).__init__(*args, **kwargs)
        self.hkjc_domain = 'racing.hkjc.com'
        self.after_login_url = 'http://{domain}/racing/Info/Meeting/RaceCard'\
            '/English/Local/{racedate}/{coursecode}/1'.format(
                domain=self.hkjc_domain,
                racedate=racedate, 
                coursecode=coursecode,
        )
        self.start_urls = [
            'http://racing.scmp.com/login.asp'
        ]

    def parse(self, response):
        return scrapy.http.FormRequest.from_response(
            response,
            formdata={'Login': 'luckyvince', 'Password': 'invader'},
            callback=self.after_login,
        )

    def after_login(self, response):
        return scrapy.Request(self.after_login_url, callback=self.parse_races)

    def parse_races(self, response):
        race_paths = response.xpath('//td[@nowrap="nowrap" and @width="24px"]'
            '/a/@href').extract()
        urls = ['http://{domain}{path}'.format(
                domain=self.hkjc_domain,
                path=path,
            ) for path in race_paths
        ] + [response.url]
        for url in urls:
            if int(url.split('/')[-1]) > 9:
                racenumber = '{}'.format(url.split('/')[-1])
            else:
                racenumber = '0{}'.format(url.split('/')[-1])
            request = scrapy.Request(url, callback=self.parse_race)
            request.meta['racenumber'] = racenumber
            yield request

    def parse_race(self, response):

        racename_ = response.xpath('//table[@class="font13 lineH20 tdAlignL"]'
            '//span[@class="bold"]/text()').extract()[0]
        racename = re.match(r'^Race \d+.{3}(?P<name>.+)$', racename_
            ).groupdict()['name']

        for tr in response.xpath('(//table[@class="draggable hiddenable"]//tr)'
                '[position() > 1]'):

            horsenumber = tr.xpath('td[1]/text()').extract()[0]
            horsename = tr.xpath('td[4]/a/text()').extract()[0]

            horsecode_ = tr.xpath('td[4]/a/@href').extract()[0]
            horsecode = re.match(r"^[^\?]+\?horseno=(?P<code>\w+)'.*$",
                horsecode_).groupdict()['code']
            self.code_set.add(horsecode)
            log.msg('-------------------------------------------------', level=log.INFO)
            log.msg('code_set', level=log.INFO)
            log.msg(str(len(self.code_set)), level=log.INFO)

            jockeycode_ = tr.xpath('td[7]/a/@href').extract()[0]
            jockeycode = re.match(r"^[^\?]+\?jockeycode=(?P<code>\w+)'.*",
                jockeycode_).groupdict()['code']

            request = scrapy.Request('http://www.hkjc.com/english/racing/horse.'
                'asp?horseno={}'.format(horsecode), callback=self.parse_horse)
            request.meta.update(response.meta)
            request.meta.update(
                racename=racename,
                horsenumber=horsenumber,
                horsename=horsename,
                horsecode=horsecode,
                jockeycode=jockeycode,
            )

            yield request

    def parse_horse(self, response):
        RaceSpider.count_unique_horse_request += 1
        log.msg('RaceSpider.count_unique_horse_request', level=log.INFO)
        log.msg(str(RaceSpider.count_unique_horse_request), level=log.INFO)
        
        totalstakes = response.xpath('//td[preceding-sibling::td[1]/font['
            'text() = "Total Stakes*"]]/font/text()').extract()[0]

        best_url = 'http://racing.scmp.com/statistic_chart/bestfinish{}.asp'
        request = scrapy.Request(best_url.format(response.meta['racenumber']),
            callback=self.parse_best)
        request.meta.update(response.meta)
        request.meta.update(totalstakes=totalstakes)

        yield request

    def parse_best(self, response):

        # log bestfinishes
        scrapy.log.msg(response.url, level=scrapy.log.INFO)

        tr_selector = '//tr[td/font/b[text()="{horsename}"]] | //tr[td/font/b'\
            '[text()="{horsename}"]]/following-sibling::tr'.format(
            horsename=response.meta['horsename'])
        besttimes = []
        for i, tr in enumerate(response.xpath(tr_selector)):
            if i > 0 and (tr.xpath('td/font/b/text()').extract() or
                    not tr.xpath('td[1][not(font) and not(@colspan)]').extract()):
                break
            besttimes_ = tr.xpath('td[3]/font/text()').extract()[0]
            besttimes.append(re.match(r'^.*\((?P<time>.+)\)$', besttimes_
                ).groupdict()['time'])

        tips_url = 'http://racing.scmp.com/racecardpro/racecardpro{}.asp'
        request = scrapy.Request(tips_url.format(response.meta['racenumber']),
            callback=self.parse_tips)
        request.meta.update(response.meta)
        request.meta.update(besttimes=besttimes)

        return request

    def parse_tips(self, response):

        tips = {}
        for tip_ in response.xpath('//table//font/select/option[contains('
                'text(), "--")]/text()').extract():
            tip = re.match(r'^(?P<val>[^-].+\d)[^\d]*--[^A-Z]*(?P<name>.+)\r\n',
                tip_).groupdict()
            tips.update({tip['name']: tip['val'].replace(u'\xa0', u'')})

        return items.RaceItem(
            racename=response.meta['racename'],
            horsenumber=response.meta['horsenumber'],
            horsename=response.meta['horsename'],
            horsecode=response.meta['horsecode'],
            jockeycode=response.meta['jockeycode'],
            totalstakes=response.meta['totalstakes'],
            besttimes=response.meta['besttimes'],
            tips=tips,
        )
