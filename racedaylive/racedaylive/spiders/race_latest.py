import re

import scrapy
from scrapy import log
from racedaylive import items
from datetime import datetime
from racedaylive.utilities import *
from dateutil.parser import parse
import pprint

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
        self.domain = 'hkjc.com'
        self.racedate = racedate
        self.racecoursecode = coursecode
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
        #HKJC racecard
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


        raceinfo_ = response.xpath('//table[@class="font13 lineH20 tdAlignL"]//descendant::text()[ancestor::td and normalize-space(.) != ""][position()>=2]').extract()
        date_racecourse_localtime = cleanstring(raceinfo_[0])
        surface_distance = cleanstring(raceinfo_[1])
        prize_rating_class = cleanstring(raceinfo_[2])
        
        racecourse = None
        localtime= None
        if date_racecourse_localtime:
             
            racecourse = unicode.strip(unicode.split(date_racecourse_localtime, u',')[-2])
            localtime = unicode.strip(unicode.split(date_racecourse_localtime, u',')[-1])
        distance = None
        surface = None
        if surface_distance:
            surface = unicode.strip(unicode.split(surface_distance, u',')[-2])
            distance = unicode.strip(unicode.split(surface_distance, u',')[0].replace('M',''))

        racerating = None
        raceclass = None
        if prize_rating_class:
            racerating = unicode.strip(unicode.split(prize_rating_class, u',')[-2].replace(u'Rating:', ''))
            raceclass = unicode.strip(unicode.split(prize_rating_class, u',')[-1].replace(u'Class', ''))

        ##RaceType racecourse numberofrunners surface distance going

        # Turf, "A" Course
        # surface = re.match(r'^[^,](?P<surface>.+),.*', raceinfo_).groupdict()['surface']

        # pprint.pprint(surface_distance)
        # pprint.pprint(prize_rating_class)
        # rating = re.match(r'^Rating:\d{2-3}-\d{2-3}(?P<rating>.+).*'), raceinfo_).groupdict()['rating']

        ### RaceCategory RACETIME SURFACE DISTANCE GOING 
        ### PM RATING CLASS  

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
            
            ##TRAINER CODE
            trainercode_ = tr.xpath('td[10]/a/@href').extract()[0]
            trainercode = re.match(r"^[^\?]+\?trainercode=(?P<code>\w+)'.*",
                trainercode_).groupdict()['code']

            todaysrating_ = tr.xpath('td[11]/text()').extract()[0]
            owner_ = tr.xpath('td[22]/text()').extract()[0]
            gear_ = tr.xpath('td[21]/text()').extract()[0]

            request = scrapy.Request('http://www.hkjc.com/english/racing/horse.'
                'asp?horseno={}'.format(horsecode), callback=self.parse_horse)
            request.meta.update(response.meta)
            request.meta.update(
                localtime=localtime,
                racename=racename,
                racecourse=racecourse,
                racesurface=surface,
                racedistance=distance,
                raceclass=raceclass,
                racerating= racerating,
                racedate = self.racedate,
                horsenumber=horsenumber,
                horsename=horsename,
                horsecode=horsecode,
                jockeycode=jockeycode,
                trainercode=trainercode,
                todaysrating=todaysrating_,
                owner=owner_,
                gear=gear_
            )
            yield request

        tips_url = 'http://racing.scmp.com/racecardpro/racecardpro{}.asp'
        request = scrapy.Request(tips_url.format(response.meta['racenumber']),
            callback=self.parse_tips)
        request.meta.update(response.meta)
        yield request

        
        result_path = response.xpath('//ul[@id="navmenu-h"]//'
            'a[text()="Results"]/@href').extract()[0]
        result_url = 'http://{domain}/{path}'.format(
            domain=self.hkjc_domain, path=result_path)
        request = scrapy.Request(result_url, callback=self.parse_results)
        request.meta.update(response.meta)
        yield request

    def parse_results(self, response):
        sectional_time_url = response.xpath('//div[@class="rowDiv15"]/div['
            '@class="rowDivRight"]/a/@href').extract()[0]
        request = scrapy.Request(sectional_time_url, callback=
            self.parse_sectional_time)
        request.meta.update(response.meta)
        yield request

    def parse_sectional_time(self, response):

        horse_lines_selector = response.xpath('//table[@class="bigborder"]//'
            'table//a/../../..')
        sectional_time_selector = response.xpath('//table[@class='
            '"bigborder"]//table//a/../../../following-sibling::tr[1]')
        for line_selector, time_selector in zip(horse_lines_selector, 
                sectional_time_selector):

            placing = line_selector.xpath('td[1]/div/text()').extract()[0].strip()

            horsenumber = line_selector.xpath('td[2]/div/text()').extract()[0].strip()

            horse_name_cell = line_selector.xpath('td[3]/div/a/text()').extract()[0]
            horse_name_regexp = '^(?P<name>[^\(]+)\((?P<code>[^\)]+)\)$'
            horse_name_dict = re.match(horse_name_regexp, horse_name_cell).groupdict()
            horsecode = horse_name_dict['code']

            timelist = [time.strip() for time in time_selector.xpath('td/text()').extract()]
            timelist_len = len(timelist)
            timelist.extend([None for i in xrange(6-timelist_len)])

            horse_path = line_selector.xpath('td[3]/div/a/@href').extract()[0]
            horse_url = 'http://www.{domain}/english/racing/{path}&Option=1#htop'.format(
                domain=self.domain, path=horse_path)

            marginsbehindleader = [s.strip('\t\n\r ') for s in line_selector.xpath(
                'td//table//td/text()').extract()]
            marginsbehindleader.extend([None]*(6 - len(marginsbehindleader)))

            finish_time = line_selector.xpath('td[10]/div/text()').extract()[0]

            positions = [s.strip('\t\n\r ') for s in line_selector.xpath(
                'td//table//td[1]/div/div/text()').extract()]
            positions.extend([None]*(6 - len(positions)))

            meta_dict = response.meta
            meta_dict.update({
                'horsenumber': horsenumber,
                'horsecode': horsecode,
                'placing': placing,
                'finish_time': finish_time,
                'positions': positions,
                'timelist': timelist,
                'horse_url': horse_url,
                'marginsbehindleader': marginsbehindleader,
            })
            print '+++++++++++++++++++++++++++++++++++++++++'
            print meta_dict

    def parse_horse(self, response):
        RaceSpider.count_unique_horse_request += 1
        log.msg('RaceSpider.count_unique_horse_request', level=log.INFO)
        log.msg(str(RaceSpider.count_unique_horse_request), level=log.INFO)
        
        #TODAY'S going? CD 

        totalstakes = response.xpath('//td[preceding-sibling::td[1]/font['
            'text() = "Total Stakes*"]]/font/text()').extract()[0]

        #DD - previousruns: Place, Date, Rating
        prev_places = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=2]//font/text()").extract()
        prev_dates = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=3]//font/text()").extract()
        # remove  u'\r\n\t\t'
        prev_dates = [ x for x in prev_dates if x != u'\r\n\t\t']

        prev_ratings = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=9]/text()").extract()

        prev_distances = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=5]/text()").extract()
        prev_rc_track_course  = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=4]/text()").extract()
        # pprint.pprint(prev_places)
        # pprint.pprint(prev_dates)
        #todays rc track course racecoursecode\s/\s #ST / "Turf" / "A+3 "    ST / "AWT" / "-" 
        # todaysrc_track_course = getrc_track_course(response.meta['racecourse'], response.meta['racesurface'])
        # pprint.pprint(todaysrc_track_course) 
        ##DD isMdn
        
        invalid_dates = [i for i, x in enumerate(prev_dates) if datetime.strptime(x, '%d/%m/%Y') >= datetime.strptime(response.meta['racedate'], '%Y%m%d')] #20150527
        valid_from_index = None
        win_indices = [i for i, x in enumerate(prev_places) if x == "01"]
        if len(invalid_dates) >0:
            valid_from_index = max(invalid_dates) 
            win_indices = win_indices[valid_from_index:]

        is_maiden = False

        if len(win_indices) ==0:
            is_maiden= True

        min_index = None
        last_won_at = None
        if len(win_indices) >0: 
            min_index = min(win_indices)
            last_won_at = prev_ratings[min_index]


        ##EarlyPacePoints need secs + lbw_post  
        ##what are qualifying races?



        ## utcracetime = local2utc(response.meta['racedate'],response.meta['localtime']),
        ##TODO internalhorseindex - need racecourse
        yield items.HorseItem(
            racedate=response.meta['racedate'],
            utcracetime = local2utc(getdateobject(response.meta['racedate']),response.meta['localtime']),
            racecourse=response.meta['racecourse'],
            raceclass=response.meta['raceclass'],
            racesurface=response.meta['racesurface'],
            racerating=response.meta['racerating'],
            racename=unicode.strip(response.meta['racename']),
            racenumber=try_int(response.meta['racenumber']),
            horsenumber=try_int(response.meta['horsenumber']),
            horsename=unicode.strip(response.meta['horsename']),
            horsecode=response.meta['horsecode'],
            jockeycode=response.meta['jockeycode'],
            trainercode=response.meta['trainercode'],
            owner=response.meta['owner'],
            totalstakes=cleanpm(unicode.strip(totalstakes)),
            todaysrating=response.meta['todaysrating'],
            gear=response.meta['gear'],
            lastwonat = last_won_at,
            isMaiden = is_maiden
        )

    def parse_tips(self, response):

        ##replace events by HKJC
        # event_ = response.xpath("//font/b/text()[contains(.,'Race')]").extract()[0]
        # event = unicode.replace(event_, u'\xa0', u'')
        # event_d = re.match(r'^(?P<racedate>\d\d-\d\d-\d\d\d\d)\s*Race\s(?P<racenumber>\d+)\s*-\s(?P<racetime>\d+:\d\d)', unicode.strip(event)).groupdict()
        
        # ##racetype
        # # racetype = response.xpath("//font/b/text()[contains(.,'Class')] | text()[contains(., 'Group')]").extract()[0]
        

        # event2 = unicode.strip(response.xpath("//font/b/text()[contains(.,'Sha Tin')] | text()[contains(., 'Happy Valley')]").extract()[0])
        # event2_d = re.match(r'^(?P<racecourse>(Sha Tin|Happy Valley))[^A-Z]*', event2).groupdict()
        ##racecourse##distance##surface


        tips = {}
        for tip_ in response.xpath('//table//font/select/option[contains('
                'text(), "--")]/text()').extract():
            tip = re.match(r'^(?P<val>[^-].+\d)[^\d]*--[^A-Z]*(?P<name>.+)\r\n',
                tip_).groupdict()
            tips.update({tip['name']: tip['val'].replace(u'\xa0', u'')})

        comments_url = 'http://racing.scmp.com/RaceCardPro/comment{}.asp'.format(
            response.meta['racenumber'])

        for horsename in response.xpath('//tr//tr//table[@bgcolor="#A70E13"]'
                '//tr[@bgcolor="white"]/td[4]//a/text()').extract():

            request = scrapy.Request(comments_url, callback=self.parse_comments)
            request.meta.update(response.meta)
            request.meta.update(tips=tips)
            request.meta.update(horsename=horsename)
            request.meta.update(racedate=self.racedate)
            request.meta.update(racecourse=self.racecoursecode)
            # request.meta.update(racecourse=event2_d['racecourse'])
            # request.meta.update(racetype=racetype)
            # request.meta.update(racedate=parse(event_d['racedate']))
            # request.meta.update(racenumber=event_d['racenumber'])
            # request.meta.update(localracetime=event_d['racetime'])
            yield request

    def parse_comments(self, response):

        comment_ = response.xpath('//td[font[contains(text(), "{}")]]/'
            'following-sibling::td/font/text()'.format(
            response.meta['horsename'])).extract()
        comment = comment_ and comment_[0] or u''
        ### make sure racenumber is 0 padded
        workouts_url = 'http://racing.scmp.com/Trackwork/Summary/Summary{}.asp'.format(
            response.meta['racenumber'])
        request = scrapy.Request(workouts_url, callback=self.parse_workouts)
        request.meta.update(response.meta)
        request.meta.update(comment=comment)

        return request

    def parse_workouts(self, response):

        tr = response.xpath('//tr[td[2]//a[text() = "{}"]]'.format(
            response.meta['horsename']))

        font = tr.xpath('td[8]/font')

        totaljump_ = font.xpath('font[1]/text()').extract()[0]
        totaljump = re.match(r'^Jump:[^\d]+(?P<num>\d+)$', totaljump_
            ).groupdict()['num']

        totalcanter_ = font.xpath('text()[2]').extract()[0][3:]
        totalcanter = re.match(r'^.*Canter: (?P<num>\d+)$', totalcanter_
            ).groupdict()['num']

        totalbarrier_ = font.xpath('font[2]/text()').extract()[0]
        totalbarrier = re.match(r'^Barrier: (?P<num>\d+)$', totalbarrier_
            ).groupdict()['num']

        totalswim_ = font.xpath('text()[3]').extract()[0][7:]
        totalswim_match = re.match(r'^.*Swim: (?P<num>\d+)$', totalswim_
            )
        totalswim = totalswim_match and totalswim_match.groupdict()['num']

        BTNumber_url = tr.xpath('td[4]//a/@href').extract()
        BTNumber = None
        if BTNumber_url:
            BTNumber_re = re.match(r'../../Trackwork/barrier/2015/(?P<num>\d+).asp',
                BTNumber_url[0])
            BTNumber = BTNumber_re and BTNumber_re.groupdict()['num']

        best_url = 'http://racing.scmp.com/statistic_chart/bestfinish{}.asp'
        request = scrapy.Request(best_url.format(response.meta['racenumber']),
            callback=self.parse_best)
        request.meta.update(response.meta)
        request.meta.update(racenumber=response.meta['racenumber'])
        request.meta.update(totaljump=totaljump)
        request.meta.update(totalcanter=totalcanter)
        request.meta.update(totalbarrier=totalbarrier)
        request.meta.update(totalswim=totalswim)
        request.meta.update(BTNumber=BTNumber)

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

        ##TOD raceindex

        return items.RaceItem(
            # standard_deviation = getbestfinishstats(besttimes)['standard-deviation'],
            # avgdistance= getbestfinishstats(besttimes)['avg'],
            racedate = response.meta['racedate'],
            racecoursecode = getrc(unicode(response.meta['racecourse'])),
            # racetype = response.meta['racetype'], 
            racenumber = try_int(response.meta['racenumber']),
            internalraceindex = getinternalraceindex(response.meta['racedate'], getrc(unicode(response.meta['racecourse'])), try_int(response.meta['racenumber'])),
            
            tips=response.meta['tips'],
            comment=cleanstring(response.meta['comment']),
            totaljump=try_int(response.meta['totaljump']),
            totalcanter=try_int(response.meta['totalcanter']),
            totalbarrier=try_int(response.meta['totalbarrier']),
            totalswim=try_int(response.meta['totalswim']),
            BTNumber=try_int(response.meta['BTNumber']),
            horsename=response.meta['horsename'],
        )
