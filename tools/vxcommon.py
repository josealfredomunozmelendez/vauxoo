# !/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import os
import pprint
import logging
import json
import psycopg2
import odoorpc
from import_data import Migration
from import_data import conect_and_login


logging.addLevelName(
    logging.ERROR,
    "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(
    logging.INFO,
    "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName(
    logging.WARNING,
    "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(
    logging.DEBUG,
    "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName(
    logging.CRITICAL,
    "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))

_logger = logging.getLogger('vxcommon')
_logger.setLevel(logging.DEBUG)
CH_VAR = logging.StreamHandler()
CH_VAR.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
CH_VAR.setFormatter(FORMATTER)
_logger.addHandler(CH_VAR)


def prepare_connection(config):
    """ Connect to both instances legacy and new and create a migration object
    in order to make easier the export and loads.
    """
    legacy = conect_and_login(
        config.get('legacy_host'),
        config.get('legacy_port'),
        config.get('legacy_db'),
        config.get('legacy_user'),
        config.get('legacy_pwd'))
    new = conect_and_login(
        config.get('nhost'),
        config.get('nport'),
        config.get('ndb'),
        config.get('nuser'),
        config.get('npwd'))

    cursor = conect_and_login(
        config.get('dbhost'),
        config.get('dbport'),
        config.get('ndb'),
        config.get('dbuser'),
        config.get('dbpwd'),
        False)

    return Migration(
        legacy, new, cursor, config.get('workers')-1 or 1, 100)


def connect():
    configfile = os.path.expanduser('~/.vxmigration')
    with open(configfile, 'r') as configfile:
        config = json.loads(configfile.read())

    _logger.info("Configuration used %s", configfile)
    _logger.info(pprint.pformat(config))

    return prepare_connection(config)
