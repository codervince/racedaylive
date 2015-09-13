from sqlalchemy import Column, BigInteger, String, Integer, UniqueConstraint, Date,\
    TIMESTAMP, Float, ForeignKey, Boolean
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, scoped_session, create_session,\
    relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
import settings

def get_engine():
    return create_engine(URL(**settings.DATABASE), pool_size=0)
    # return DBDefer(URL(**settings.DATABASE))

def create_schema(engine):
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Raceday = Base.classes.raceday
    Race = Base.classes.race
    Runner = Base.classes.runner
    Owner = Base.classes.owner
    Trainer = Base.classes.trainer
    Jockey = Base.classes.jockey
    Horse = Base.classes.horse
    # ModelBase.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    # self.Session = sessionmaker(bind=engine)
# self.cache = defaultdict(lambda: defaultdict(lambda: None)) #necessary?
    session = create_session(bind=engine)
        
    testlist = session.query(Raceday).all()     
    for test in testlist:  
        print test.racedate

# def db_connect():
#     return create_engine(URL(**settings.DATABASE))




# class User(db.Model):
#     __tablename__ = "user"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     email = db.Column(db.String(120))
#     password = db.Column(db.String(120))
#     name = db.Column(db.String(60))
#     animal = db.Column(db.String(60))
#     datesignedup = db.Column(db.TIMESTAMP())
    
#     systems = relationship("t_system",
#         backref=db.backref('users', lazy='dynamic')) ## t_SystemPerformance.t_systems.all() QUERY

#     __table_args__ = (UniqueConstraint('email'),)

#     def __init__(self, email, password, name, datesignedup, animal):
#         self.email = email
#         self.password = password
#         self.name = name
#         self.datsignedup = datesignedup
#         self.animal = animal

# # class User(db.Model):
# #     __tablename__ = "User"
# #     ID = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
# #     Email = db.Column(db.String(120))
# #     Password = db.Column(db.String(120))
# #     Name = db.Column(db.String(60))
# #     Animal = db.Column(db.String(60))
# #     DateSignedUp = db.Column(db.TIMESTAMP())
    
# #     systems = relationship("t_system",
# #         backref=db.backref('users', lazy='dynamic')) ## t_SystemPerformance.t_systems.all() QUERY

# #     __table_args__ = (UniqueConstraint('Name', 'Animal'),)

# #     def __init__(self, Email, Password, Name, DateSignedUp, Animal):
# #         self.Email = Email
# #         self.Password = Password
# #         self.Name = Name
# #         self.DateSignedUp = DateSignedUp
# #         self.Animal = Animal

Base = declarative_base()

##RACEDAY TABLES
class Owner(Base):
    __tablename__ = "owner"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
    ownername = Column("ownername", String(255), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('ownername'),)
#     def __init__(self, ownername):
#         self.name= ownername

class Horse(Base):
    __tablename__ = "horse"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
    horsename = Column("horsename", String(255), nullable=False)
    horsecode = Column("horsecode", String(6), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('horsecode'),)
#     def __init__(self, horsename, horsecode):
#         self.horsename= horsename
#         self.horsecode = horsecode

class Trainer(Base):
    __tablename__ = "trainer"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
    trainername = Column("trainername", String(255), nullable=False)
    trainercode = Column("trainercode", String(6), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('trainercode'),)
#     def __init__(self, trainername, trainercode):
#         self.name= trainername
#         self.code = trainercode

class Jockey(Base):
    __tablename__ = "jockey"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
    jockeyname = Column("jockeyname", String(255), nullable=False)
    jockeycode = Column("jockeycode", String(6), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('jockeycode'),)
#     def __init__(self, jockeyname, jockeycode):
#         self.name= jockeyname
#         self.code = jockeycode


class Raceday(Base):
    __tablename__ = "raceday"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
    racedate = Column(Date, nullable=False)
    racecoursecode = Column(String(2))
    runners_list = Column(postgresql.ARRAY(String(5))) #skips race

    __table_args__ = (UniqueConstraint('racedate', 'racecoursecode'),)
#     def __init__(self, racedate, racecoursecode, runners_list):
#         self.racedate= racedate
#         self.racecoursecode = racecoursecode
#         self.runners_list = runners_list

class Race(Base):
    __tablename__ = "race"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
    racenumber = Column(Integer)
    racename = Column(String(150))
    raceclass = Column(String(50))
    racerating = Column(String(50))
    racegoing = Column(String(10)) #GF GY Y 
    racesurface = Column(String(15)) #AWT or B+3
    racedistance = Column(Integer) # 1000
    utcracetime = Column(TIMESTAMP()) #exact jump time updatable
    marketorder = Column(String(15))
    result = Column(String(15))
    winodds = Column(Float)
    favpos = Column(Integer)
    favodds = Column(Float)
    norunners = Column(Integer)
    f4 = Column(postgresql.ARRAY(Float))
    tierce= Column(postgresql.ARRAY(Float))
    qtt = Column(postgresql.ARRAY(Float))
    dt = Column(postgresql.ARRAY(Float))
    tt = Column(postgresql.ARRAY(Float))
    ttc = Column(postgresql.ARRAY(Float))
    sixup = Column(postgresql.ARRAY(Float))
    sixupc = Column(postgresql.ARRAY(Float))
    raceday_id = Column(Integer, ForeignKey('raceday.id'))

    raceday = relationship("Raceday", 
        backref=backref('races', lazy='dynamic'))
    __table_args__ = (UniqueConstraint('raceday_id', 'racenumber'),)
    
#     def __init__(self, racedate, racecoursecode, racenumber, racename, raceclass, racerating, racegoing,racesurface, racedistance, utcracetime,
#         marketorder, result, winodds, favpos, favodds, norunners, f4, tierce, qtt, dt, tt, ttc, sixup, sixupc
#         ):
#         self.racedate = racedate
#         self.racecoursecode = racecoursecode
#         self.racenumber = racenumber
#         self.racename = racename
#         self.raceclass = raceclass
#         self.racerating = racerating
#         self.racegoing = racegoing
#         self.racesurface = racesurface
#         self.racedistance = racedistance
#         self.utcracetime = utcracetime
#         self.marketorder = marketorder
#         self.result= result
#         self.winodds = winodds
#         self.favpos = favpos
#         self.favodds = favodds
#         self.norunners = norunners
#         self.f4 = f4
#         self.tierce = tierce
#         self.qtt = qtt
#         self.dt = dt
#         self.tt  = tt
#         self.ttc = ttc
#         self.sixup = sixup
#         self.sixupc = sixupc
  
  ##results go in r_runner same index
class Runner(Base):
    __tablename__ = "runner"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
    horsenumber = Column(Integer)
    todaysrating = Column(Integer)
    lastwonat= Column(Integer)
    isMaiden = Column(Boolean)
    seasonstakes =Column(Float)
    draw = Column(Integer)
    isScratched = Column(Boolean)
    priority = Column(String(100))
    gear = Column(String(20))
    placing= Column(Integer)
    finish_time = Column(Float) #seconds
    marginsbehindleader = Column(postgresql.ARRAY(Float)) #floats
    positions = Column(postgresql.ARRAY(Integer)) #ints
    timelist= Column(postgresql.ARRAY(Float))
    scmp_runner_comment = Column(String(256))
    barriertimes = Column(postgresql.ARRAY(String(100)))
    jumptimes = Column(postgresql.ARRAY(String(100)))
    totalbarrier = Column(postgresql.ARRAY(Integer)) 
    totalcanter =Column(postgresql.ARRAY(Integer)) 
    totaljump = Column(postgresql.ARRAY(Integer)) 
    totalswim = Column(postgresql.ARRAY(Integer)) 
    owner_id = Column(Integer, ForeignKey('owner.id'))
    owner = relationship("Owner", 
        backref=backref('runners', lazy='dynamic'))

    jockey_id = Column(Integer, ForeignKey('jockey.id'))
    jockey = relationship("Jockey", 
        backref=backref('runners', lazy='dynamic'))

    trainer_id = Column(Integer, ForeignKey('trainer.id'))
    trainer = relationship("Trainer", 
        backref=backref('runners', lazy='dynamic'))

    horse_id = Column(Integer, ForeignKey('horse.id'))
    horse = relationship("Horse", 
        backref=backref('runners', lazy='dynamic'))

    race_id = Column(Integer, ForeignKey('race.id'))
    race = relationship("Race", 
        backref=backref('runners', lazy='dynamic'))

    __table_args__ = (UniqueConstraint('race_id', 'horse_id'),)

#     def __init__(self, race_id, horsenumber, horse_id, jockey_id, trainer_id, owner_id,
#         todaysrating, lastwonat, isMaiden, seasonstakes, draw, priority, gear,placing, finish_time,
#         marginsbehindleader, positions, timelist,scmp_runner_comment, barriertimes, 
#         jumptimes,totalbarrier, totalcanter, totaljump, totalswim, isScratched=False,):
#         self.race_id = race_id
#         self.horsenumber = horsenumber
#         self.horse_id = horse_id
#         self.trainer_id = trainer_id
#         self.jockey_id = jockey_id
#         self.owner_id = owner_id
#     
#         self.todaysrating = todaysrating
#         self.lastwonat= lastwonat
#         self.isMaiden = isMaiden
#         self.seasonstakes = seasonstakes
#         self.draw= draw
#         self.isScratched = isScratched
#         self.priority = priority
#         self.gear = gear
#         self.placing = placing
#         self.finish_time = finish_time
#         self.marginsbehindleader = marginsbehindleader
#         self.positions = positions
#         self.timelist = timelist
#         self.scmp_runner_comment = scmp_runner_comment
#         self.barriertimes = barriertimes
#         self.jumptimes = jumptimes
#         self.totalbarrier = totalbarrier
#         self.totalcanter = totalcanter
#         self.totaljump = totaljump
#         self.totalswim =totalswim 

# ### tipster
# class t_System(db.Model):
#     __tablename__ = "t_system"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     name = db.Column(db.String(60))
#     animal = db.Column(db.String(60))
#     datestarted = db.Column(db.Date)
#     datestopped = db.Column(db.Date)

#     __table_args__ = (UniqueConstraint('name', 'animal'),)

#     def __init__(self, name, animal, datestarted, datestopped):
#         self.name = name
#         self.animal = animal
#         self.datestarted = datestarted
#         self.datestopped = datestopped

# ##MANY MANY SETUP
# user_systems = db.Table('user_systems',
#     db.Column('user.id', db.Integer, ForeignKey('user.id')),
#     db.Column('t_system.id', db.Integer, ForeignKey('t_system.id')),
#     db.Column('created', db.TIMESTAMP),
#     db.Column('ended', db.TIMESTAMP)
#     )


# class t_Naps(db.Model):
#     __tablename__ = "t_naps"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False)
#     horsenumber = db.Column(db.Integer)
#     isnap1 =db.Column(db.Boolean)

#     t_system_id= db.Column(db.Integer, ForeignKey('t_system.id'))
#     raceday_id = db.Column(db.Integer, ForeignKey('raceday.id'))
#     race_id= db.Column(db.Integer, ForeignKey('race.id'))

#     def __init__(self, t_system_id, raceday_id, race_id, horsenumber, isnap1):
#         self.t_system_id = t_system_id
#         self.t_raceday_id = raceday_id
#         self.t_race_id = race_id
#         self.horsenumber = horsenumber


# #reflect
# class t_SystemRecords(db.Model):
#     __tablename__ = "t_systemrecords"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) # Unique ID
    
#     first = db.Column(db.Integer)
#     second = db.Column(db.Integer)
#     third = db.Column(db.Integer)
#     fourth = db.Column(db.Integer)
#     updated = db.Column(db.TIMESTAMP)
#     updated_date = db.Column(db.Date)

#     race_id = db.Column(db.Integer, ForeignKey('race.id'))
#     race = relationship("race",
#         backref=db.backref('t_systemrecords', lazy='dynamic')) ## t_SystemPerformance.t_systems.all() QUERY
    
#     t_system_id= db.Column(db.Integer, ForeignKey('t_system.id'))
#     t_system = relationship("t_system",
#         backref=db.backref('t_systemrecords', lazy='dynamic')) ## t_SystemPerformance.t_systems.all() QUERY

#     __table_args__ = (UniqueConstraint('race_id', 't_system_id'),)

#     def __init__(self,t_race_id, t_system_id, first, second, third, fourth, updated=datetime.utcnow()):
#         self.t_race_id= t_race_id
#         self.t_system_id=t_system_id
#         self.first = first
#         self.second = second
#         self.third = third
#         self.fourth = fourth
#         self.updated = updated
#         self.updated_date = updated.date()


# '''
# Contains aggregate data for tipsters based on the updated/_date.
# Thus can be updated at any time pre post race 
# select latest always
# '''
# class t_SystemPerformance(db.Model):
#     __tablename__ = "t_systemperformance"
#     id = db.Column(db.Integer, primary_key=True)
    
#     tipsterscore = db.Column(db.Float) 
#     winners = db.Column(db.Integer)
#     seconds = db.Column(db.Integer)
#     thirds = db.Column(db.Integer)
#     fourths = db.Column(db.Integer)
#     totalraces = db.Column(db.Integer)
#     winsr = db.Column(db.Float)
#     roi_level = db.Column(db.Float)
#     favorites = db.Column(db.Integer)
#     perf_seq = db.Column(db.TEXT())
#     maxlosingstreak = db.Column(db.Integer)
#     maxwinningstreak = db.Column(db.Integer)
#     last10 = db.Column(db.String(40))
#     updated = db.Column(db.TIMESTAMP)
#     updated_date = db.Column(db.Date)

#     t_system_id= db.Column(db.Integer, ForeignKey('t_system.id'))
#     t_system = relationship("t_system",
#         backref=db.backref('t_systemperformances', lazy='dynamic')) ## t_SystemPerformance.t_systems.all() QUERY

#     __table_args__ = (UniqueConstraint('updated', 't_system_id'),)

#     def __init__(self, t_system_id, tipsterscore, winners, seconds, thirds, fourths, totalraces, winsr, roi_level,favorites,
#         perf_seq, maxlosingstreak, maxwinningstreak, last10, updated=datetime.utcnow()):
#         self.t_system_id = t_system_id
#         self.tipsterscore = tipsterscore
#         self.winners = winners
#         self.seconds = seconds
#         self.thirds = thirds
#         self.fourths = fourths
#         self.totalraces = totalraces
#         self.winsr = winsr
#         self.roi_level = roi_level
#         self.favorites = favorites
#         self.perf_seq = perf_seq
#         self.maxlosingstreak = maxlosingstreak
#         self.maxwinningstreak = maxwinningstreak
#         self.last10 = last10
#         self.updated = updated
#         self.updated_date = updated.date()

# '''
# ODDS

# '''

# class o_HKOdds(db.Model):
#     __tablename__ = "o_hk_odds"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) # Unique ID
#     horsenumber = Column("horsenumber", Integer, nullable = False) # Horse number.

#     updatedatetime = Column("updatedate", DateTime, nullable = False) # Date and time of last update.
#     winodds = Column("winodds", DECIMAL(10,2)) # Odds of win. It's not float! Float for money is not acceptable!
#     iswinfav = Column("isWinFav", db.Integer) # Some times this parameter can takes value 2 and more.
#     placeodds = Column("placeodds", DECIMAL(10,2)) # The same as Win odds.
#     isplacefav = Column("isPlaceFav", db.Integer) # The same as is_win_fav.
#     pool = Column("pool", db.BigInteger) # Pool size.
#     isReserve = Column("isReserve", db.Boolean) # Reserve data.
#     isScratched = Column("isScratched", db.Boolean) # Scratched data.

#     race_id = db.Column(db.Integer, ForeignKey('race.id'))
#     race = relationship("Race", 
#         backref=db.backref('odds', lazy='dynamic'))    
#     horse_id = db.Column(db.Integer, ForeignKey('horse.id'))
#     horse = relationship("Horse", 
#         backref=db.backref('odds', lazy='dynamic')) 

#     def __init__(self, racedate, racecoursecode, racenumber, horsenumber, updatedatetime, winodds, iswinfav, placeodds, isplacefav, pool, isReserve = False, isScratched = False):
#         self.racedate = racedate
#         self.racecoursecode = racecoursecode
#         self.racenumber = racenumber
#         self.horsenumber = horsenumber
#         self.updatedatetime = updatedatetime
#         self.winodds = winodds
#         self.iswinfav = iswinfav
#         self.placeodds = placeodds
#         self.isplacefav = isplacefav
#         self.pool = pool
#         self.isReserve = isReserve
#         self.isScratched = isScratched

# '''
# Aggregate Data

# '''
# class o_HKOddsAgg(db.Model):
#     __tablename__ = "o_hkoddsagg"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) # Unique ID
#     horsenumber = db.Column(db.Integer)
#     opwin = db.Column(db.Float)
#     opwinrank = db.Column(db.Integer)
#     win12am = db.Column(Float)
#     win6am  = db.Column(Float)
#     win8am = db.Column(Float)
#     win12pm = db.Column(Float)
#     winl20mins= db.Column(Float)
#     winl10mins= db.Column(Float)
#     winl5mins= db.Column(Float)
#     winl2mins= db.Column(Float)
#     winsp = db.Column(Float)
#     winsprank = db.Column(db.Integer)
#     winnowopdiff = db.Column(Float)
#     diffthislast = db.Column(Float)

#     race_id = db.Column(db.Integer, ForeignKey('race.id'))
#     race = relationship("Race", 
#         backref=db.backref('odds', lazy='dynamic'))    
#     horse_id = db.Column(db.Integer, ForeignKey('horse.id'))
#     horse = relationship("Horse", 
#         backref=db.backref('odds', lazy='dynamic')) 

#     def __init__(self,race_id, horse_id, horsenumber,opwin,opwinrank,win12am,win6am,win8am,win12pm,winl20mins,winl10mins,winl5mins,winl2mins, winsp,
#         winsprank,winnowopdiff,diffthislast):
#         self.race_id = race_id
#         self.horse_id = horse_id
#         self.horsenumber = horsenumber
#         self.opwin = opwin
#         self.opwinrank = opwinrank
#         self.win12am = Win12am
#         self.win6am = Win6am
#         self.win8am = Win8am
#         self.win12pm = Win12pm
#         self.winl20mins = winl20mins
#         self.winl10mins = winl10mins
#         self.winl5mins = winl5mins
#         self.winl2mins = winl2mins
#         self.winsp = winsp
#         self.winsprank= winsprank
#         self.winnowopdiff = winnowopdiff
#         self.diffthislast = diffthislast
