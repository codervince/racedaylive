from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker, scoped_session, create_session
from sqlalchemy import create_engine
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

# ##RACEDAY TABLES
# class Owner(db.Model):
#     __tablename__ = "owner"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     name = Column("name", String(255), nullable=False)
#     __table_args__ = (UniqueConstraint('name'),)
#     def __init__(self, ownername):
#         self.name= ownername
  
# class Horse(db.Model):
#     __tablename__ = "horse"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     name = Column("horsename", String(255), nullable=False)
#     code = Column("horsecode", String(6), nullable=False, unique=True)
#     __table_args__ = (UniqueConstraint('horsecode'),)
#     def __init__(self, horsename, horsecode):
#         self.horsename= horsename
#         self.horsecode = horsecode

# class Trainer(db.Model):
#     __tablename__ = "trainer"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     name = Column("trainername", String(255), nullable=False)
#     code = Column("trainercode", String(6), nullable=False, unique=True)
#     __table_args__ = (UniqueConstraint('trainercode'),)
#     def __init__(self, trainername, trainercode):
#         self.name= trainername
#         self.code = trainercode

# class Jockey(db.Model):
#     __tablename__ = "jockey"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     name = Column("jockeyname", String(255), nullable=False)
#     code = Column("jockeycode", String(6), nullable=False, unique=True)
#     __table_args__ = (UniqueConstraint('jockeycode'),)
#     def __init__(self, jockeyname, jockeycode):
#         self.name= jockeyname
#         self.code = jockeycode


# class Raceday(db.Model):
#     __tablename__ = "raceday"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     racedate = Column(db.Date, nullable=False)
#     racecoursecode = db.Column(db.String(2))
#     runners_list = db.Column(postgresql.ARRAY(String(5))) #skips race

#     __table_args__ = (UniqueConstraint('racedate', 'racecoursecode'),)
#     def __init__(self, racedate, racecoursecode, runners_list):
#         self.racedate= racedate
#         self.racecoursecode = racecoursecode
#         self.runners_list = runners_list

# class Race(db.Model):
#     __tablename__ = "race"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     racenumber = db.Column(db.Integer)
#     racename = db.Column(db.String(150))
#     raceclass = db.Column(db.String(50))
#     racerating = db.Column(db.String(50))
#     racegoing = db.Column(db.String(10)) #GF GY Y 
#     racesurface = db.Column(db.String(15)) #AWT or B+3
#     racedistance = db.Column(Integer) # 1000
#     utcracetime = db.Column(db.TIMESTAMP()) #exact jump time updatable
#     marketorder = db.Column(db.String(15))
#     result = db.Column(db.String(15))
#     winodds = db.Column(db.Float)
#     favpos = db.Column(db.Integer)
#     favodds = db.Column(db.Float)
#     norunners = db.Column(db.Integer)
#     f4 = db.Column(postgresql.ARRAY(Float))
#     tierce= db.Column(postgresql.ARRAY(Float))
#     qtt = db.Column(postgresql.ARRAY(Float))
#     dt = db.Column(postgresql.ARRAY(Float))
#     tt = db.Column(postgresql.ARRAY(Float))
#     ttc = db.Column(postgresql.ARRAY(Float))
#     sixup = db.Column(postgresql.ARRAY(Float))
#     sixupc = db.Column(postgresql.ARRAY(Float))
#     raceday_id = db.Column(db.Integer, ForeignKey('raceday.id'))

#     raceday = relationship("Raceday", 
#         backref=db.backref('races', lazy='dynamic'))
#     __table_args__ = (UniqueConstraint('raceday_id', 'racenumber'),)
    
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
  
#   ##results go in r_runner same index
# class Runner(db.Model):
#     __tablename__ = "runner"
#     id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) 
#     horsenumber = db.Column(db.Integer)
#     todaysrating = db.Column(db.Integer)
#     lastwonat= db.Column(db.Integer)
#     isMaiden = db.Column(db.Boolean)
#     seasonstakes =db.Column(db.Float)
#     draw = db.Column(db.Integer)
#     isScratched = db.Column(db.Boolean)
#     priority = db.Column(db.String(100))
#     gear = db.Column(db.String(20))
#     placing= db.Column(db.Integer)
#     finish_time = db.Column(db.Float) #seconds
#     marginsbehindleader = db.Column(postgresql.ARRAY(Float)) #floats
#     positions = db.Column(postgresql.ARRAY(Integer)) #ints
#     timelist= db.Column(postgresql.ARRAY(Float))
#     scmp_runner_comment = db.Column(db.String(256))
#     barriertimes = db.Column(postgresql.ARRAY(String(100)))
#     jumptimes = db.Column(postgresql.ARRAY(String(100)))
#     totalbarrier = db.Column(postgresql.ARRAY(Integer)) 
#     totalcanter =db.Column(postgresql.ARRAY(Integer)) 
#     totaljump = db.Column(postgresql.ARRAY(Integer)) 
#     totalswim = db.Column(postgresql.ARRAY(Integer)) 
#     owner_id = db.Column(db.Integer, ForeignKey('owner.id'))
#     owner = relationship("Owner", 
#         backref=db.backref('runners', lazy='dynamic'))

#     jockey_id = db.Column(db.Integer, ForeignKey('jockey.id'))
#     jockey = relationship("Jockey", 
#         backref=db.backref('runners', lazy='dynamic'))

#     trainer_id = db.Column(db.Integer, ForeignKey('trainer.id'))
#     trainer = relationship("Trainer", 
#         backref=db.backref('runners', lazy='dynamic'))

#     horse_id = db.Column(db.Integer, ForeignKey('owner.id'))
#     horse = relationship("Horse", 
#         backref=db.backref('runners', lazy='dynamic'))

#     race_id = db.Column(db.Integer, ForeignKey('race.id'))
#     race = relationship("Race", 
#         backref=db.backref('runners', lazy='dynamic'))

#     __table_args__ = (UniqueConstraint('race_id', 'horse_id'),)

#     def __init__(self, race_id, horsenumber, horse_id, jockey_id, trainer_id, owner_id,
#         todaysrating, lastwonat, isMaiden, seasonstakes, draw, priority, gear,placing, finish_time,
#         marginsbehindleader, positions, timelist,scmp_runner_comment, barriertimes, jumptimes,totalbarrier, totaljump, totalswim, isScratched=False,):
#         self.race_id = race_id
#         self.horsenumber = horsenumber
#         self.horse_id = horse_id
#         self.trainer_id = trainer_id
#         self.jockey_id = jockey_id
#         self.owner_id = owner_id
    
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
