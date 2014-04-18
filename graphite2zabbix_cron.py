#!/usr/bin/pyhon

import sys
import json
import requests
import os
from time import sleep


GRAPHITE_HOST="http://domain.com/graphite"
ZABBIX_HOST='http://domain.com/zabbix/'
ZABBIX_PORT='10051'
ZABBIX_HOSTNAME='hostname1'
ZABBIX_SENDER='/usr/local/sbin/zabbix_sender'

def get_data(uri):
        URL=GRAPHITE_HOST+uri
        r = requests.get(URL)
        return r.json()

def zabbix_send(key, value):
        value=str(value)
        query=ZABBIX_SENDER+" -z "+ZABBIX_HOST+" -p "+ZABBIX_PORT+" -s '"+ZABBIX_HOSTNAME+"' -k "+key+" -o " +value
        os.system(query)
        sleep(0.5)

#sample1, get last data from graphite
key='hosname.key'
uri='/render?from=-30minutes&until=now&target=+'key+'&format=json'
result=get_data(uri)
for datas in result[0]['datapoints']:
	if datas[0] is not None:
		data=datas[0]
		continue
zabbix_send(key,int(data))

