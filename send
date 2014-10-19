#!/bin/bash

SUBJ="IP Changed"
EMAIL="juansantiago.medina@gmail.com"

ip1=""
ip2=""

read ip1 < ip.txt
ip2=$(wget -qO- ifconfig.me/ip)

if [ "$ip1" = "$ip2" ]
then
	exit
else
	python /home/pi/ecan_recognition/IP/upload_ecan.py "$ip2"
	echo "$ip2" > ip.txt
	echo "$ip2" | mail -s $SUBJ $EMAIL
	exit
fi
