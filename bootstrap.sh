#!/bin/bash

# using pip and virtualenv
sudo apt-get -y install python-pip python-virtualenv python-dev libxml2-dev libxslt-dev libssl-dev

virtualenv --no-site-packages --python=python2.7 env
env/bin/pip install -r requirements.txt

