graphite2zabbix
===============

A small script to get data from graphite and put them to zabbix server 

USAGE
- edit conf section at the script
- add zabbix trapper item at zabbix server
	- item type has to be 'Zabbix Trapper'
	- item key has to be same with graphite key, like 'web.host1.diskusage', you can choise different item name
	- Application has to be 'graphite'
	- add cron entry like this;
		\* * * * * python graphite2zabbix.py  >> /tmp/graphite2zabbix.log.log 2>&1
	- that's all :)
	- it refresh items list every 10 minutes, be patient

REQUIREMENT
- zabbix sender
- python modules
	- sys
	- json
	- requests
	- os
	- time

NOTES
- to reduce zabbix api call, it creates a item cache file and refresh it every 10 minutes
