#!/usr/bin/env python
# coding: utf-8

from zabbix_module  import ZabbixApi
from socket import gethostname, gethostbyname

hostname  = gethostname()
ipaddress = gethostbyname(hostname)
zabbix    = ZabbixApi()
authid    = zabbix.login()

is_exist = zabbix.is_exists(authid, hostname)
if is_exist:
    print "already exist, so enable status [hostid: {hostid}, hostname: {hostname}]".format(
        hostid    = is_exist,
        hostname  = hostname
    )
    hostid = zabbix.get_hostid(authid, hostname)
    zabbix.enable_host(authid, hostid)
    hostid = zabbix.get_hostid(authid, hostname)
else:
    group_ids = zabbix.get_hostgroups(authid, hostname)
    template_ids  = zabbix.get_templates(authid, hostname)
    macros = zabbix.get_macros(hostname)
    result = zabbix.create_host(authid, hostname, ipaddress, group_ids, template_ids, macros)
    print result

    hostid = zabbix.get_hostid(authid, hostname)
    print "completed registrasion to zabbix [hostid: {hostid}, hostname: {hostname}]".format(
        hostid    = hostid,
        hostname  = hostname
    )
    hostid = zabbix.get_hostid(authid, hostname)
