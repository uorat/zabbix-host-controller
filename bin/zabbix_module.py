#!/usr/bin/env python
# coding: utf-8

import json
import re
import urllib2
import socket
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../conf')
from zabbix_config import ZabbixConfig

class ZabbixApi:
    """ Module of Zabbix."""

    def login(self):
        """ Login and get authid.

        Returns:
            authid (string): authenticated uid.
        """
        param = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                "user": ZabbixConfig.USER,
                "password": ZabbixConfig.PASSWORD
            },
            "id": 0
            }
        )
        response = self.__execute_zabbix_api(param)
        return response['result']

    def enable_host(self, authid, hostid):
        """ enable host status

        Params:
            authid (string): authenticated uid.
            hostid (int): hostname for filter
            status (int) Status of host
                - 0: enable
                - 1: disable
                - 2: impossible

        Returns:
            True || False
        """
        return self.__update_host_status(authid, hostid, 0)

    def disable_host(self, authid, hostid):
        """ disable host status

        Params:
            authid (string): authenticated uid.
            hostid (int): hostname for filter
            status (int) Status of host
                - 0: enable
                - 1: disable
                - 2: impossible

        Returns:
            True || False
        """
        return self.__update_host_status(authid, hostid, 1)

    def create_host(self, authid, hostname, ip, group_ids, template_ids, macros = None):
        """ create (Register) host

        Params:
            authid        (string)    : authenticated uid.
            hostname      (string)    : hostname for registering zabbix.
            ip            (string)    : ip address
            group_ids     ([integer]) : list of zabbix host group id
            template_ids  ([integer]) : list of zabbix template id
            macros        (dict)      : zabbix user macros

        Returns:
            True || False

        Refs:
            https://www.zabbix.com/documentation/2.4/manual/api/reference/usermacro/object#hosttemplate_level_macro
        """
        return self.__create_host(authid, hostname, ip, group_ids, template_ids, macros)

    def is_exists(self, authid, hostname):
        """Check exist from hostname.

        Params:
            authid (string): authenticated uid.
            hostname (string): hostname for filter

        Returns:
            True|False
        """
        hosts = self.__get_hostids(authid, hostname)
        return hosts[0] if hosts else False

    def get_hostid(self, authid, hostname):
        """Get hostid.

        Params:
            authid (string): authenticated uid.
            hostname (string): hostname for filter

        Returns:
            hostid (int): host id.
        """
        return self.__get_hostids(authid, hostname)[0]

    def get_hostgroups(self, authid, hostname):
        """ get hostgroup ids from hostname pattern

        Params:
            authid        (string)    : authenticated uid.
            hostname      (string)    : hostname for registering zabbix.

        Returns:
            ([integer])
        """
        hostgroup_ids = []

        zbx_hostgroup = ZabbixConfig.ZABBIX_HOSTGROUP_MAPPING.get(self.__get_group(hostname))
        if zbx_hostgroup is not None:
            for hostgroup in zbx_hostgroup:
                hostgroup_ids.append(self.__get_hostgroupids(authid, hostgroup)[0])

        env_group = ZabbixConfig.ZABBIX_HOSTGROUP_MAPPING.get(self.__get_environment(hostname))
        if env_group is not None:
            for hostgroup in env_group:
                hostgroup_ids.append(self.__get_hostgroupids(authid, hostgroup)[0])

        return hostgroup_ids

    def get_macros(self, hostname):
        """ get macros [key/value] from hostname
        """
        group = self.__get_group(hostname)
        macros = []
        if self.__get_macro(group): macros.extend(self.__get_macro(group))
        if self.__get_macro(hostname): macros.extend(self.__get_macro(hostname))
        return macros if len(macros) > 0 else None

    def get_templates(self, authid, hostname):
        """ get template ids from hostname pattern
        """
        group = self.__get_group(hostname)
        templates = ZabbixConfig.ZABBIX_TEMPLATE_MAPPING.get(group)
        template_ids = []
        for template in templates:
            template_ids.append(self.__get_templateids(authid, template)[0])
        return template_ids

    def __get_group(self, hostname):
        """ get group name from hostname
        """
        return ZabbixConfig.GROUP_MAPPING.get(re.sub('\d+', '', hostname))

    def __get_macro(self, key):
        """ get macros [key/value] from key
        """
        return ZabbixConfig.ZABBIX_MACRO_MAPPING.get(key)

    def __get_environment(self, hostname):
        """ get environment from hostname pattern
        """
        r = re.compile('-*(prd|stg|dev)-')
        match = r.search(hostname)
        return match.group(1) if match else None

    def __execute_zabbix_api(self, param, headers = ZabbixConfig.HEADERS):
        """ Execute zabbix api (request and get response).

        Args:
            param (string): JSON Parameter.
            header: HTTP Header.

        Returns:
            response (string): JSON data.
        """
        request = urllib2.Request(ZabbixConfig.ZABBIX_API_URL, param)
        for key in headers:
           request.add_header(key, headers[key])
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        return response

    def __get_hostids(self, authid, hostname):
        """Get list of hostid.  """
        param = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": "extend",
                    "filter": {
                       "name":[ hostname ]
                    }
                },
                "auth": authid,
                "id": 1
            }
        )
        response = self.__execute_zabbix_api(param)
        hosts = []
        for result in response['result']:
           # set hostgrup-id
           hosts.append(result['hostid'])
           self.__log_info("host: {host}, hostid: {hostid}, status: {status} ".format(
                   host = result['host'],
                   hostid = result['hostid'],
                   status = result['status']))
        return hosts

    def __get_hostgroupids(self, authid, groupname):
        """Get list of groupid.
        """
        param = json.dumps(
            {
               "jsonrpc": "2.0",
               "method": "hostgroup.get",
               "params": {
                  "output": "extend",
                  "filter": {
                     "name":[ groupname ]
                  }
               },
                "auth": authid,
                "id": 1
            }
        )
        response = self.__execute_zabbix_api(param)
        groups = []
        for result in response['result']:
          # set hostgrup-id
          groups.append(result['groupid'])
          self.__log_info("name: {name}, groupid: {groupid} ".format(
                  name = result['name'],
                  groupid = result['groupid']))
        return groups

    def __get_templateids(self, authid, template):
        """Get list of templateid.
        """
        param = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "template.get",
                "params": {
                    "output": "extend",
                    "filter": {
                        "host": [ template ]
                    }
                },
                "auth": authid,
                "id": 1
            }
        )
        response = self.__execute_zabbix_api(param)
        templates = []
        for result in response['result']:
          templates.append(result['templateid'])
          self.__log_info("name: {name}, templateid: {templateid} ".format(
                  name = result['name'],
                  templateid = result['templateid']))
        return templates

    def __create_host(self, authid, hostname, ip, group_ids, template_ids, macros):
        """ register host on zabbix.
        """
        groups = map(lambda x: { "groupid": x }, group_ids)
        templates = map(lambda x: { "templateid": x }, template_ids)
        data = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostname,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": groups,
                "templates": templates,
            },
            "auth": authid,
            "id": 1
        }
        if macros is not None: data['params'].update({ "macros": macros })
        param = json.dumps(data)
        print param
        response = self.__execute_zabbix_api(param)
        return response['result']

    def __update_host_status(self, authid, hostid, status):
        """Update host status

        Params:
            authid (string): authenticated uid.
            hostid (int): hostname for filter
            status (int) Status of host
                - 0: enable
                - 1: disable
                - 2: impossible

        Returns:
            True || False
        """
        if not isinstance(status, int):
            raise TypeError( "status should set int (status = {0})".format(status) )
        param = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.update",
                "params": {
                    "hostid": hostid,
                    "status": status
                },
                "auth": authid,
                "id": 1
            }
        )
        response = self.__execute_zabbix_api(param)
        result = response['result']['hostids'][0] == hostid
        self.__log_info("status update : hostid: {hostid}, result: {result} ".format(
            hostid = hostid, result = result))
        return result

    def __log_info(self, msg = ""):
        print "   => {0}".format(msg)

