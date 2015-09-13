#!/bin/bash

# using pip and virtualenv
sudo apt-get -y install python-pip python-virtualenv python-dev libxml2-dev libxslt-dev libssl-dev libffi-dev libpq-dev

virtualenv --no-site-packages --python=python2.7 env
env/bin/pip install -r requirements.txt

docker run --name raceday-postgres -v $PWD/db:/var/lib/postgresql/data -p 5432:5432 -e POSTGRES_PASSWORD='' -e POSTGRES_USER=vmac -d postgres

docker run -it --link raceday-postgres:postgres --rm postgres sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U vmac  -c "CREATE DATABASE hkraces_aug15 OWNER vmac;"'

