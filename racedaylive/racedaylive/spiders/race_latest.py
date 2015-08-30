import re

import scrapy
from scrapy import log
from racedaylive import items
from datetime import datetime, date
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
        self.races_url = 'http://{domain}/racing/Info/Meeting/RaceCard'\
            '/English/Local/{racedate}/{coursecode}/1'.format(
                domain=self.hkjc_domain,
                racedate=racedate, 
                coursecode=coursecode,
        )
        self.after_login_url = 'http://racing.scmp.com/racecardpro/racecardpro.asp'
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
        return scrapy.Request(self.after_login_url, callback=self.parse_scmp_date)

    def parse_scmp_date(self, response):

        date_str = response.xpath('//b[contains(text(), "Race 1")]/text()').extract()[0]
        date_dict = re.match(r'^(?P<day>\d\d)-(?P<month>\d\d)-(?P<year>\d\d\d\d).*',
            date_str).groupdict()
        latest_race_date = datetime(int(date_dict['year']), int(date_dict['month']), 
            int(date_dict['day']))

        request = scrapy.Request(self.races_url, callback=self.parse_races)
        request.meta.update(response.meta)
        request.meta['latest_race_date'] = latest_race_date
        return request

    def parse_races(self, response):
        #HKJC racecard
        race_paths = response.xpath('//td[@nowrap="nowrap" and @width="24px"]'
            '/a/@href').extract()
        card_urls = ['http://{domain}{path}'.format(
                domain=self.hkjc_domain,
                path=path,
            ) for path in race_paths
        ] + [response.url]
        result_urls = [_url.replace('RaceCard', 'Results') for _url in card_urls]
        for card_url, result_url in zip(card_urls, result_urls):
            if int(card_url.split('/')[-1]) > 9:
                racenumber = '{}'.format(card_url.split('/')[-1])
            else:
                racenumber = '0{}'.format(card_url.split('/')[-1])
            request = scrapy.Request(result_url, callback=self.parse_results)
            request.meta.update(response.meta)
            request.meta['racenumber'] = racenumber
            request.meta['card_url'] = card_url
            yield request

    def parse_results(self, response):
        sectional_time_url = response.xpath('//div[@class="rowDiv15"]/div['
            '@class="rowDivRight"]/a/@href').extract()
        print sectional_time_url[0]
        try:
            _sectional_time_url = sectional_time_url[0]
        except IndexError:
            assert False
        request = scrapy.Request(_sectional_time_url, callback=
            self.parse_sectional_time)
        #self.parse_race
        # request = scrapy.Request(response.meta['card_url'], callback=
            # self.parse_race)
        request.meta.update(response.meta)
        yield request

    def parse_sectional_time(self, response):

        horse_lines_selector = response.xpath('//table[@class="bigborder"]//'
            'table//a/../../..')
        sectional_time_selector = response.xpath('//table[@class='
            '"bigborder"]//table//a/../../../following-sibling::tr[1]')
        sectional_time_data = {}
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

            sectional_time_data.update({(horsecode, response.meta['racenumber']):
                {
                    'horsecode': horsecode,
                    'horsenumber': horsenumber,
                    'placing': placing,
                    'finish_time': finish_time,
                    'marginsbehindleader': marginsbehindleader,
                    'positions': positions,
                    'timelist': timelist,
                    'horse_url': horse_url,
                }
            })

        request = scrapy.Request(response.meta['card_url'], callback=self.parse_race)
        request.meta.update(response.meta)
        request.meta['sectional_time_data'] = sectional_time_data
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
            # print "surface distance\n", 
            # print surface_distance

            # racedistance': u'Turf',  'racesurface': u'1800M',
            ## this line has: Turf, "B+2" Course, 1800M, Good To Firm
            #other lines have Turf, "C" Course, 1000M, Good To Firm
            # Turf, "C" Course, 1800M, Good
            # All Weather Track, 1200M, Fast len 3 

            surface = unicode.strip(unicode.split(surface_distance, u',')[0])
            trackvariant = unicode.strip(unicode.split(surface_distance, u',')[1])
            if surface != u'AWT':
                surface = trackvariant
            # get_racecoursecode
            distance = unicode.strip(unicode.split(surface_distance, u',')[2].replace('M',''))
            #only if not current race!!
            going = unicode.strip(unicode.split(surface_distance, u',')[3])

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
        ##season_stakes and priority
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

            jockeyname_ = tr.xpath('td[7]/a/text()').extract()[0]
            jockeycode_ = tr.xpath('td[7]/a/@href').extract()[0]
            jockeycode = re.match(r"^[^\?]+\?jockeycode=(?P<code>\w+)'.*",
                jockeycode_).groupdict()['code']
            
            ##TRAINER CODE
            trainername_ = tr.xpath('td[10]/a/text()').extract()[0]
            trainercode_ = tr.xpath('td[10]/a/@href').extract()[0]
            trainercode = re.match(r"^[^\?]+\?trainercode=(?P<code>\w+)'.*",
                trainercode_).groupdict()['code']

            todaysrating_ = tr.xpath('td[11]/text()').extract()[0]
            owner_ = tr.xpath('td[22]/text()').extract()[0]
            gear_ = tr.xpath('td[21]/text()').extract()[0]

            seasonstakes_ = tr.xpath('td[18]/text()').extract()[0]
            priority_ = tr.xpath('td[20]/text()').extract()[0]
            draw_ = tr.xpath('td[8]/text()').extract()[0]


            request = scrapy.Request('http://www.hkjc.com/english/racing/horse.'
                'asp?horseno={}'.format(horsecode), callback=self.parse_horse)
            sec_time_data = response.meta['sectional_time_data'][(horsecode, response.meta['racenumber'])]
            request.meta.update(response.meta)
            request.meta.update(
                localtime=localtime,
                racename=racename,
                racecoursecode=get_racecoursecode(racecourse),
                racesurface=surface,
                racegoing= going,
                racedistance=get_distance(distance),
                raceclass=raceclass,
                racerating= try_int(racerating),
                racedate = getdateobject(self.racedate),
                horsenumber=try_int(horsenumber),
                horsename=horsename,
                horsecode=horsecode,
                jockeycode=jockeycode,
                jockeyname=re.sub(r'\([^)]*\)', '', jockeyname_),
                trainercode=trainercode,
                trainername = trainername_,
                todaysrating=try_int(todaysrating_),
                owner=owner_,
                gear=gear_,
                draw=try_int(draw_),
                placing=get_placing(sec_time_data['placing']),
                finish_time=get_sec(sec_time_data['finish_time']),
                marginsbehindleader=map(horselengthprocessor, sec_time_data['marginsbehindleader']),
                positions=map(try_int, sec_time_data['positions']),
                timelist=sec_time_data['timelist'], #test get_sec
                seasonstakes = try_int(seasonstakes_),
                priority = get_priority(priority_)
            )
            yield request

        if response.meta['latest_race_date'] <= datetime.strptime(self.racedate, 
                '%Y%m%d'):
            tips_url = 'http://racing.scmp.com/racecardpro/racecardpro{}.asp'
            request = scrapy.Request(tips_url.format(response.meta['racenumber']),
                callback=self.parse_tips)
            request.meta.update(response.meta)
            yield request

    ##RESULTS IS TAKING CARE OF THIS STUFF OK
    def parse_horse(self, response):
        RaceSpider.count_unique_horse_request += 1
        log.msg('RaceSpider.count_unique_horse_request', level=log.INFO)
        log.msg(str(RaceSpider.count_unique_horse_request), level=log.INFO)
        
        ## GET SEASON STAKES INSTEAD
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
        # datetime.strptime(response.meta['racedate'], '%Y%m%d')
        invalid_dates = [i for i, x in enumerate(prev_dates) if datetime.strptime(x, '%d/%m/%Y').date() >= response.meta["racedate"] ] #20150527
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
            utcracetime = local2utc(response.meta['racedate'],response.meta['localtime']),
            racecoursecode=response.meta['racecoursecode'],
            raceclass=try_int(response.meta['raceclass']),
            racedistance=response.meta['racedistance'],
            racegoing=response.meta['racegoing'],
            racesurface=response.meta['racesurface'],
            racerating=response.meta['racerating'],
            racename=unicode.strip(response.meta['racename']),
            racenumber=try_int(response.meta['racenumber']),
            horsenumber=try_int(response.meta['horsenumber']),
            horsename=unicode.strip(response.meta['horsename']),
            horsecode=response.meta['horsecode'],
            jockeycode=response.meta['jockeycode'],
            jockeyname=response.meta['jockeyname'],
            trainercode=response.meta['trainercode'],
            trainername=response.meta['trainername'],
            ownername=response.meta['owner'],
            # totalstakes=cleanpm(unicode.strip(totalstakes)),
            todaysrating=response.meta['todaysrating'],
            gear=unicode.strip(response.meta['gear']),
            lastwonat = get_rating(last_won_at),
            isMaiden = is_maiden,
            placing=try_int(response.meta['placing']),
            finish_time=response.meta['finish_time'],
            marginsbehindleader=response.meta['marginsbehindleader'],
            positions=response.meta['positions'],
            timelist=response.meta['timelist'],
            priority=removeunicode(response.meta['priority']),
            seasonstakes=response.meta['seasonstakes']
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

        #per RACE return COLNAME tipster split
        '''
             'racenumber': 11,
     'tips': {u'Alan Aitken': u'10  4  9  12',
              u'Andrew Hawkins': u'10+ 4  6  9',
              u'Brett Davis': u'4  3  10 9',
              u'Michael Cox': u'4  3  9  8',
              u'Most Favoured': u'4  10 3  9',
              u'Phillip Woo': u'4  1  10 6',
              u'Racing Post Online': u'4  10 9  1',
              u'Shannon (vincent Wong)': u'4* 3  2  1'},
        * NAP * SecondNap

            t_system_id= db.Column(db.Integer, ForeignKey('t_system.id'))
    t_raceday_id = db.Column(db.Integer, ForeignKey('t_raceday.id'))
    t_race_id= db.Column(db.Integer, ForeignKey('t_race.id'))
    horsenumber = db.Column(db.Integer)
    nap1 =db.Column(db.Boolean)

        '''
        ordinals = {'1':'first', '2':'second', '3': 'third', '4':'fourth'}

        naps = {}
        for k,v in tips.items():
            if k == u"Shannon (vincent Wong)":
                newk = u"Shannon"
            else:
                newk = k
            #take care of naps, nap2s and find
            if (u'*' in v) or (u'+' in v):
                first= v.split(" ")[0]
                #first will be nap
                if u'*' in first:
                    nap1 = True
                elif u'_' in first:
                    nap1 = False
                else:
                    nap1 = None
                if nap1 is not None:
                    value_dict = {}
                    value_dict.update({'t_system_name':k, 'horsenumber': first, 'nap1':nap1, })
                    naps[newk] = value_dict
        
        new_tips = {}
        for k,v in tips.items():
            if k == u"Shannon (vincent Wong)":
                newk = u"Shannon"
            else:
                newk = k
            tips_value_dict = {}
            vals = v.split(u' ')
            vals = [v for v in vals if v != u'']
            # print vals 
            #remove naps+-
            for i,_v in enumerate(vals):
                newv = try_int(_v.replace(u'*', u'').replace(u'+', ''))
                tips_value_dict.update({ordinals[str(i+1)]:newv})
            new_tips[k] = tips_value_dict
            # pprint.pprint(new_tips)
            # log.msg(new_tips, level=log.INFO)

        ##classify positive or negative? DB
        comments_url = 'http://racing.scmp.com/RaceCardPro/comment{}.asp'.format(
            response.meta['racenumber'])

        for horsename in response.xpath('//tr//tr//table[@bgcolor="#A70E13"]'
                '//tr[@bgcolor="white"]/td[4]//a/text()').extract():

            request = scrapy.Request(comments_url, callback=self.parse_comments)
            request.meta.update(response.meta)
            request.meta.update(tips=new_tips)
            request.meta.update(naps=naps)
            request.meta.update(horsename=horsename)
            request.meta.update(racedate=getdateobject(self.racedate))
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

        ##times more useful
        totaljump_ = font.xpath('font[1]/text()').extract()[0]
        totaljump = re.match(r'^Jump:[^\d]+(?P<num>\d+)$', totaljump_).groupdict()['num']
        # '//tr[ td[2]//a[text()="WINNING LEADER"]]/td[position()>2 and position() < 8]/font/font[@color="BROWN"]/text()'
        jump_times = None
        if totaljump >0:
            jump_times_ = tr.xpath('/td[position()>2 and position() < 8]/font/font[@color="BROWN"]/text()').extract()
            try:
                jump_times = jump_times_[0]
            except ValueError:
                jump_times = None

        totalcanter_ = font.xpath('text()[2]').extract()[0][3:]
        totalcanter = re.match(r'^.*Canter: (?P<num>\d+)$', totalcanter_).groupdict()['num']

        totalbarrier_ = font.xpath('font[2]/text()').extract()[0]
        totalbarrier = re.match(r'^Barrier: (?P<num>\d+)$', totalbarrier_).groupdict()['num']
        barrier_times = None
        if totalbarrier >0:
            barrier_times_ = tr.xpath('/td[position()>2 and position() < 8]/font/a/font[@color="GREEN"]/text()').extract()
            try:
                barrier_times = barrier_times[0]
            except ValueError:
                barrier_times = None

        totalswim_ = font.xpath('text()[3]').extract()[0][7:]
        totalswim_match = re.match(r'^.*Swim: (?P<num>\d+)$', totalswim_
            )
        totalswim = totalswim_match and totalswim_match.groupdict()['num']

        # BTNumber_url = tr.xpath('td[4]//a/@href').extract()
        # BTNumber = None
        # if BTNumber_url:
        #     BTNumber_re = re.match(r'../../Trackwork/barrier/2015/(?P<num>\d+).asp',
        #         BTNumber_url[0])
        #     BTNumber = BTNumber_re and BTNumber_re.groupdict()['num']

        best_url = 'http://racing.scmp.com/statistic_chart/bestfinish{}.asp'
        request = scrapy.Request(best_url.format(response.meta['racenumber']),
            callback=self.parse_best)
        request.meta.update(response.meta)
        request.meta.update(racenumber=response.meta['racenumber'])
        request.meta.update(totaljump=totaljump)
        request.meta.update(totalcanter=totalcanter)
        request.meta.update(totalbarrier=totalbarrier)
        request.meta.update(barriertimes=barrier_times)
        request.meta.update(jumptimes=jump_times)
        request.meta.update(totalswim=totalswim)
        # request.meta.update(BTNumber=BTNumber)

        yield request

    def parse_best(self, response):
        # log bestfinishes
        scrapy.log.msg(response.url, level=scrapy.log.INFO)
        ##DO WE NEED THIS?
        tr_selector = '//tr[td/font/b[text()="{horsename}"]] | //tr[td/font/b'\
            '[text()="{horsename}"]]/following-sibling::tr'.format(
            horsename=response.meta['horsename'])
        # besttimes = []
        # for i, tr in enumerate(response.xpath(tr_selector)):
        #     if i > 0 and (tr.xpath('td/font/b/text()').extract() or
        #             not tr.xpath('td[1][not(font) and not(@colspan)]').extract()):
        #         break
        #     besttimes_ = tr.xpath('td[3]/font/text()').extract()[0]
        #     besttimes.append(re.match(r'^.*\((?P<time>.+)\)$', besttimes_
        #         ).groupdict()['time'])
        # pprint.pprint(besttimes)
        ##TOD raceindex
        ### ONLY CALL IF self.racedate NOT IN PAST 
        return items.RaceItem(
            # standard_deviation = getbestfinishstats(besttimes)['standard-deviation'],
            # avgdistance= getbestfinishstats(besttimes)['avg'],
            racedate = response.meta['racedate'],
            racecoursecode = getrc(unicode(response.meta['racecourse'])),
            # racetype = response.meta['racetype'], 
            racenumber = try_int(response.meta['racenumber']),
            # internalraceindex = getinternalraceindex(response.meta['racedate'], getrc(unicode(response.meta['racecourse'])), try_int(response.meta['racenumber'])),
            
            tips=response.meta['tips'], #name - > t_system_id, first, second, third fourth
            naps=response.meta['naps'],
            scmp_runner_comment=cleanstring(response.meta['comment']),
            totaljump=try_int(response.meta['totaljump']),
            totalcanter=try_int(response.meta['totalcanter']),
            totalbarrier=try_int(response.meta['totalbarrier']),
            barriertimes=try_int(response.meta['barriertimes']),
            jumptimes=try_int(response.meta['jumptimes']),
            totalswim=try_int(response.meta['totalswim']),
            # BTNumber=try_int(response.meta['BTNumber']),
            horsename=response.meta['horsename'],
        )
