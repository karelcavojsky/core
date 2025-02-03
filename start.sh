#!/bin/bash

ORIGIN_DIR=`pwd`
WORKING_DIR=$(dirname "$0")
VIRTUAL_ENV=venv


cd $WORKING_DIR

script/setup
source venv/bin/activate
hass -c config

cd $ORIGIN_DIR
