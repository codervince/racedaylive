#utiltiies
from fractions import Fraction
from datetime import date, time, datetime, timedelta
from dateutil import tz
import re
import operator
import math

##SCMP

# def get_scmp_lbw(lbw):
#     '''

#     '''
#     if lbw is None or lbw == u'-':
#         return None




# def parse_mixed_fraction(s):
#     if s.isdigit():
#         return float(s)
#     elif len(s) == 1:
#         return unicodedata.numeric(s[-1])
#     else:
#         return float(s[:-1]) + unicodedata.numeric(s[-1])

# def sanitizelbw(lbw):
#     if "L" not in lbw:
#         '''suspect lbw'''
#         return None
#     lbw = lbw.replace("L", "")
#     return parse_mixed_fraction(lbw)

### RAILTYPE INFO

def cleanstring(s):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, u' ',s).sub(u'-', u'')

## for comparing with historical data
## ST / "AWT" / "-"
def getrc_track_course(racecourse, surface):
    rc_code = getrc(racecourse)
    surface = unicode.strip(surface)
    surface_course_codes = {
    u'"A" Course': ("Turf", "A"),
    u'"A+3" Course': ("Turf", "A+3"),   
    u'"B" Course': ("Turf", "B"),
    u'"B+2" Course': ("Turf", "B+2"),
    u'"C" Course': ("Turf", "C"), 
    u'"C+3" Course': ("Turf", "C+3"),
    u'All Weather Track': ("AWT", "-")
    }
    spacer = u' / '
    newsurface, newcourse = surface_course_codes[surface]
    return rc_code+spacer+newsurface+spacer+newcourse
    # add u' / '

def getinternalraceindex(racedate, racecoursecode, racenumber):
    if type(racedate) != type(datetime(2015, 5, 31, 0, 0)):
        return None
    return racedate.strftime('%Y%m%d') + '_' + str(racecoursecode) + '_' + str(racenumber)


def average(s): return sum(s) * 1.0 / len(s)


def getbestfinishstats(besttimes):
    #make sure best finishes is a list
    ##init dictionary keys
    stats = {}
    stats['standard-deviation'] = None
    stats['variance'] = None
    stats['avg'] = None
    if type(besttimes) != type([]):
        return None
    if len(besttimes) == 0:
        return None
    thesum = reduce(operator.add, map(float,besttimes))
    stats['avg'] = round(thesum*1.0/len(besttimes),2)
    # stats['maxdistance'] = max(map(float, besttimes))
    stats['variance'] = map(lambda x: (float(x) - stats['avg'])**2, besttimes)
    stats['standard-deviation'] = round(math.sqrt(sum(stats['variance'])*1.0/len(stats['variance'])),2)
    return stats

def cleanpm(prizemoney):
    return int(''.join(re.findall("[-+]?\d+[\.]?\d*", prizemoney)))/1000.0


'''
expect format datetime object + time 1:45 12 hour clock
convert to UTC time object -8
need to explicity state timezone in datetime object?
'''
def local2utc(todaysdate, basictime):
    h = int(basictime.split(':')[0])
    h = h+12 if h < 12 else h
    m = int(basictime.split(':')[1])
    hk_t = time(h,m)
    hk_d = datetime.combine(todaysdate, hk_t) ##todaysdate is a date object
    return hk_d - timedelta(hours=8) 

def getrc(racecourse):
    racecourse = unicode.strip(racecourse)
    if racecourse == 'Sha Tin' or racecourse == 'ST':
        return u'ST'
    elif racecourse =='Happy Valley' or racecourse== 'HV':
        return 'HV'
    else:
        return None

RAILTYPES = {
    
u'ST': {
    u'A': [430, 30.5],
    u'A+2': [430, 28.5],
    u'A+3': [430, 27.5],
    u'B': [430,26],
    u'B+2': [430, 24],
    u'C': [430, 21.3],
    u'C+3': [430, 18.3],
    u'AWT': [365, 22.8]
},

u'HV': {
    u'A': [312, 30.5],
    u'A+2': [310, 8.5],
    u'B': [338, 26.5],
    u'B+2': [338, 24.5],
    u'B+3': [338, 23.5],
    u'C': [334, 22.5],
    u'C+3': [335, 19.5]
}

}

def split_by(tosplit, separator):
    rtn = []
    if tosplit is not None:
        for i in tosplit:
            rtn.append(unicode.split(i, u'\xa0'))
        return rtn

def gethomestraight(racecourse, railtype):
    if racecourse == u'Sha Tin':
        racecourse = u'ST'
    if racecourse == u'Happy Valley':
        racecourse = u'HV'
    if railtype == u"All Weather Track":
        railtype = u"AWT"
    return RAILTYPES[racecourse][railtype][0]

def gettrackwidth(racecourse, railtype):
    if racecourse == u'Sha Tin':
        racecourse = u'ST'
    if racecourse == u'Happy Valley':
        racecourse = u'HV'
    if railtype == u"All Weather Track":
        railtype = u"AWT"
    return RAILTYPES[racecourse][railtype][1]



def to_eventinfo(racecourse, surface, going, railtype):
    rtn = u''
    if racecourse in [u'Sha Tin', u'ST']:
        rtn += u'ST '
        if surface == 'AWT':
            rtn += u'aw '
    else:
        rtn += u'HV tf '
    #going
    rtn += u'-' + raitype + u' '
    return rtn


def from_eventinfo(eventinfo):
    '''
    splits e.g. ST tf g/f -C 
    into list of 
    racecourse surface going railtype
    '''
    rtn = {}
    rtn['surface'] = 'Turf'
    rtn['railtype'] = None
    goings = [u'g', u'g/f', u'f', u'w/s']
    if eventinfo is None:
        return []
    rc = re.findall("^(ST|HV)\s.*", eventinfo)
    if rc:
        rtn['racecourse'] = rc[0]
    tf_aw = re.findall(".*\s(tf|aw)\s.*", eventinfo)
    if tf_aw == 'aw':
        rtn['surface']= u'AWT'
    rt = re.findall(".*-(.*)$", eventinfo)
    if rt:
        if unicode.strip(rt[0]) == u'All Weather Track':
            rtn['railtype'] = None
        else: 
            rtn['railtype'] = unicode.strip(rt[0])
    return rtn
    ##return racecourse, surface, going, railtype
    
    

    


def get_scmp_ftime(ftime, myformat=None):
    '''
    strftime('%s')
    expected format:1:40.7 m:ss.n
    if format =='s' return no of seconds else datetiem obj
    '''
    if ftime is None:
        return None
    dt1_obj = datetime.strptime(ftime, "%M:%S.%f")
    if dt1_obj is not None:
        totalsecs = (dt1_obj.minute*60.0) + dt1_obj.second + (dt1_obj.microsecond/1000.0)
    if myformat == u's':
        return totalsecs
    else:
        return dt1_obj

def processscmpodds(odds):
    if odds is None:
        return None
    else:
        return try_float(odds)

def isFavorite(oddscolor):
    if oddscolor is None:
        return 0
    elif oddscolor == '#FF0000':
        return bool(1)
    else:
        return bool(0)




##########

def processscmpplace(place):
    place99 = ['DISQ', 'DNF', 'FE', 'PU', 'TNP', 'UR', 'VOID', 'WD', 'WR', 'WV', 'WV-A', 'WX', 'WX-A']
    if place is None:
        return None
    elif place in place99:
        return 99
# r_dh = r'.*[0-9].*DH$'
    else:
        return try_int(place)



def timeprocessor(value):
    #tries for each possible format
    for format in ("%S.%f", "%M.%S.%f", "%S"):
        try:
            return datetime.strptime(value, format).time()
        except:
            pass
    return None

def horselengthprocessor(value):
    #covers '' and '-'

    if '---' in value:
        return None
    elif value == '-':
        #winner
        return 0.0
    elif "-" in value and len(value) > 1:
        return float(Fraction(value.split('-')[0]) + Fraction(value.split('-')[1]))
    elif value == 'N':
        return 0.3
    elif value == 'SH':
        return 0.1
    elif value == 'HD':
        return 0.2
    elif value == 'SN':
        return 0.25  
    #nose?           
    elif value == 'NOSE':
        return 0.05
    elif '/' in value:
         return float(Fraction(value))        
    elif value.isdigit():
        return try_float(value)
    else:
        return None

def try_float(value):
    try:
        return float(value)
    except:
        return 0.0

def try_int(value):
    try:
        return int(value)
    except:
        return 0

def getHorseReport(ir, h):
    lir = ir.split('.')
    return [e.replace(".\\n", "...") for e in lir if h in e]


#done in default output processor?
def noentryprocessor(value):
    return None if value == '' else value


'''
remove \r\n\t\t\t\t\t
'''
def cleanstring(value):
    return unicode.strip(value)

def getdateobject(datestring):
    return datetime.strptime(datestring, '%Y%m%d').date()