#!/usr/bin/python3

import scapy.all
import os
import os.path
import shutil
import sys
import collections
import matplotlib.pyplot as plt

SCAPY_DONE_STRING = "scapy_done_1"

def save_figure(figure, filename):
	print("Generating figure:", filename, "...", end=" ")
	figure.savefig("{}.pdf".format(filename))
	figure.savefig("{}.png".format(filename))
	pickle.dump(figure, open("{}.fig.pickle".format(filename), 'wb'))
	print("Done")

base_path = sys.argv[1]
os.chdir(base_path)

if os.path.exists(SCAPY_DONE_STRING):
	print("Post analysys already done. Goodbye.")
	sys.exit(1)

PLOT_DIR = "scapy/"
if os.path.exists(PLOT_DIR):
	shutil.rmtree(PLOT_DIR)
os.mkdir(PLOT_DIR)

pcap_packets = scapy.all.rdpcap("switch-2_tcpdump.pcap", count=-1)

zero_epoch = None
pps_buffer = collections.deque()
pps_count = list()
pps_times = list()

pre60_count = 0
post60_count = 0

for packet in pcap_packets:
	if not zero_epoch:
		zero_epoch = packet.time

	relative_packet_time = packet.time - zero_epoch

	##
	## PACKETS PER SECOND
	##

	# add packet to pps pps_buffer
	pps_buffer.append(packet)

	# remove packets that moved out of the window
	while packet.time - pps_buffer[0].time > 1:
		pps_buffer.popleft()

	pps_count.append(len(pps_buffer))
	pps_times.append(relative_packet_time)

	##
	## PACKETS BEFORE / AFTER 60s MARK
	##

	if relative_packet_time < 60:
		pre60_count += 1
	else:
		post60_count += 1

with open(PLOT_DIR + "count.txt", 'w') as outfile:
	infostring = "pre/post 60 count: {}/{}".format(pre60_count, post60_count)
	print(infostring)
	outfile.write(infostring + '\n')

plt.plot(pps_times, pps_count)
plt.grid()
plt.savefig(PLOT_DIR + "/pps")
