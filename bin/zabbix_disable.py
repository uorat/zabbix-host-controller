#!/usr/bin/env python
# coding: utf-8

from zabbix_module import ZabbixApi
from socket import gethostname

hostname = gethostname()
zabbix = ZabbixApi()
authid = zabbix.login()
hostid = zabbix.get_hostid(authid, hostname)

zabbix.disable_host(authid, hostid)

# check
zabbix.get_hostid(authid, hostname)
