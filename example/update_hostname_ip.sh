#!/bin/bash

set -eu

cd $(dirname $0)
. ./config.sh

readonly INSTANCE_ID=`curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null`
readonly PRIVATEIP=`curl -s http://169.254.169.254/latest/meta-data/local-ipv4|sed -e 's/\./-/g' 2>/dev/null`
readonly BEFORE=`hostname`
readonly AFTER="${PREFIX}-ip-${PRIVATEIP}"

function print_log()
{
        echo "[update_hostname] $1"
}


if [ ${SRC_INSTANCE_ID} = ${INSTANCE_ID} ]; then
  echo "Not change hostname, because this instance is template for AutoScaling [this: ${INSTANCE_ID}, template: ${SRC_INSTANCE_ID}]"
elif [ ${BEFORE} = ${AFTER} ]; then
  echo "Not change hostname [before: ${BEFORE}, after: ${AFTER}]"
else
  echo "Change hostname for AutoScaling [before: ${BEFORE}, after: ${AFTER}]"
  if [ `which hostnamectl` ]; then
    hostnamectl set-hostname ${AFTER}
  else
    hostname ${AFTER} && \
      sed -i -e "s/${BEFORE}/${AFTER}/g" /etc/sysconfig/network && \
      echo -e "\n$(ip route | grep src | awk '{ print $NF }') ${AFTER}" >> /etc/hosts && \
      service zabbix-agent restart && service zabbix-host-register restart
  fi
  echo "Completed update hostname"
fi
