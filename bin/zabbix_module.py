# /usr/bin/env python
# coding: utf-8

import json
import urllib2
import socket
from zabbix_config import ZabbixConfig

class ZabbixApi:
    """ Module of Zabbix."""

    ZABBIX_API_URL = ZabbixConfig.ZABBIX_API_URL
    HEADERS = ZabbixConfig.HEADERS
    USER = ZabbixConfig.USER
    PASSWORD = ZabbixConfig.PASSWORD

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
                "user": self.USER,
                "password": self.PASSWORD
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

    def get_hostid(self, authid, hostname):
        """Get hostid.

        Params:
            authid (string): authenticated uid.
            hostname (string): hostname for filter

        Returns:
            hostid (int): host id.
        """
        return self.__get_hostids(authid, hostname)[0]


    def __execute_zabbix_api(self, param, headers = HEADERS):
        """ Execute zabbix api (request and get response).

        Args:
            param (string): JSON Parameter.
            header: HTTP Header.

        Returns:
            response (string): JSON data.
        """
        request = urllib2.Request(self.ZABBIX_API_URL, param)
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

