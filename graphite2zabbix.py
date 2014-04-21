#!/usr/bin/pyhon

import sys
import json
import requests
import os
import time

'''
configuration
'''
ZABBIX_USERNAME='zabbixusername'
ZABBIX_PASSWORD='zabbixpassword'
ZABBIX_HTTP_AUTH='' # ZABBIX_HTTP_AUTH=('username','password') 
ZABBIX_USER_ID='' # find from zabbix administration section, should be number, 1 maybe
ZABBIX_SERVER_CONNECTION='http' # http/https
ZABBIX_SERVER='zabbix.domain.name'
ZABBIX_INSTALLATION_FOLDER='/' # '/zabbix'
ZABBIX_SENDER='/usr/bin/zabbix_sender -vvv'
ZABBIX_SERVER_PORT='10051'
ZABBIX_MONITORED_HOSTNAME='host' # all items will be added this host, create a dummy host as unmonitored 
GRAPHITE_HOST="https://graphite.domain.name/"
GRAPHITE_HTTP_AUTH='' # GRAPHITE_HTTP_AUTH=('username', 'password') 
GRAPHITE_INSTALLATION_FOLDER='/' #/graphite
headers = {'content-type': 'application/json'}
FILE_ITEMS_TMP='/tmp/graphite2zabbix.list'
'''
'''



ZABBIX_API_URL=ZABBIX_SERVER_CONNECTION+'://'+ZABBIX_SERVER+ZABBIX_INSTALLATION_FOLDER+'/api_jsonrpc.php'


def get_zabbix_aut_key():
        payload= {'jsonrpc': '2.0','method':'user.login','params':{'user':ZABBIX_USERNAME,'password':ZABBIX_PASSWORD},'id':ZABBIX_USER_ID}
	try:
	        r = requests.post(ZABBIX_API_URL, data=json.dumps(payload), headers=headers, verify=False,auth=ZABBIX_HTTP_AUTH)
		result=r.text
		if  r.status_code != 200 or ( 'error' in result ) or (type(result) == list):
			print 'error\t: authentication'
			sys.exit()
		else:
			result=json.loads(r.text)
			return result['result']
	except:
		print 'error\t: authentication'
		sys.exit()

def refresh_zabbix_items_cache():
	#get items with graphite application name
	print 'info\t: getting all items with "graphite" application name from zabbix api'
	#get application id
	payload={
	    "jsonrpc": "2.0",
	    "method": "application.get",
	    "params": {
		"output": "extend"
	    },
	    "auth": zabbix_aut_key,
	    "id": ZABBIX_USER_ID
	}
	r = requests.post(ZABBIX_API_URL, data=json.dumps(payload), headers=headers, verify=False,auth=ZABBIX_HTTP_AUTH)
	result=r.text
	if  r.status_code != 200 or ( 'error' in result ) or (type(result) == list):
		print 'error\t: application.get'
		sys.exit()
	else:
		result=json.loads(result)
		for i in result['result']:
			applicationid=0
			if i['name']=='graphite':
				applicationid=i['applicationid']
		if applicationid==0:
			print 'error\t: did you create zabbix item with applicatian name "graphite" ?'
	#get items
	payload={
	    "jsonrpc": "2.0",
	    "method": "item.get",
	    "params": {
		"applicationids": applicationid,
		"output": "extend"
	    },
	    "auth": zabbix_aut_key,
	    "id": ZABBIX_USER_ID
	}
	r = requests.post(ZABBIX_API_URL, data=json.dumps(payload), headers=headers, verify=False,auth=ZABBIX_HTTP_AUTH)
	result=json.loads(r.text)
	if  r.status_code != 200 or ( 'error:"' in result ) or (type(result) == list):
		print 'error: item.get'
		sys.exit()
	else:
		zabbix_items={}
		for i in result['result']:
			zabbix_items[i['itemid']]=i['key_']
		#save file
		file = open(FILE_ITEMS_TMP, "wb")
		file.write(str(zabbix_items))
		file.close()



def read_zabbix_items():
	file = open(FILE_ITEMS_TMP, "r")
	items_dict=file.read()
	file.close()
	items_dict=eval(items_dict)
	return items_dict

def get_graphite_data(key):
        URL=GRAPHITE_HOST+'/'+GRAPHITE_INSTALLATION_FOLDER+'/render?from=-30minutes&until=now&target='+key+'&format=json'
	try:
	        r = requests.get(URL,verify=False,auth=GRAPHITE_HTTP_AUTH)
		if  r.status_code != 200:
			print 'error\t: graphite call failed'
	        	sys.exit()
		else:
			return r.text
	except:
		print 'error\t: graphite call failed'
		sys.exit()

def zabbix_send(key, value):
        value=str(value)
        query=ZABBIX_SENDER+" -z "+ZABBIX_SERVER+" -p "+ZABBIX_SERVER_PORT+" -s '"+ZABBIX_MONITORED_HOSTNAME+"' -k "+key+" -o " +value
        os.system(query)

def main():
	global zabbix_aut_key
	zabbix_aut_key=get_zabbix_aut_key()

	#refresh items cache file every 10 minutes or file doesn't now exist
	minute=time.strftime("%M")
	if ( os.path.isfile(FILE_ITEMS_TMP) != True or minute[-1] == '0'):
		refresh_zabbix_items_cache()

	#get zabbix items from cache file
	print 'info\t: getting all items with "graphite" application name from cache'
	items_dict=read_zabbix_items()
	if(len(items_dict)==0):
		print 'warning\t: 0 item found, skipping'
		sys.exit()
	for id,key in items_dict.items():
		print 'info\t: '+key
		print 'info\t: getting graphite data ('+key+')'
		#get data from graphite
		data=get_graphite_data(key)
		data_json=json.loads(data)
		if len(data_json) == 0:
			print 'warning\t: key could not found at graphite, skipping'
			continue
		last_value=0
		for data in data_json[0]['datapoints']:
			if data[0] is not None:
				last_value=data[0]
		print 'info\t: '+str(last_value)
		#feed zabbix
		print 'info\t: feeding zabbix'
		zabbix_send(key,last_value)
		print '-'

if __name__ == "__main__":
	print '---'
	main()

