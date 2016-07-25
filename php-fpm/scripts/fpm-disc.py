#!/usr/bin/env python

import os
import re
import xml.etree.ElementTree as ET
import ConfigParser as CP
import json

class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[asection]\n'

    def readline(self):
        if self.sechead:
            try:
                return self.sechead
            finally:
                self.sechead = None
        else:
            return self.fp.readline()

def detect_conf_file():
    paths = [
              '/etc/php5/fpm/php-fpm.conf',
              '/etc/php-fpm.conf',
              '/etc/php/5.6/fpm/php-fpm.conf',
              '/usr/local/etc/php5/fpm/php-fpm.conf',
              '/usr/local/etc/php/fpm/php-fpm.conf',
              '/usr/local/etc/php/5.5/fpm/php-fpm.conf',
              '/usr/local/etc/php/5.6/fpm/php-fpm.conf',
              '/usr/local/etc/php/7.0/fpm/php-fpm.conf',
              '/usr/local/etc/php-fpm.conf',
              '/etc/php/fpm-php5.3/php-fpm.conf',
              '/etc/php/php-fpm.conf'
              ]
    for p in paths:
        if os.path.isfile(p):
            return p
    return

ini_filename = detect_conf_file()

def get_xml_pools(filename):
    try:
        tree = ET.parse(filename)
    except ET.ParseError:
        return
    pools = []
    workers = tree.find('workers')
    for pool in workers.findall('section'):
        for p in pool.findall('value'):
            if p.attrib == {'name': 'name'}:
                name = p.text
            if p.attrib == {'name': 'listen_address'}:
                listen = p.text
        pools.append({name: listen})
    return pools


def read_ini_file(filename):
    conf = {}
    Config = CP.RawConfigParser()
    try:
        Config.readfp(FakeSecHead(open(filename)))
    except:
        return
    for section in Config.sections():
        conf[section] = dict(Config.items(section))
    return conf



def get_includes(ini_file):
    if ini_file == None:
        return
    includes = []
    try:
        include_str = ini_file['asection']['include']
    except KeyError:
        try:
            include_str = ini_file['global']['include']
        except KeyError:
            return []
    reg = re.compile('\*.*$')
    include_dir = reg.sub('',include_str)
    listdir = os.listdir(include_dir)
    for f in listdir:
        if re.match("[\w\.\-]*\.conf$", f):
            includes.append(include_dir + f)
    return includes

def get_ini_listens(ini_file):
    listens = {}
    Config = CP.RawConfigParser()
    try:
        Config.readfp(FakeSecHead(open(ini_file)))
    except:
        return
    for section in Config.sections():
        if section != 'asection' and section != 'global':
            listens[section] = dict(Config.items(section))['listen']
    return listens

conf_xml = True

listens = []
try:
    xml_pools = get_xml_pools(ini_filename)
    for l in xml_pools:
        listens.append(l)
except:
    xml_pools = []
    conf_xml = False

if not conf_xml:
    ini_file = read_ini_file(ini_filename)
    listens.append(get_ini_listens(ini_filename))
    for i in get_includes(ini_file):
        listens.append(get_ini_listens(i))

zbx_data = []
for l in listens:
    for key, value in l.iteritems():
        zbx_data.append(dict([("{#POOLNAME}", key),("{#LISTEN}", value)]))

zbx_dump = {'data': zbx_data}
print json.dumps(zbx_dump, sort_keys=True, separators=(', ', ": "), indent=4)
