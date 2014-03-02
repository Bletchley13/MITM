#!/bin/sh

if [ "$USER" != "root" ]; then
	echo "You must be ROOT to execute the shell"
	exit 1
fi

if [ "$1" = "" ]; then
	echo "You need to specify the target port of your MITM server"
	echo "Usage: $0 port_of_your_MITM_server"
	exit 1
fi

echo "1" > /proc/sys/net/ipv4/ip_forward

iptables -F
iptables -t nat -F

iptables -I FORWARD -i vboxnet0 -o vboxnet0 -j ACCEPT
iptables -I FORWARD -i vboxnet0 -s 192.168.56.0/24 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -I FORWARD -o vboxnet0 -d 192.168.56.0/24 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -t nat -I POSTROUTING -s 192.168.56.0/24 ! -d 192.168.56.0/24 -j MASQUERADE
iptables -t nat -I PREROUTING  -i vboxnet0 -p tcp -m multiport --dports 80,443 -j REDIRECT --to-port $1
