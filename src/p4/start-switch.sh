#!/bin/bash

P4_FILE_PREFIX="switch-int"
if [[ "$#" == "1" ]]; then
	P4_FILE_PREFIX=$(basename "$1" .p4)
fi

VETH="veth-mi"


function setup_nic(){
	NAME=$1
	# remove old if existing
	sudo ip link del "$NAME"
	# create a dummy NIC
	sudo ip link add "$NAME" type dummy
	# set its mac address
	#sudo ip link set dev "$NAME" address "$MAC"
	# disable TCP offload to avoid incorrect checksum
	sudo ethtool -K "$NAME" tso off gso off gro off tx off
	# disable ipv6 to avoid being disturbed by other probe services
	sudo sysctl "net.ipv6.conf.$NAME.disable_ipv6=1"
	# take it up
	sudo ip link set dev "$NAME" up
}

# 2 NICs in-out and 3rd NIC for INT
#
# pkt ===> VETH-0 [((( BMv2 P4 switch )))] VETH-1 ===>
#                        *
#                        *
#                      VETH-mon
setup_nic "$VETH-0"   # 1st port of the P4 switch
setup_nic "$VETH-1"   # 2th port of the P4 switch
setup_nic "$VETH-int" # CPU port of the P4 switch (to receive INT packets)

# thrift port to config BMv2
THRIFT_PORT=9090
function conf_switch(){
	simple_switch_CLI --thrift-port "$THRIFT_PORT"
}

function config_int(){
	echo "Configure INT"
	echo "table_add tb_int_config_transit set_transit => 1" | conf_switch
	#do INT on any packet
	echo "table_add tb_int_config_source set_source 0.0.0.0&&&0x00000000 0000&&&0x0000 0.0.0.0&&&0x00000000 0000&&&0x0000 => 4 10 0xFFFF 0" | conf_switch
	#echo "table_add tb_int_config_sink set_sink 1 => 3" | simple_switch_CLI
	echo "mirroring_add 1 3" | conf_switch
	echo
	echo "P4 switch is ready"
	echo
}

set -e

# compile P4 code
p4c --target bmv2 --arch v1model "$P4_FILE_PREFIX.p4" 

# run configuration in the future (3 seconds are enough to start BMv2)
(sleep 3 && config_int )&

DEBUG="--log-level info --pcap=./ --log-console"
DEBUG="--log-level error --log-console"
#DEBUG=""


# start BMv2 switch
exec sudo simple_switch -i "1@$VETH-0" -i "2@$VETH-1" -i "3@$VETH-int" --thrift-port "$THRIFT_PORT" $DEBUG  "$P4_FILE_PREFIX.json"

#echo start client
#sudo ip netns exec client ../client-server/client 1.1.1.1 5000