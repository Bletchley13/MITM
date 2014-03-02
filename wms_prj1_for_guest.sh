#!/bin/sh

if [ "$USER" != "root" ]; then
	echo "You must be ROOT to execute the shell"
	exit 1
fi

ifconfig eth0 down
ifconfig eth0 up
ifconfig eth0 192.168.56.123 netmask 255.255.255.0
route add default gw 192.168.56.1

echo "" >> /etc/resolv.conf
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
