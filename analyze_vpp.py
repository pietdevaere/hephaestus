#!/usr/bin/python3
import matplotlib.pyplot as plt
from matplotlib.markers import *
import sys
import csv
import math
import collections
import pickle
import copy
import functools
import numpy as np
import os
import os.path
import shutil
import scapy.all

INVALID_SPIN_COLOR = "#ff69b450"

###
### Helper functions
###

def save_figure(figure, filename):
	print("Generating figure:", filename, "...", end=" ")
	figure.savefig("{}.pdf".format(filename))
	figure.savefig("{}.png".format(filename))
	pickle.dump(figure, open("{}.fig.pickle".format(filename), 'wb'))
	print("Done")

def forward_cursor_to_time(cursor, time, time_series):
	if time_series[0] >= time:
		return -1

	while (cursor < (len(time_series) - 1) and time_series[cursor + 1] < time):
		cursor = cursor + 1

	return cursor


def interpollate_rtts(target_times, source_times, source_rtts):
	target_rtts = list()
	source_cursor = 0

	target_times.sort()
	for time in target_times:
		assert(time != None)

		# First seek to the right point in the array
		source_cursor = forward_cursor_to_time(source_cursor, time, source_times)

		# If we are at the first element in the array
		if source_cursor == -1:
			target_rtts.append(source_rtts[0])
			continue

		# If we are at the last element of the array
		if source_cursor == len(source_times) - 1:
			target_rtts.append(source_rtts[-1])
			continue

		# Otherwise, we have to do some interpollation
		time_delta = source_times[source_cursor + 1] - source_times[source_cursor]
		rtt_delta = source_rtts[source_cursor + 1] - source_rtts[source_cursor]
		slope = rtt_delta / time_delta

		offset = time - source_times[source_cursor]
		interpollated_rtt = source_rtts[source_cursor] + offset * slope
		target_rtts.append(interpollated_rtt)

	return target_rtts



###
### Do some bookkeeping, ensure that all is okey before we start
###

## point this script at a directory
base_path = sys.argv[1]

## We verify that this directory has been VPP analyzed before
os.chdir(base_path)
if not os.path.exists("vpp_done"):
	print("Not analyzed by VPP yet. Goodbye.")
	sys.exit(1)

## clean up data from previous runs
PLOT_DIR = "plots/"
if os.path.exists(PLOT_DIR):
	shutil.rmtree(PLOT_DIR)
os.mkdir(PLOT_DIR)

analyzer_names = ["basic", "pn", "pn_valid", "two_bit", "stat_heur", "rel_heur"]
num_of_analyzers = len(analyzer_names)

vpp_data = list()

###
### read out the vpp data
###

with open("switch-2_vpp.csv", newline='') as csvfile:
	reader = csv.DictReader(csvfile, skipinitialspace=True)
	base_time = None
	for row in reader:
		if base_time == None:
			base_time = float(row["time"])

		vpp_entry = collections.defaultdict(lambda: None)
		vpp_entry["time"] = float(row["time"]) - base_time
		vpp_entry["pn"] = int(row["pn"])
		vpp_entry["host"] = row["host"]

		for analyzer in analyzer_names:
			if row[analyzer + "_new"] == '1':
				vpp_entry[analyzer] = float(row[analyzer + "_data"]) * 1000

		vpp_data.append(vpp_entry)

###
### figure out what the zero epoch time is
###

pcap_packets = scapy.all.rdpcap("switch-2_tcpdump.pcap", count=1)
zero_epoch = pcap_packets[0].time

print("zero_epoch: {}".format(zero_epoch))

###
### Read out the client, server and ping times
###

# The client
client_rtts = list()
client_times = list()
client_rtts_TCP = list()
client_times_TCP = list()

with open("client-0_minq_stderr.txt") as client_log:
	for raw_line in client_log:
		if raw_line.find("RTT:") != -1:
			line = raw_line.split()
			rtt = float(line[-1])
			epoch = float(line[-5])
			time = epoch - zero_epoch
			client_rtts.append(rtt)
			client_times.append(time)
		if raw_line.find("RTT_TCP:") != -1:
			line = raw_line.split()
			rtt = float(line[-1])
			epoch = float(line[-5])
			time = epoch - zero_epoch
			client_rtts_TCP.append(rtt)
			client_times_TCP.append(time)

# The server
server_rtts = list()
server_times = list()
server_rtts_TCP = list()
server_times_TCP = list()

with open("server-0_minq_stderr.txt") as server_log:
	for raw_line in server_log:
		if raw_line.find("RTT:") != -1:
			line = raw_line.split()
			rtt = float(line[-1])
			epoch = float(line[-5])
			time = epoch - zero_epoch
			server_rtts.append(rtt)
			server_times.append(time)

		if raw_line.find("RTT_TCP:") != -1:
			line = raw_line.split()
			rtt = float(line[-1])
			epoch = float(line[-5])
			time = epoch - zero_epoch
			server_rtts_TCP.append(rtt)
			server_times_TCP.append(time)

# Ping
ping_rtts = list()
ping_times = list()
with open("client-0_ping_stdout.txt") as ping_log:
	for raw_line in ping_log:
		if raw_line.startswith("["):
			line = raw_line.split()
			rtt = float(line[-2][5:])
			epoch = float(line[0][1:-1]) # cut of the brackets
			time = epoch - zero_epoch
			ping_rtts.append(rtt)
			ping_times.append(time)

###
### Make plot of all analyzers
###
to_plot = analyzer_names
f, axarr = plt.subplots(len(to_plot))
f.set_size_inches(20, 13)

axarr[0].set_title("Comparison of spin analyzers".format())

min_x_val = math.inf
max_x_val = -math.inf
# plot the data
for i in range(len(to_plot)):
	analyzer_name = analyzer_names[i]
	axes = axarr[i]

	y_values_analyzer = [ x[analyzer_name] for x in vpp_data ]
	x_values_analyzer = [ x["time"] for x in vpp_data ]
	rejected_x_values = [ x["time"] for x in vpp_data if x[analyzer_name] == None ]
	rejected_y_values = [ 35 for x in range(len(rejected_x_values)) ]

	min_x_val = min(min_x_val, min(x_values_analyzer))
	max_x_val = max(max_x_val, max(x_values_analyzer))

	client_line = axes.plot(client_times, client_rtts,
			label="client_estimate", linewidth = .5)
	server_line = axes.plot(server_times, server_rtts,
			label="server_estimate", linewidth = .5)
	ping_line = axes.plot(ping_times, ping_rtts,
			label="ping", linewidth = .5)

	analyzer_line = axes.plot(x_values_analyzer, y_values_analyzer, label=analyzer_name, linewidth = .5)
	rejected_marks = axes.plot(rejected_x_values, rejected_y_values, 'rx')

	axes.set_ylim([30, 120])
	axes.grid()
	axes.legend(loc = 2)

# set the x axes limits
for axes in axarr:
	axes.set_xlim([min_x_val, max_x_val])

save_figure(plt.gcf(), PLOT_DIR + "/all_analyzers")

print([min_x_val, max_x_val])

###
### Interpollate the client estimates to the sample points of the analyzer
###

client_interpol_times = [x['time'] for x in vpp_data]

client_interpol_rtts = interpollate_rtts(client_interpol_times, client_times, client_rtts)

plt.figure()

plt.plot(client_interpol_times, client_interpol_rtts, 'x', label="interpollated")
plt.plot(client_times, client_rtts, '*', label="original")


save_figure(plt.gcf(), PLOT_DIR + "/interpollated_client")

###
### Add this data to the vpp_data data structure
###

for i in range(len(vpp_data)):
	vpp_data[i]['client'] = client_interpol_rtts[i]

# for myself not to use these anymore
del(client_interpol_rtts)
del(client_interpol_times)

###
### plot correlation
###

plt.figure()
plt.plot([ x["client"] for x in vpp_data ], [ x["pn_valid"] for x in vpp_data ],
			'.', markersize=1)
plt.xlabel("client RTT estimates [ms]")
plt.ylabel("pn_valid RTT estimates [ms]")
save_figure(plt.gcf(), PLOT_DIR + "/correlation_scatter")

###
### Calculate error readings
###

for entry in vpp_data:
	for analyzer_name in analyzer_names:
		if entry[analyzer_name] != None:
			entry[analyzer_name + '_error'] = entry[analyzer_name] - entry['client']


###
### Plot ECDFs
###

f = plt.figure()
f.set_size_inches(10, 7)
x_limits = (-40, 40)
marker_distance = 1

to_plot = analyzer_names
markers = ("o", "v", 's', 'p', 'h', '8')
colors = ('b', 'g', 'r', 'c', 'm', 'y')

# first plot the lines

for markersonly in range(1): #2):
	for i in range(len(to_plot)):

		analyzer_name = to_plot[i]
		analyzer_rtts = [ x[analyzer_name] for x in vpp_data ]
		error_data = [ x[analyzer_name + '_error'] for x in vpp_data
				if x[analyzer_name + '_error'] != None]
		error_data.sort()
		frequency = [i/len(error_data) for i in range(len(error_data))]

		if markersonly:
			linestyle = ' '
			label = None
		else:
			linestyle = '-'
			label = analyzer_name

		plt.plot(error_data, frequency,
				color = colors[i],
				linestyle = linestyle,
				linewidth = 1,
				#marker = markers[i],
				#markevery = (float(i), float(marker_distance * len(to_plot))),
				#markevery = (0.01*i, 0.1),
				#markeredgewidth = 1,
				#markersize = 5,
				#markeredgecolor = colors[i],
				#markerfacecolor = (0,0,0,0),
				label = label)

plt.xlim(x_limits)
plt.legend()
save_figure(plt.gcf(), PLOT_DIR + "/ECDF")
