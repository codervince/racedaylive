
## rd_models
##make sure these are created!
# dividends go in r_race same index
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
    racesurface = db.Column(db.String(15)) #AWT or C+3 A   
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
	horsenumber = db.Column(db.Integer)
	horsecode = db.Column(db.String(10))
	horsename = db.Column(db.String(60))
	jockeycode = db.Column(db.String(10))
	trainercode = db.Column(db.String(10))
	ownername = db.Column(db.String(100))
	todaysrating = db.Column(db.Integer)
	lastwonat= db.Column(db.Integer)
	isMaiden = db.Column(db.Boolean)
	seasonstakes =db.Column(db.Float)
	draw = db.Column(db.Integer)
	isScratched = db.Column(db.Boolean)
	priority = db.Column(db.String(100))
	gear = db.Column(db.String(20))
    __table_args__ = (UniqueConstraint('raceid', 'horsecode'),)

    def __init__(self, raceid, horsenumber, horsename, horsecode, jockeycode, trainercode, ownername, todaysrating, lastwonat, isMaiden, seasonstakes, draw, isScratched=False, priority, gear):
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
