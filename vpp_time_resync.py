#!/usr/bin/python2

import os
import sys
import os.path

base_path = sys.argv[1]
os.chdir(base_path)

if not os.path.isfile("switch-2_vpp.csv"):
	print("\tNo VPP file")
	sys.exit(11)
if os.path.isfile("switch-2_vpp_resync.csv"):
	sys.exit(10)
print("\tNeeds resyncing")

import csv
import scapy.all


class Quic(scapy.all.Packet):
	name = "IETF QUIC"
	fields_desc = [ scapy.all.XByteField("type", 0),
				    scapy.all.XLongField("conn_id", 0),
				    scapy.all.IntField("pn", 0),
				    scapy.all.ConditionalField(scapy.all.XIntField("version", 0), lambda pkt:pkt.type & 0x80)]
zero_epoch = None




print("\tReading packets ...")
packets = scapy.all.rdpcap("switch-2_tcpdump.pcap", count=-1)
print("\t\tDone")


print("\tMaking hashmap")
zero_epoch = packets[0].time

pn_to_time = dict()

for packet in packets:
	time = packet.time - zero_epoch
	if packet["UDP"].sport == 4433:
		host = "server"
	else:
		host = "client"
	pn =  Quic(packet["Raw"].load).pn

	pn_to_time[(pn, host)] = time
#	print("adding pn:{}, host:{}".format(pn, host))

print("\t\tone")

csv_infile = open("switch-2_vpp.csv", 'rb')
csv_in = csv.DictReader(csv_infile, skipinitialspace=True)

csv_outfile = open("switch-2_vpp_resync.csv", 'wb')
csv_out = csv.DictWriter(csv_outfile, csv_in.fieldnames)
header = dict()
for field in csv_in.fieldnames:
	header[field] = field
csv_out.writerow(header)

for row in csv_in:
	pn = int(row['pn'])
	host = row['host'].strip()
	try:
		time = pn_to_time[(pn, host)]
	except KeyError:
		print("\tpacket not found. BAD! pn:{}, host:{}".format(pn, host))
		sys.exit(1)
	row['time'] = time
	csv_out.writerow(row)

#for packet in pcap_packets:
	#if not zero_epoch:
		#zero_epoch = packet.time

	#time = packet.time - zero_epoch
	#quic = Quic(packet["Raw"].load)
	#print("{:3.3}: {}".format(time, quic.pn))
	##print(len(quic_packet.load))


#for packet in pcap_packets:
	#if not zero_epoch:
		#zero_epoch = packet.time

	#time = packet.time - zero_epoch
	#quic = Quic(packet["Raw"].load)
	#print("{:3.3}: {}".format(time, quic.pn))
	##print(len(quic_packet.load))
