#!/usr/bin/python2

import os
import sys
import os.path

base_path = sys.argv[1]
os.chdir(base_path)

if not os.path.isfile("switch-2_vpp.csv"):
	print("\tNo VPP file")
	sys.exit(11)
if os.path.isfile("switch-2_mbytes.csv"):
	sys.exit(10)
print("\tNeeds extracting")

import csv
import scapy.all


class Quic(scapy.all.Packet):
	name = "IETF QUIC"
	fields_desc = [ scapy.all.XByteField("type", 0),
				    scapy.all.XLongField("conn_id", 0),
				    scapy.all.IntField("pn", 0),
				    scapy.all.ConditionalField(scapy.all.XIntField("version", 0), lambda pkt:pkt.type & 0x80),
				    scapy.all.XByteField("measurement", 0),]
zero_epoch = None


print("\tReading packets ...")
packets = scapy.all.rdpcap("switch-2_tcpdump.pcap", count=-1)
print("\t\tDone (1)")

print("\tProcessing packets")
zero_epoch = packets[0].time

FIELDNAMES = ("time", "pn", "host", "measurement")

csv_outfile = open("switch-2_mbytes.csv", 'wb')
csv_out = csv.DictWriter(csv_outfile, FIELDNAMES)
header = dict()
for field in FIELDNAMES:
	header[field] = field
csv_out.writerow(header)

for packet in packets:
	row = dict()
	row['time'] = packet.time - zero_epoch
	if packet["UDP"].sport == 4433:
		row['host'] = "server"
	else:
		row['host'] = "client"
	quic = Quic(packet["Raw"].load)
	row['pn'] =  quic.pn
	row['measurement'] = quic.measurement
	csv_out.writerow(row)

print("\t\tDone (2)")
