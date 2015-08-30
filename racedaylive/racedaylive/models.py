
class rd_owner(ModelBase):
    __tablename__ = "rd_owner"
    name = Column("name", String(255), nullable=False)
    __table_args__ = (UniqueConstraint('name'),)
    def __init__(self, name):
        self.name= name
  
class rd_horse(ModelBase):
    __tablename__ = "rd_horse"
    horsename = Column("horsename", String(255), nullable=False)
    horsecode = Column("horsecode", String(6), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('horsecode'),)
    def __init__(self, horsename, horsecode):
        self.horsename= horsename
        self.horsecode = horsecode

class rd_trainer(ModelBase):
    __tablename__ = "rd_trainer"
    trainername = Column("trainername", String(255), nullable=False)
    trainercode = Column("trainercode", String(6), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('trainercode'),)
    def __init__(self, trainername, trainercode):
        self.horsename= trainername
        self.horsecode = trainercode

class rd_jockey(ModelBase):
    __tablename__ = "rd_jockey"
    jockeyname = Column("jockeyname", String(255), nullable=False)
    jockeycode = Column("jockeycode", String(6), nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('jockeycode'),)
    def __init__(self, jockeyname, jockeycode):
        self.horsename= jockeyname
        self.horsecode = jockeycode

    # runners = relationship("HKRunner", backref="horse")
    # racedays = relationship("HKraceday", backref="horse")
    # trackevents = relationship("HKTrackwork", backref="horse")
    # vetevents = relationship("HKVet", backref="horse")
    # UniqueConstraint('name', 'code', 'homecountry', name='Horsecodehomecountry_uidx')


class rd_race(db.Model):
    __tablename__ = "rd_race"
    id = db.Column(db.Integer, primary_key=True)
    racedate = db.Column(db.Date)
    racecoursecode = db.Column(db.String(5))
    racenumber = db.Column(db.Integer)
    racename = db.Column(db.String(150))
    raceclass = db.Column(db.String(50))
    racerating = db.Column(db.String(50))
    racegoing = db.Column(db.String(10)) #GF GY Y 
    racesurface = db.Column(db.String(15)) #AWT or B+3
    racedistance = db.Column(Integer) # 1000
    utcracetime = db.Column(db.TIMESTAMP()) #exact jump time updatable
    runners = relationship("rd_runner")
    __table_args__ = (UniqueConstraint('racedate', 'racecoursecode', 'racenumber'),)
    
    def __init__(self, racedate, racecoursecode, racenumber, racename, raceclass, racerating, racegoing,racesurface, racedistance, utcracetime):
        self.racedate = racedate
        self.racecoursecode = racecoursecode
        self.racenumber = racenumber
        self.racename = racename
        self.raceclass = raceclass
        self.racerating = racerating
        self.racegoing = racegoing
        self.racesurface = racesurface
        self.racedistance = racedistance
        self.utcracetime = utcracetime
  
  ##results go in r_runner same index
class rd_runner(db.Model):
	__tablename__ = "rd_runner"
	id = db.Column(db.Integer, primary_key=True)
	race_id = db.Column(db.Integer, ForeignKey('rd_race.id'))
    rd_owner_id = db.Column(db.Integer, ForeignKey('rd_owner.id'))
    rd_horse_id = db.Column(db.Integer, ForeignKey('rd_horse.id'))
    rd_trainer_id = db.Column(db.Integer, ForeignKey('rd_trainer.id'))
    rd_jockey_id = db.Column(db.Integer, ForeignKey('rd_jockey.id'))
    horsenumber = db.Column(db.Integer)
	todaysrating = db.Column(db.Integer)
	lastwonat= db.Column(db.Integer)
	isMaiden = db.Column(db.Boolean)
	seasonstakes =db.Column(db.Float)
	draw = db.Column(db.Integer)
	isScratched = db.Column(db.Boolean)
	priority = db.Column(db.String(100))
	gear = db.Column(db.String(20))
    placing= db.Column(db.Integer)
    finish_time = db.Column(db.Float) #seconds
    marginsbehindleader = db.Column(ARRAY(Float)) #floats
    positions = db.Column(ARRAY(Integer)) #ints
    timelist= db.Column(ARRAY(Float))
    scmp_runner_comment = db.Column(db.String(256))
    barriertimes = db.Column(ARRAY(String(100)))
    jumptimes = db.Column(ARRAY(String(100)))
    totalbarrier = db.Column(ARRAY(Integer)) 
    totalcanter =db.Column(ARRAY(Integer)) 
    totaljump = db.Column(ARRAY(Integer)) 
    totalswim = db.Column(ARRAY(Integer)) 
    ##extras??

    __table_args__ = (UniqueConstraint('raceid', 'horsecode'),)

    def __init__(self, raceid, horsenumber, horsename, horsecode, jockeycode, trainercode, ownername,
        todaysrating, lastwonat, isMaiden, seasonstakes, draw, isScratched=False, priority, gear,placing, finish_time,
        marginsbehindleader, positions, timelist,scmp_runner_comment, barriertimes, jumptimes ):
    	self.raceid = raceid
    	self.horsenumber = horsenumber
    	self.horsename = horsename
    	self.horsecode = horsecode
    	self.jockeycode = jockeycode
    	self.trainercode = trainercode
    	self.ownername = ownername
    	self.todaysrating = todaysrating
    	self.lastwonat= lastwonat
    	self.isMaiden = isMaiden
    	self.seasonstakes = seasonstakes
    	self.draw= draw
    	self.isScratched = isScratched
    	self.priority = priority
    	self.gear = gear
        self.placing = placing
        self.finish_time = finish_time
        self.marginsbehindleader = marginsbehindleader
        self.timelist = timelist
        self.scmp_runner_comment = scmp_runner_comment
        self.barriertimes = barriertimes
        self.jumptimes = jumptimes
        self.totalbarrier = totalbarrier
        self.totalcanter = totalcanter
        self.totaljump = totaljump
        self.totalswim =totalswim 

##for runnerstats look at results tables WILL BE UPDATED RIGHT AFTER RACE - DISPLAY most recent stats for horse


## tips REFLECT THESE TABLES EXIST!



### reflect
class t_System(db.Model):
    __tablename__ = "t_system"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    animal = db.Column(db.String(60))
    datestarted = db.Column(db.Date)
    datestopped = db.Column(db.Date)
    performances = relationship("t_SystemPerformance") ##I have seen that error before if I forget that ForeignKey() takes the name of a database table-and-field but that relationship() takes the name of an ORM class instead.
    __table_args__ = (UniqueConstraint('name', 'animal'),)

    def __init__(self, name, animal, datestarted, datestopped):
        self.name = name
        self.animal = animal
        self.datestarted = datestarted
        self.datestopped = datestopped
#reflect aka subscriptions
class t_UserSystems(db.Model):
	id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    t_system_id= db.Column(db.Integer, ForeignKey('t_system.id'))
    datestarted = db.Column(db.Date)
    datestopped = db.Column(db.Date)

    def __init__(user_id, t_system_id, datestarted, datestopped):
    	self.user_id = user_id
        self.t_system_id = t_system_id
        self.datestarted = datestarted
        self.datestopped = datestopped

##requires raceday id

class t_Raceday(db.Model):
    __tablename__ = "t_raceday"
    racedate = db.Column(db.Date)
    racecoursecode = db.Column(db.String(5))
    runners_list = db.Column(db.Column(ARRAY(String(5))))

    def __init__(self, racedate, racecoursecode, runnerslist):
        self.racedate = racedate
        self.racecoursecode = racecoursecode
        self.runnerslist = runnerslist

class t_Naps(db.Model):
    __tablename__ = "t_naps"
    t_system_id= db.Column(db.Integer, ForeignKey('t_system.id'))
    t_raceday_id = db.Column(db.Integer, ForeignKey('t_raceday.id'))
    t_race_id= db.Column(db.Integer, ForeignKey('t_race.id'))
    horsenumber = db.Column(db.Integer)
    isnap1 =db.Column(db.Boolean)
    def __init__(self, t_system_id, t_raceday_id, t_race_id, horsenumber, isnap1):
        self.t_system_id = t_system_id
        self.t_raceday_id = t_raceday_id
        self.t_race_id = t_race_id
        self.horsenumber = horsenumber


#reflect
class t_SystemRecords(db.Model):
    __tablename__ = "t_systemrecords"
    id = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False) # Unique ID
    t_race_id = db.Column(db.Integer, ForeignKey('t_race.id'))
    t_system_id= db.Column(db.Integer, ForeignKey('t_system.id'))
    first = db.Column(db.Integer)
    second = db.Column(db.Integer)
    third = db.Column(db.Integer)
    fourth = db.Column(db.Integer)
    updated = db.Column(db.TIMESTAMP)
    updated_date = db.Column(db.Date)
    __table_args__ = (UniqueConstraint('t_race_id', 't_system_id'),)

    def __init__(self,t_race_id, t_system_id, first, second, third, fourth, updated=datetime.utcnow()):
        self.t_race_id= t_race_id
        self.t_system_id=t_system_id
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.updated = updated
        self.updated_date = updated.date()


##SELECTION TABLE
''' 
user table REFLECT
user has a system WHEN HE/SHE SUBSCRIBES!!!

'''




'''
