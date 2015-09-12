
_instructions_

gets raceday information HK

Install: . bootstrap.sh

docker run --name raceday-postgres -v $PWD/db:/var/lib/postgresql/data -p 5432:5432 -e POSTGRES_PASSWORD='' -e POSTGRES_USER=vmac -d postgres
docker run -it --link raceday-postgres:postgres --rm postgres sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U vmac -d hkraces_aug15'

Start spider: cd racedaylive ../env/bin/scrapy crawl race -a racedate=20150513 -a coursecode=HV -a historical=0 (or 1)


##TODO

## PIPELINE
* reflects existing tables - no new table creation
* updates RD -> RA --> H J T O RU

* Upon entry storedwrite stats to extendedraceday table

## SCRAPY 
* deploy to cloud and run periodically


#TODO

1 GITHUB update
2 raceindex 1st item
3 pipeline 


###To add

LSW?
CD RUNNINGPOSITION runningstyle

average speed 0-F CD,

[LBW_L123]
[SP_L123]
[LBW_LCSD]
[RP_LCSD]

PACE POINTS


AWD,
RUNNING_POS_CSD  

DRAW_PERFORMANCE
todaysdraw, winsthisdraw versus winswidedraw? 


### Else:

1 pace use DB
2 Class/Form/Pace DB
2 2YO/Career/Progeny/Owner/T/J DB

D, L3, MIN, AVG, thisGoing

[AVG0-FPACE_SD]


Each Race has pace points number 6+ also the actual speed vs. standard and racetype- sit/sprint  