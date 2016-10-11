#!/bin/bash

set -eu

cd $(dirname $0)
. ./config.sh

readonly INSTANCE_ID=`curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null`
readonly BEFORE=`hostname`
readonly AFTER="${PREFIX}-${INSTANCE_ID}"

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
  hostnamectl set-hostname ${AFTER}
  [[ -f /etc/motd ]] && sed -i -e "s/${BEFORE}/${AFTER}/g" /etc/motd
fi
