# /usr/bin/env python
# coding: utf-8

class ZabbixConfig:
    ZABBIX_API_URL = "http://your-zabbix.local/zabbix/api_jsonrpc.php"
    HEADERS = {
        "Content-Type": "application/json"
    }
    USER = "Admin"
    PASSWORD = "zabbix"
