from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session,exc, create_session
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import settings
import items
import sqlalchemy
from collections import *
# from racedaylive.items import *
from racedaylive.models import *
from racedaylive import models
'''
HorseItem

Raceday racedate, racecoursecode, runnerslist self.code_set
Race raceday_id
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


'''

ENGINE = models.get_engine()

def get_or_create_pl(model, item):

    '''
    indexfields should be a dict of the uniqur fields for lookup
    '''

    get_params = lambda model, item: {c.name: item.get(c.name) 
        for c in model.__table__.columns if c.name != 'id'}
    get_unique = lambda model, item: {c.name: item.get(c.name) 
        for c in model.__table__.columns if c.name != 'id' and getattr(c, 'unique')}
    get_unique_together = lambda model, item: [{c.name: item.get(c.name) 
        for c in model.__table_args__[0].columns} 
        for targ in model.__table_args__ if isinstance(
        targ, sqlalchemy.UniqueConstraint)]

    session = Session(bind=ENGINE)

    instance = None
    unique = get_unique(model, item)
    for k, v in unique.iteritems():
        query = session.query(model).filter_by(**{k: v})
        instance = query.first()
        if instance:
            break

    if not instance:
        unique_together = get_unique_together(model, item)
        for params in unique_together:
            query = session.query(model).filter_by(**params)
            instance = query.first()
            if instance:
                break

    created = False
    kwargs = get_params(model, item)
    params = dict(
        (k, v) for k, v in kwargs.iteritems()
        if not isinstance(v, ClauseElement))
    if not instance:
        #params.update(defaults)
        instance = model(**params)
    else:
        for k, v in params.iteritems():
            setattr(instance, k, v)

    try:
        session.add(instance)
        session.commit()
        created = True
    except Exception:
        session.close()
        raise

    session.refresh(instance)  # Refreshing before session close
    session.close()
    return instance

# def get_or_create(model, defaults=None, **kwargs):
#     ''' 
#     needs to be able to do LOOKUP BASED ON THE UNIQUE INDEX
#     Short get or create implementation. Like in Django.
#     This can run within the read_pool
#     We don't use write scheduling here, because of very low amount of writes.
#     Optimization unneeded, as I think.
#     We use this function to prevent IntegrityError messages.
#     '''

#     defaults = defaults or {}

#     session = Session()  # I'm thread safe =)

#     query = session.query(model).filter_by(**kwargs)

#     instance = query.first()

#     created = False

#     if not instance:
#         params = dict(
#             (k, v) for k, v in kwargs.iteritems()
#             if not isinstance(v, ClauseElement))
#         params.update(defaults)
#         instance = model(**params)

#         try:
#             session.add(instance)
#             session.commit()
#             created = True
#         except IntegrityError:
#             session.rollback()
#             instance = query.one()
#             created = False
#         except Exception:
#             session.close()
#             raise

#     session.refresh(instance)  # Refreshing before session close
#     session.close()
#     return instance, created


class RacedaylivePipelineHorseItem(object):

    def process_item(self, item, spider):

        if not isinstance(item, items.HorseItem):
            return

        owner = get_or_create_pl(models.Owner, item)
        horse = get_or_create_pl(models.Horse, item)
        trainer = get_or_create_pl(models.Trainer, item)
        jockey = get_or_create_pl(models.Jockey, item)
        raceday = get_or_create_pl(models.Raceday, item)
 
        item['raceday_id'] = raceday.id
        race = get_or_create_pl(models.Race, item)
 
        item['owner_id'] = owner.id
        item['jockey_id'] = jockey.id
        item['trainer_id'] = trainer.id
        item['horse_id'] = horse.id
        item['race_id'] = race.id
        get_or_create_pl(models.Runner, item)


class RacedaylivePipeline(object):

    def __init__(self):
        Base = automap_base()
        engine = create_engine(URL(**settings.DATABASE))
        # create_tables(engine)    
        Base.prepare(engine, reflect=True)

        Raceday = Base.classes.raceday
        Race = Base.classes.race
        Runner = Base.classes.runner
        Owner = Base.classes.owner
        Trainer = Base.classes.trainer
        Jockey = Base.classes.jockey
        Horse = Base.classes.horse

        self.Session = sessionmaker(bind=engine)
        self.cache = defaultdict(lambda: defaultdict(lambda: None)) #necessary?
        session = create_session(bind=engine)
        
        testlist = session.query(Raceday).all()     
        for test in testlist:  
            print test.racedate

    # write to rd_race
    def process_item(self, item, spider):
        session = self.Session()
        #which item?
        # if isinstance(item, HorseItem):
            # iscreated = False
        '''
        horsenumber = db.Column(db.Integer)
	    todaysrating = db.Column(db.Integer)
	    lastwonat= db.Column(db.Integer)
	    isMaiden = db.Column(db.Boolean)
	    seasonstakes =db.Column(db.Float)
	    draw = db.Column(db.Integer)
	    isScratched = db.Column(db.Boolean)
	    priority = db.Column(db.String(100))
	    gear = db.Column(db.String(20))
        '''
        #creating runner object nested
        #or dictionary

        #get racedays
        raceday_id = get_or_create_pl(
                Raceday,{racedate:item.get("racedate", None),racecoursecode:item.get("racecoursecode", None)}  ,
                    racedate= item.get("racedate", None),
                    racecoursecode= item.get("RacecourseCode", None),
                    runnerslist=RaceSpider.code_set
                   )
        print raceday_id
        return item
   #          runner = Runner(

   #          race_id = get_or_create_pl(
   #          	Race,
   #          	{raceday_id: get_or_create_pl(Raceday,{racedate:item.get("racedate", None),\
   #           racecoursecode:item.get("racecoursecode", None)},\
   #          	racedate=item.get("racedate", None), racecoursecode=item.get("racecoursecode", None),\
   #          	runnerslist=self.code_set,racenumber:item.get("racenumber", None)).id,racenumber = item.get("racenumber", None)},
   #          	racenumber= item.get("racenumber", None)
			# 	racename = item.get("racename", None)
			# 	raceclass = item.get("raceclass", None)
			# 	racerating = item.get("racerating", None)
			# 	racegoing = item.get("racegoing", None)
			# 	racesurface = item.get("racesurface", None)
			# 	racedistance = item.get("racedistance", None)
			# 	utcracetime = item.get("utcracetime", None)
			# 	norunners = len(self.runners_list[racenumber]),
			# 	raceday_id = get_or_create_pl(Raceday,{racedate:item.get("racedate", None),\
   #           racecoursecode:item.get("racecoursecode", None)},\
   #          	racedate=item.get("racedate", None), racecoursecode=item.get("racecoursecode", None),\
   #          	runnerslist=self.code_set,racenumber:item.get("racenumber", None)).id
			# 	),
			# 	#end race 
   #          horse_id= get_or_create_pl(Horse,\
   #          	{code:item.get("code", None)},\
   #          	name=item.get("name", None), 
   #      	code=item.get("code", None)).id,

   #          trainer_id = get_or_create_pl(Trainer,{code:item.get("code", None)},
   #      	name=item.get("name", None), 
   #      	code=item.get("code", None)).id,

   #          jockey_id = get_or_create_pl(Jockey,{code:item.get("code", None)},
   #      	name=item.get("name", None), 
   #      	code=item.get("code", None)).id,

   #          owner_id = get_or_create_pl(Owner,{code:item.get("name", None)},
			# horsenumber = item.get("horsenumber", None)
			# todaysrating = item.get("todaysrating", None)
			# lastwonat= item.get("lastwonat", None)
			# isMaiden = item.get("isMaiden", None)
			# seasonstakes =item.get("seasonstakes", None)
			# draw = item.get("draw", None)
			# isScratched = item.get("isScratched", None)
			# priority = item.get("priority", None)
			# gear = item.get("gear", None)
   #      	)

   #          	print raceday_id, horse_id
   #          	# yield raceday_id
   #          assert owner_id is not None
   #          # return item
        # else:
        # 	pass
        # try:
        #     # session.add(races)
        #     # session.add(runners)
        #     # session.commit()
        # except:
        #     # session.rollback()
        #     raise
        # finally:
        #     # session.close()

            # return






            ##do RACE
'''
RA
racenumber = db.Column(db.Integer)
racename = db.Column(db.String(150))
raceclass = db.Column(db.String(50))
racerating = db.Column(db.String(50))
racegoing = db.Column(db.String(10)) #GF GY Y 
racesurface = db.Column(db.String(15)) #AWT or B+3
racedistance = db.Column(Integer) # 1000
utcracetime = db.Column(db.TIMESTAMP()) #exact jump time updatable
norunners = db.Column(db.Integer)
'''
            # raceid,iscreated = get_or_create(Race,
            # 	racenumber=item.get("racenumber", None),
            # 	racename=item.get("racename", None),
            # 	raceclass=item.get("raceclass", None),
            # 	racegoing=item.get("racegoing", None),
            # 	racesurface=item.get("racesurface", None),
            # 	racedistance=item.get("racedistance", None),
            # 	utcracetime=item.get("utcracetime", None),
            # 	norunners=len(self.runners_list[racenumber]),
            # 	raceday_id= raceday_id
            # 	)
            # yield raceid
'''
RU 
horsenumber = db.Column(db.Integer)
todaysrating = db.Column(db.Integer)
lastwonat= db.Column(db.Integer)
isMaiden = db.Column(db.Boolean)
seasonstakes =db.Column(db.Float)
draw = db.Column(db.Integer)
isScratched = db.Column(db.Boolean)
priority = db.Column(db.String(100))
gear = db.Column(db.String(20))
'''
        #    horseid = get_or_create(
        #     Horse, 
        #         "Name": item["Horsename"],
        #         "Code": item["Horsecode"],
        #         "SireName": item["SireName"],
        #         "DamName": item["DamName"],
        #         "ImportType": item["ImportType"],
        #         "Sex": item["Sex"],
        #         "Homecountry": 'HKG',
        #         "YearofBirth": item["LocalRaceDateTime"].replace(item["LocalRaceDateTime"].year - item.get("Age",0)).year
        #     })

        # jockeyid = self.scheduler.get_id(
        #     Jockey, "Name",
        #     {
        #         "Name": item["Jockeyname"],
        #         "Code": item["Jockeycode"],
        #         "Homecountry": 'HKG'
        #     })


        # trainerid = self.scheduler.get_id(
        #     Trainer, "Name",
        #     {
        #         "Name": item["Trainername"],
        #         "Code": item["Trainercode"],
        #         "Homecountry": 'HKG'

        #     })

        # ownerid = self.scheduler.get_id(
        #     Owner, "Name",
        #     {   "Name": item["Owner"]   

        #     })

            # horse, jockey, trainer, owner
            
        # print 
        # racedays = RPRacedaydump(

        #             racename = item.get("racename", None),
        #             racedate= item.get("racedate",None),
        #             racecoursecode= item.get("racecourse",None),
        #             Racetime= item.get("racetime",None),
        #             Racepm= item.get("racepm", None),
   					# ...
        #         )
        # try:
        # # session.add(races)
        #     session.add(racedays)
        #     session.commit()
        # except:
        #     session.rollback()
        #     raise
        # finally:
        #     session.close()
        

# # -*- coding: utf-8 -*-

# # Define your item pipelines here
# #
# # Don't forget to add your pipeline to the ITEM_PIPELINES setting
# # See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# from __future__ import print_function

# import traceback
# from Queue import Queue, Empty
# from collections import defaultdict, Counter

# from racedaylive import settings
# from racedaylive.items import *
# from racedaylive.models import *
# from scrapy import log
# from scrapy.signalmanager import SignalManager
# from scrapy.signals import spider_closed
# from scrapy.xlib.pydispatch import dispatcher
# from sqlalchemy import update, or_
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import sessionmaker, scoped_session
# from sqlalchemy.sql.expression import ClauseElement
# from twisted.internet.defer import inlineCallbacks, returnValue
# from twisted.internet.threads import deferToThreadPool
# from twisted.python.threadable import isInIOThread
# from twisted.python.threadpool import ThreadPool
# from StringIO import StringIO

# # Needed for multithreading, as I remember
# Session = scoped_session(sessionmaker(bind=engine))
# from theseus import Tracer

# # if settings.DEBUG:
# #     engine.echo = True


# def dicthash(inp):
#     return tuple(sorted(inp.iteritems(), key=lambda item: item[0]))


# def row2dict(row):

#     if isinstance(row, dict):
#         return row

#     d = {}
#     for column in row.__table__.columns:
#         d[column.name] = str(getattr(row, column.name))

#     return d


# class ProfiledThreadPool(ThreadPool):

#     @staticmethod
#     def output_callgrind(out):
#         with open('callgrind.theseus', 'ab') as f:
#             f.write(out)

#     def _worker(self):
#         from twisted.internet import reactor
#         tracer = Tracer()
#         tracer.install()
#         ThreadPool._worker(self)

#         out = StringIO()

#         tracer.write_data(out)

#         reactor.callFromThread(self.output_callgrind, out.getvalue())
#         out.close()
#         tracer.uninstall()


# def get_or_create(model, defaults=None, **kwargs):
#     ''' Short get or create implementation. Like in Django.
#     This can run within the thread_pool
#     We don't use write scheduling here, because of very low amount of writes.
#     Optimization unneeded, as I think.
#     We use this function to prevent IntegrityError messages.
#     '''

#     defaults = defaults or {}

#     session = Session()  # I'm thread safe =)

#     query = session.query(model).filter_by(**kwargs)

#     instance = query.first()

#     created = False

#     if not instance:
#         params = dict(
#             (k, v) for k, v in kwargs.iteritems()
#             if not isinstance(v, ClauseElement))
#         params.update(defaults)
#         instance = model(**params)

#         try:
#             session.add(instance)
#             session.commit()
#             created = True
#         except IntegrityError:
#             session.rollback()
#             instance = query.one()
#             created = False
#         except Exception:
#             session.rollback()
#             session.close()
#             raise

#     session.refresh(instance)  # Refreshing before session close
#     session.close()
#     return instance, created


# class Reporter(object):

#     def __init__(self):
#         self.counters = defaultdict(lambda: Counter())
#         ''' Statistical counters. You may access them directly if needed '''

#         self.id_counters = defaultdict(
#             lambda: defaultdict(
#                 lambda: set()))
#         ''' More complex counter used storing item keys '''

#         self._created = defaultdict(lambda: list())
#         ''' All created items by type '''

#         self._updated = defaultdict(lambda: list())
#         ''' All updated items. Should be list of tuples '''

#     def saved(self, model, item_id):
#         self.id_counters['created'][model].add(item_id)

#     def updated(self, model, item_id, item, old_item):
#         self.id_counters['updated'][model].add(item_id)
#         self._updated[model].append((item_id, item, old_item))

#     def unchanged(self, model, item_id):
#         self.id_counters['unchanged'][model].add(item_id)

#     def get_report(self):
#         out = StringIO()

#         print('========== Spider report ==========', file=out)
#         print(file=out)
#         print('---------- Counters ---------------', file=out)

#         for counter, results in self.counters.iteritems():
#             print(counter, file=out)
#             for modelname, count in results.iteritems():
#                 print('  {} - {}'.format(modelname.__name__, count), file=out)

#         for counter, results in self.id_counters.iteritems():
#             print(counter, file=out)
#             for modelname, items in results.iteritems():
#                 print('  {} - {}'.format(
#                     modelname.__name__, len(items)), file=out)

#         print('---------- Updated objects --------', file=out)
#         print(file=out)

#         for counter, items in self._updated.iteritems():
#             print(str(counter), file=out)

#             items = sorted(items)

#             for item_id, new, old in items:
#                 print('-----------------------------------', file=out)
#                 print(item_id, file=out)
#                 old = row2dict(old)
#                 for key, value in row2dict(new).iteritems():
#                     old_value = old.get(key)

#                     if str(old_value) != str(value):
#                         print('{}: {} to {}'.format(
#                             key, old_value, value), file=out)

#         result = out.getvalue()
#         out.close()

#         return result


# class DBScheduler(object):
#     ''' Database operation scheduler
#     We will have one or more read thread and only one write thread.
#     '''

#     def __init__(self, spider):
#         from twisted.internet import reactor  # Imported here.inside

#         self.spider = spider
#         ''' Used for logging for now '''

#         self.reactor = reactor
#         ''' Used for thred pools '''

#         engine = get_engine()
#         create_schema(engine)

#         self.thread_pool = ThreadPool(
#             minthreads=1, maxthreads=13, name="ReadPool")

#         # There should be only one pool in the write_pool
#         # Never increase maxtreads value
#         self.write_pool = ProfiledThreadPool(
#             minthreads=1, maxthreads=1, name="WritePool")

#         self.thread_pool.start()
#         self.write_pool.start()

#         self.signals = SignalManager(dispatcher.Any).connect(
#             self.stop_threadpools, spider_closed)

#         self.reporter = Reporter()
#         ''' Reporer is used for statistics collection '''
#         self.counters = self.reporter.counters

#         self.cache = defaultdict(
#             lambda: dict())

#         self.write_queue = Queue()
#         self.writelock = False  # Write queue mutex

#     def stop_threadpools(self):
#         self.thread_pool.stop()
#         self.write_pool.stop()

#         for line in self.reporter.get_report().splitlines():
#             log.msg(line)

#     def _do_save_item(self, item):
#         ''' Save items one by one '''
#         assert not isInIOThread()

#         session = Session()

#         session.add(item)

#         try:
#             session.commit()
#             self.reporter.saved(item.__class__, item)
#             result = True
#         except IntegrityError as error:
#             session.rollback()
#             result = False
#         finally:
#             session.close()

#         return result

#     def _do_save(self):
#         assert not isInIOThread()

#         while not self.write_queue.empty():
#             items = []

#             try:
#                 self.writelock = True
#                 try:
#                     while True:
#                         items.append(self.write_queue.get_nowait())
#                 except Empty:
#                     pass

#                 session = Session()

#                 try:
#                     session.add_all(items)
#                     session.commit()

#                     # All items were unique.
#                     # All of them are counted

#                     for item in items:
#                         self.reporter.saved(item.__class__, item)

#                 except IntegrityError as error:
#                     # This is needed because we are calling from the thread

#                     self.spider.log(
#                         'Exception occured while saving objects: {}'.format(
#                             error), level=log.WARNING)

#                     self.spider.log(
#                         traceback.format_exc(), level=log.DEBUG)

#                     session.rollback()

#                     self.spider.log(
#                         'Saving {} items one by one'.format(len(items)))

#                     for item in items:
#                         # Saving items one by one
#                         self._do_save_item(item)
#                 except Exception:
#                     session.rollback()
#                     raise
#                 finally:
#                     session.close()
#             finally:
#                 self.writelock = False

#     def save(self, obj):
#         ''' Save object.
#         Very effective if we know, that object
#         doesn't exist within the database.
#         If the object already exists - ignore it.
#         TODO: Maybe we need to implement strategy when
#         object update will be needed on duplicate.
#         '''

#         self.write_queue.put(obj)

#         if self.writelock:
#             return None
#         else:
#             return deferToThreadPool(
#                 self.reactor, self.write_pool, self._do_save)

#     def _do_update_if_changed(self, model, selector, updated):
#         ''' Update model matching some *selector* dict and
#         if it's changed.
#         For each custom situation custom query should be built
#         using *case* function.
#         This function is very general.
#         '''

#         assert not isInIOThread()

#         result_query = update(model)

#         for field, value in selector.iteritems():
#             result_query = result_query.where(
#                 getattr(model, field) == value)

#         result_query = result_query.where(
#             reduce(or_, [getattr(model, field) != value
#                          for field, value in updated.iteritems()]))

#         result_query = result_query.values(**updated)

#         session = Session()

#         try:
#             result = session.execute(result_query)
#             session.commit()
#         except:
#             session.rollback()
#             raise
#         finally:
#             session.close()

#         return result.rowcount

#     @inlineCallbacks
#     def update_if_changed(self, model, selector, updated):
#         result = 0

#         item = dict(selector)
#         item.update(updated)

#         old_item = yield self.get_changed(model, selector, updated)

#         if old_item is not None:
#             result = yield deferToThreadPool(
#                 self.reactor, self.thread_pool,
#                 self._do_update_if_changed, model, selector, updated)

#             if result:
#                 self.reporter.updated(
#                     model, dicthash(selector), item, old_item)
#         else:
#             self.reporter.unchanged(model, dicthash(selector))

#         returnValue(result)

#     def _do_update(self, model, selector, updated):
#         assert not isInIOThread()

#         session = Session()

#         try:
#             result = session.query(model).filter_by(**selector).update(updated)
#             session.commit()
#         except:
#             session.rollback()
#             raise
#         finally:
#             session.close()

#         return result

#     def update(self, model, selector, updated):
#         ''' Update model matching some *selector* dict and
#         replacing it's values from *updated* dict.
#         Universal solution, but slow. Really slow.
#         For each custom situation custom query should be built
#         using *case* function.
#         '''

#         return deferToThreadPool(
#             self.reactor, self.thread_pool,
#             self._do_update, model, selector, updated)

#     def _do_exists(self, model, selector):
#         session = Session()

#         try:
#             result = bool(
#                 session.query(model.id).filter_by(**selector).scalar())
#             return result
#         finally:
#             session.close()

#     def exists(self, model, selector):
#         ''' Check whether object matching selector exists '''
#         return deferToThreadPool(
#             self.reactor, self.thread_pool,
#             self._do_exists, model, selector)

#     def _do_is_changed(self, model, selector, updated):
#         session = Session()

#         result_query = session.query(model.id).filter(**selector)

#         result_query = result_query.filter(
#             reduce(or_, [getattr(model, field) != value
#                          for field, value in updated.iteritems()]))

#         try:
#             result = bool(result_query.scalar())
#         finally:
#             session.close()

#         return result

#     def is_changed(self, model, selector, updated):
#         ''' Check whether model fields are changed '''
#         return deferToThreadPool(
#             self.reactor, self.thread_pool,
#             self._do_is_changed, model, selector, updated)

#     def _do_get_changed(self, model, selector, updated):
#         session = Session()

#         query = session.query(model).filter_by(**selector)

#         query = query.filter(
#             reduce(or_, [getattr(model, field) != value
#                          for field, value in updated.iteritems()]))

#         try:
#             item = query.first()

#             if item is not None:
#                 item = row2dict(item)

#             return item
#         finally:
#             session.close()

#     def get_changed(self, model, selector, updated):
#         ''' Return model if it's changed and None if it's unchanged '''
#         return deferToThreadPool(
#             self.reactor, self.thread_pool,
#             self._do_get_changed, model, selector, updated)

#     def _do_get_id(self, model, unique, fval, fields):
#         assert not isInIOThread()

#         session = Session()

#         try:
#             result = session.query(model.id).filter(
#                 getattr(model, unique) == fval).one().id
#             return result
#         finally:
#             session.close()

#     @inlineCallbacks
#     def get_id(self, model, unique, fields,
#                update_existing=False):
#         ''' Get an ID from the cache or from the database.
#         If doesn't exist - create an item.
#         All database operations are done from
#         the separate thread
#         - update_existing: Update object if it exists within the database.
#         '''
#         assert isInIOThread()

#         fval = fields[unique]

#         try:
#             result = self.cache[model][fval]
#             self.counters['cache.hit'][model] += 1
#             returnValue(result)
#         except KeyError:
#             self.counters['cache.miss'][model] += 1

#         selectors = {unique: fval}

#         result, created = yield deferToThreadPool(
#             self.reactor, self.thread_pool,
#             get_or_create,
#             model, fields, **selectors)

#         if created:
#             self.reporter.saved(model, result)
#         else:
#             self.counters['db.cache.hit'][model] += 1
#             if update_existing:
#                 yield self.update_if_changed(
#                     model, {unique: fval}, fields)

#         result = result.id

#         self.cache[model][fval] = result
#         returnValue(result)


# class RacedaylivePipeline(object):

#     def open_spider(self, spider):
#         self.scheduler = DBScheduler(spider)

#     @inlineCallbacks
#     def process_item(self, item, spider):
#     	pp.pprint(RaceSpider.code_set)
#         if isinstance(item, HorseItem):
#         #do horse
#         '''
#     racedate = db.Column(db.Date)
#     racecoursecode = db.Column(db.String(5))
#     racenumber = db.Column(db.Integer)
#     racename = db.Column(db.String(150))
#     raceclass = db.Column(db.String(50))
#     racerating = db.Column(db.String(50))
#     racegoing = db.Column(db.String(10)) #GF GY Y 
#     racesurface = db.Column(db.String(15)) #AWT or C+3 A   
#     racedistance = db.Column(Integer) # 1000
#     utcracetime = db.Column(db.TIMESTAMP()) #exact jump time updatable
#         '''

#             raceid = self.scheduler.get_id(
#                 rd_race, 'racedate', 'racecoursecode', 'racenumber'
#                 {
#                     "racedate": item["racedate"],
#                     "racecoursecode": item["racecoursecode"],
#                     "racenumber": item["racenumber"]
#                     "racename" : item["racename"]
#                     "raceclass" : item["raceclass"]
#                     "racerating" : item["racerating"]
#                     "racegoing": item["racegoing"]
#                     "racesurface": item["racesurface"]
#                     "racedistance": item["racedistance"]
#                     "utcracetime": item["utcracetime"]
#                 })
#             '''
#         self.raceid = raceid
#     	self.horsenumber = horsenumber
#     	self.horsename = horsename
#     	self.horsecode = horsecode
#     	self.jockeycode = jockeycode
#     	self.trainercode = trainercode
#     	self.ownername = ownername
#     	self.todaysrating = todaysrating
#     	self.lastwonat= lastwonat
#     	self.isMaiden = isMaiden
#     	self.seasonstakes = seasonstakes
#     	self.draw= draw
#     	self.isScratched = isScratched
#     	self.priority = priority
#     	self.gear = gear
#             '''
#             #raceid goes into runner
#             raceid = yield raceid

#             thisrunner = rd_runner(
#                 horsenumber = item["horsenumber"],
#                 horsename = item["horsename"],
#                 horsecode = item["horsecode"],
#                 trainercode = item["trainercode"],
#                 ownername = item["ownername"],
#                 todaysrating = item["todaysrating"],
#                 lastwonat = item["lastwonat"],
#                 isMaiden = item["isMaiden"],
#                 seasonstakes = item["seasonstakes"],
#                 draw = item["draw"]
#                 isScratched = item["isScratched"]
#                 priority = item["priority"]
#                 gear = item["gear"]
#                 raceid = raceid
#                 )
#         #do vet table eventdate details passeddate
#             self.scheduler.save(thisrunner)

#         # if isinstance(item, RaceItem):

#         #     ownerid = self.scheduler.get_id(
#         #         Owner, 'name',
#         #         {
#         #             "name": item["Owner"],
#         #             "homecountry": item["Homecountry"]
#         #         }, update_existing=True)

#         #     gearid = self.scheduler.get_id(
#         #         Gear, "name",
#         #         {
#         #             "name": item["Gear"]
#         #         }, update_existing=True)

#         #     eventtypeid = self.scheduler.get_id(
#         #         EventType, "name",
#         #         {
#         #             "name": item["EventType"]
#         #         }, update_existing=True)

#         #     horseid = self.scheduler.get_id(
#         #         Horse, 'code',
#         #         {
#         #             "code": item["HorseCode"],
#         #             "name": item["HorseName"],
#         #             "homecountry": item["Homecountry"],
#         #             "sirename": item["SireName"],
#         #             "damname": item["DamName"],
#         #             "damsirename": item["DamSireName"],
#         #             "importtype": item["ImportType"],
#         #             "countryoforigin": item["CountryofOrigin"],
#         #             "yearofbirth": item["YearofBirth"]
#         #         }, update_existing=True)

#         #     ownerid = yield ownerid
#         #     gearid = yield gearid
#         #     eventtypeid = yield eventtypeid
#         #     horseid = yield horseid

#         #     trackwork = HKTrackwork(
#         #         eventdate=item["EventDate"],
#         #         eventvenue=item["EventVenue"],
#         #         eventdescription=item["EventDescription"],
#         #         # ImportType=item["ImportType"],
#         #         # SireName=item["SireName"],
#         #         # DamName=item["DamName"],
#         #         # DamSireName=item["DamSireName"],
#         #         eventtypeid=eventtypeid,
#         #         ownerid=ownerid,
#         #         gearid=gearid,
#         #         horseid=horseid)

#         #     exists = yield self.scheduler.exists(
#         #         HKTrackwork,
#         #         {
#         #             'eventdate': item["EventDate"],
#         #             'eventdescription': item["EventDescription"],
#         #             'horseid': horseid
#         #         })

#         #     if exists:
#         #         # Consider not to update this record.
#         #         # There are a lot of them
#         #         # If you really need this -
#         #         # Query merging will be needed.
#         #         # It's not very easy to implement
#         #         # as i remember.

#         #         # So if you don't need to update "Trackwork"
#         #         # object - don't update it. Just add new items.
#         #         res = yield self.scheduler.update_if_changed(
#         #             HKTrackwork,
#         #             {
#         #                 'eventdate': item["EventDate"],
#         #                 'eventtypeid': eventtypeid,
#         #                 'horseid': horseid
#         #             },
#         #             {
#         #                 'ownerid': ownerid,
#         #                 'gearid': gearid,
#         #                 'eventvenue': item['EventVenue'],
#         #                 'eventdescription': item['EventDescription'],
#         #             })
#         #     else:
#         #         self.scheduler.save(trackwork)

#         returnValue(item)

# class RpostPipeline(object):

# #     def __init__(self): 
# #         engine = create_engine(URL(**settings.DATABASE))
# #         # create_tables(engine)
# #         create_schema(engine)
# #         self.Session = sessionmaker(bind=engine)
# #         self.cache = defaultdict(lambda: defaultdict(lambda: None))

# #     # write to rd_race
# #     def process_item(self, item, spider):
# #         session = self.Session()

# #         racedays = RPRacedaydump(

# #                     racename = item.get("racename", None),
# #                     racedate= item.get("racedate",None),
# #                     racecoursecode= item.get("racecourse",None),
# #                     Racetime= item.get("racetime",None),
# #                     Racepm= item.get("racepm", None),
# #    					...
# #                 )
# #         try:
# #         # session.add(races)
# #             session.add(racedays)
# #             session.commit()
# #         except:
# #             session.rollback()
# #             raise
# #         finally:
# #             session.close()
# #         return item


# ##UPDATE   tips=response.meta['tips'] comments if racedate is current
# ##tables rd_Race, rd_Runner, rd_Tips
