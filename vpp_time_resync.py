#!/usr/bin/python2

import os
import sys
import csv
import scapy.all

base_path = sys.argv[1]
os.chdir(base_path)

class Quic(scapy.all.Packet):
	name = "IETF QUIC"
	fields_desc = [ scapy.all.XByteField("type", 0),
				    scapy.all.XLongField("conn_id", 0),
				    scapy.all.IntField("pn", 0),
				    scapy.all.ConditionalField(scapy.all.XIntField("version", 0), lambda pkt:pkt.type & 0x80)]


zero_epoch = None

class Pcaptrace():
	def __init__(self, filename, count=-1):
		print("Reading packets ...")
		self.packets = scapy.all.rdpcap(filename, count=count)
		print(" Done")
		self.cursor = 0
		self.zero_epoch = self.packets[0].time

	def read_next_packet(self):
		full_packet = self.packets[self.cursor]
		self.cursor += 1
		return Quic(full_packet["Raw"].load)

	def forward_to_pn(self, pn):
		packet = self.read_next_packet()
		while packet.pn != pn:
			self.read_next_packet()
		return packet

pcap = Pcaptrace("switch-2_tcpdump.pcap", -1)

csv_infile = open("switch-2_vpp.csv", 'rb')
csv_in = csv.DictReader(csv_infile, skipinitialspace=True)

csv_outfile = open("switch-2_vpp_resync.csv", 'wb')
csv_out = csv.DictReader(csv_outfile, csv_in.fieldnames)



for row in csv_in:
	pn = row['pn']
	packet = pcap.forward_to_pn(pn)
	time = packet.time - pcap.zero_epoch
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
