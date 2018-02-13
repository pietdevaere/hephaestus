#!/usr/bin/python3

import matplotlib.pyplot as plt
import sys
import math
import collections
import pickle
import copy
import functools
import numpy as np

INVALID_SPIN_COLOR = "#ff69b450"

####################################################
## TIME CLASS to facilitate relative times
####################################################
@functools.total_ordering
class Time:
	zeroTime = None

	def __init__(self, epoch):
		self.epoch = float(epoch)

	def __float__(self):
		if Time.zeroTime:
			return float(self.epoch - Time.zeroTime)
		else:
			return float(self.epoch)

	def __repr__(self):
		return str(float(self))

	def __format__(self, format_spec):
		return "{:.6} s".format(float(self))

	def __eq__(self, other):
		if other == None:
			return False
		return float(self) == float(other)

	def __lt__(self, other):
		return float(self) < float(other)

####################################################
## SUM UP time intervals
####################################################
def get_total_invalid_time(intervals):
	result = 0
	for interval in intervals:
		result += float(interval[1]) - float(interval[0])

	return float(result)

####################################################
## Parse inputs
####################################################


moku_path = sys.argv[1]
client_log_path = sys.argv[2]
server_log_path = sys.argv[3]
ping_path = sys.argv[4]
output_prefix = sys.argv[5]
if len(sys.argv) > 6:
	run_info = sys.argv[6]
else:
	run_info = ''

all_datasets = list()

data_spin = dict()
all_datasets.append(data_spin)
data_spin['rtts'] = list()
data_spin['times'] = list()
data_spin['plot_color'] = 'y'
data_spin['legend'] = 'spin signal (two bits)'
data_spin['rejected'] = list()

data_spinbit = dict()
all_datasets.append(data_spinbit)
data_spinbit['rtts'] = list()
data_spinbit['times'] = list()
data_spinbit['plot_color'] = 'y'
data_spinbit['legend'] = 'spinbit (one bit)'
data_spinbit['rejected'] = list()


data_spinbit_pn = dict()
all_datasets.append(data_spinbit_pn)
data_spinbit_pn['rtts'] = list()
data_spinbit_pn['times'] = list()
data_spinbit_pn['plot_color'] = 'y'
data_spinbit_pn['legend'] = 'spinbit (one bit) with Pn filter'
data_spinbit_pn['rejected'] = list()


data_server = dict()
all_datasets.append(data_server)
data_server['rtts'] = list()
data_server['times'] = list()
data_server['plot_color'] = 'm'
data_server['legend'] = 'server RTT estimate'
data_server['rejected'] = list()

data_server_tcp = dict()
all_datasets.append(data_server_tcp)
data_server_tcp['rtts'] = list()
data_server_tcp['times'] = list()
data_server_tcp['plot_color'] = 'm'
data_server_tcp['legend'] = 'server RTT estimate (TCP)'
data_server_tcp['rejected'] = list()

data_client = dict()
all_datasets.append(data_client)
data_client['rtts'] = list()
data_client['times'] = list()
data_client['plot_color'] = 'c'
data_client['legend'] = 'client RTT estimate'
data_client['rejected'] = list()

data_client_tcp = dict()
all_datasets.append(data_client_tcp)
data_client_tcp['rtts'] = list()
data_client_tcp['times'] = list()
data_client_tcp['plot_color'] = 'c'
data_client_tcp['legend'] = 'client RTT estimate (TCP)'
data_client_tcp['rejected'] = list()

data_ping = dict()
all_datasets.append(data_ping)
data_ping['rtts'] = list()
data_ping['times'] = list()
data_ping['plot_color'] = 'b'
data_ping['legend'] = 'ping client->server'
data_ping['rejected'] = list()

server_invalid_intervals = list()
client_invalid_intervals = list()
rtt_invalid_intervals = list()
client_invalid_time = Time(0)
server_invalid_time = Time(0)

####################################################
## EXTRACT DATA FROM FILES
####################################################

time = 0
moku_file = open(moku_path)
for raw_line in moku_file:

	## VALID BIT
	if raw_line.startswith("LATENCY_VALID_CLIENT:"):
		line = raw_line.split()
		time = Time(line[2])
		client_valid = bool(int(line[-1]))
		if client_invalid_time == Time(0) and client_valid == False:
			client_invalid_time = time
		if client_invalid_time != Time(0) and client_valid == True:
			client_invalid_intervals.append((client_invalid_time, time))
			client_invalid_time = Time(0)
	if raw_line.startswith("LATENCY_VALID_SERVER:"):
		line = raw_line.split()
		time = Time(line[2])
		server_valid = bool(int(line[-1]))
		if server_invalid_time == Time(0) and server_valid == False:
			server_invalid_time = time
		if server_invalid_time != Time(0) and server_valid == True:
			server_invalid_intervals.append((server_invalid_time, time))
			server_invalid_time = Time(0)

	## TWO BIT SPIN SIGNAL
	if raw_line.startswith("TWO_BIT_LATENCY_FLIP:"):
		line = raw_line.split()
		rtt = float(line[4][:-2])
		time = Time(line[2])
		data_spin['rtts'].append(rtt)
		data_spin['times'].append(time)
	elif raw_line.startswith("TWO_BIT_LATENCY_ERROR:"):
		line = raw_line.split()
		rtt = float(line[4][:-2])
		time = Time(line[2])
		data_spin['rejected'].append((time, rtt))

	## ONE BIT SPINBIT
	if raw_line.startswith("ONE_BIT_LATENCY_FLIP:"):
		line = raw_line.split()
		rtt = float(line[4][:-2])
		time = Time(line[2])
		data_spinbit['rtts'].append(rtt)
		data_spinbit['times'].append(time)


if client_invalid_time != Time(0):
	client_invalid_intervals.append((client_invalid_time, time))
if server_invalid_time != Time(0):
	server_invalid_intervals.append((server_invalid_time, time))
moku_file.close()

print("Number of client invalid intervals: {:<5} Total invalid time: {:.3} s".format(
	len(client_invalid_intervals), get_total_invalid_time(client_invalid_intervals)))
print("Number of server invalid intervals: {:<5} Total invalid time: {:.3} s".format(
	len(server_invalid_intervals), get_total_invalid_time(server_invalid_intervals)))
print("Number of spin transitions:", len(data_spin['rtts']),
	  'rejected:', len(data_spin['rejected']))
print("Number of spinBIT transitions:", len(data_spinbit['rtts']))

#moku_file = open(moku_path)
#for raw_line in moku_file:
	#if raw_line.startswith("TWO_BIT_LATENCY_FLIP:"):
		#line = raw_line.split()
		#rtt = float(line[4][:-2])
		#time = Time(line[2])
		#data_spin['rtts'].append(rtt)
		#data_spin['times'].append(time)
	#elif raw_line.startswith("TWO_BIT_LATENCY_ERROR:"):
		#line = raw_line.split()
		#rtt = float(line[4][:-2])
		#time = Time(line[2])
		#data_spin['rejected'].append((time, rtt))

#moku_file.close()

#moku_file = open(moku_path)
#for raw_line in moku_file:
	#if raw_line.startswith("ONE_BIT_LATENCY_FLIP:"):
		#line = raw_line.split()
		#rtt = float(line[4][:-2])
		#time = Time(line[2])
		#data_spinbit['rtts'].append(rtt)
		#data_spinbit['times'].append(time)
#moku_file.close()

moku_file = open(moku_path)
for raw_line in moku_file:
	if raw_line.startswith("ONE_BIT_PN_LATENCY_FLIP:"):
		line = raw_line.split()
		rtt = float(line[4][:-2])
		time = Time(line[2])
		data_spinbit_pn['rtts'].append(rtt)
		data_spinbit_pn['times'].append(time)
	elif raw_line.startswith("ONE_BIT_PN_LATENCY_ERROR:"):
		line = raw_line.split()
		rtt = float(line[4][:-2])
		time = Time(line[2])
		data_spinbit_pn['rejected'].append((time, rtt))
print("Number of spinBIT with Pn filter transitions:", len(data_spinbit_pn['rtts']),
	  'rejected:', len(data_spinbit_pn['rejected']))
moku_file.close()

server_log_file = open(server_log_path)
for raw_line in server_log_file:
	if raw_line.find("RTT:") != -1:
		line = raw_line.split()
		rtt = float(line[-1])
		time = Time(line[-5])
		data_server['rtts'].append(rtt)
		data_server['times'].append(time)
	if raw_line.find("RTT_TCP:") != -1:
		line = raw_line.split()
		rtt = float(line[-1])
		time = Time(line[-5])
		data_server_tcp['rtts'].append(rtt)
		data_server_tcp['times'].append(time)
print("Number of rtts reported by server:", len(data_server['rtts']))
print("Number of rtts (tcp) reported by server:", len(data_server_tcp['rtts']))
server_log_file.close()

client_log_file = open(client_log_path)
for raw_line in client_log_file:
	if raw_line.find("RTT:") != -1:
		line = raw_line.split()
		rtt = float(line[-1])
		time = Time(line[-5])
		data_client['rtts'].append(rtt)
		data_client['times'].append(time)
	if raw_line.find("RTT_TCP:") != -1:
		line = raw_line.split()
		rtt = float(line[-1])
		time = Time(line[-5])
		data_client_tcp['rtts'].append(rtt)
		data_client_tcp['times'].append(time)
print("Number of rtts reported by client:", len(data_client['rtts']))
print("Number of rtts (tcp) reported by client:", len(data_client_tcp['rtts']))
client_log_file.close()

ping_file = open(ping_path)
for raw_line in ping_file:
	if raw_line.startswith("PING"):
		try:
			line = raw_line.split()
			rtt = float(line[2])
			time = Time(line[1])
			data_ping['rtts'].append(rtt)
			data_ping['times'].append(time)
		except:
			pass
	if raw_line.startswith("["):
		line = raw_line.split()
		rtt = float(line[-2][5:])
		time = Time(line[0][1:-1])
		data_ping['rtts'].append(rtt)
		data_ping['times'].append(time)
print("Number of rtts reported by ping:", len(data_ping['rtts']))
ping_file.close()

####################################################
## HELPER FUNCTIONS
####################################################

def merge_intervals(intervals_A, intervals_B):
	all_intervals = sorted(intervals_A + intervals_B)
	start = all_intervals[0][0]
	stop = all_intervals[0][1]
	merged_intervals = list()

	for interval in all_intervals:
		if interval[0] <= stop:
			stop = max(stop, interval[1])
		else:
			merged_intervals.append((start, stop))
			start = interval[0]
			stop = interval[1]

	merged_intervals.append((start, stop))
	return merged_intervals

def save_figure(figure, filename):
	print("Generating figure:", filename, "...", end=" ")
	figure.savefig("{}.pdf".format(filename))
	figure.savefig("{}.png".format(filename))
	pickle.dump(figure, open("{}.fig.pickle".format(filename), 'wb'))
	print("Done")

def moving_minimum(serie, window_size = 10):
	result = list()
	window = collections.deque(maxlen = window_size)

	window.append(serie[0])
	result.append(serie[0])

	for i in range(1, len(serie)):
		window.append(serie[i])
		rejected_min = min(window)
		corrected_window = window.copy()
		#corrected_window.remove(rejected_min)
		accepted_min = min(corrected_window)
		result.append(accepted_min)

	return result

def moving_minimum_time(serie, epochs, rtts = 5):
	result = list()
	window = list()
	serie_indexes = list()
	seconds = 0

	for i in range(len(serie)):
		if serie[i] == None:
			result.append(None)
			continue
		window.append(serie[i])
		serie_indexes.append(i)
		base_epoch = epochs[i]


		for window_index in range(len(window)):
			serie_index = serie_indexes[window_index]
			if float(epochs[serie_index]) >= float(base_epoch) - seconds:
				break

		window = window[window_index:]
		serie_indexes = serie_indexes[window_index:]

		result.append(min(window))
		seconds = result[-1] * rtts / 1000

	return result

####################################################
## MERGE CLIENT & SERVER INVALID
####################################################

rtt_invalid_intervals = merge_intervals(client_invalid_intervals, server_invalid_intervals)
print("Number of RTT invalid intervals: {:<5} Total invalid time: {:.3} s".format(
	len(rtt_invalid_intervals), get_total_invalid_time(rtt_invalid_intervals)))
####################################################
## MAKE TIME RELATIVE
####################################################

max_time = 0
min_time = math.inf
for dataset in all_datasets:
	if 'times' in dataset:
		max_time = max(max_time, float(max(dataset['times'])))
		min_time = min(min_time, float(min(dataset['times'])))

Time.zeroTime = min_time

#for dataset in all_datasets:
	#if 'times' in dataset:
		#for i in range(len(dataset['times'])):
			#dataset['times'][i] = dataset['times'][i] - min_time

	#if 'rejected' in dataset:
		#for i in range(len(dataset['rejected'])):
			#new_time = dataset['rejected'][i][0] - min_time
			#new_rtt = dataset['rejected'][i][1]

			#dataset['rejected'][i] = (new_time, new_rtt)

max_rtt = 0
min_rtt = math.inf
for dataset in all_datasets:
	if rtt:
		max_rtt = max(max_rtt, max(dataset['rtts']))
		min_rtt = min(min_rtt, min(dataset['rtts']))

max_plot_time = max_time - min_time
max_plot_time = min(max_plot_time, 150)




print(client_invalid_intervals)
print()
print(server_invalid_intervals)



####################################################
## MAKE MOVING MINIMUMS
####################################################

def add_moving_minimums():
	for dataset in all_datasets:
		if 'moving_min' not in dataset:
			dataset['moving_min'] = moving_minimum_time(dataset['rtts'], dataset['times'])

add_moving_minimums()

####################################################
## FILTER SPINBIT FOR REORDERING
####################################################

def reject_reordered_threshold(dataset, threshold = 1):
	output = copy.deepcopy(dataset)
	output['times'] = list()
	output['rtts'] = list()
	output['rejected'] = list()
	output['legend']= '>>SET ME<<'
	del(output['moving_min'])
	for i in range(len(dataset['times'])):
		if dataset['rtts'][i] > threshold:
			output['times'].append(dataset['times'][i])
			output['rtts'].append(dataset['rtts'][i])
		else:
			output['rejected'].append((dataset['times'][i], dataset['rtts'][i]))

	return output

def reject_reordered_dynamic(dataset, fraction = 0.1):
	output = copy.deepcopy(dataset)
	output['times'] = list()
	output['rtts'] = list()
	output['rejected'] = list()
	output['legend']= '>>SET ME<<'
	del(output['moving_min'])
	window = collections.deque(maxlen = 10)
	window.append(dataset['rtts'][0])
	rejected = 0

	for i in range(len(dataset['times'])):
		threshold = fraction * min(window)

		if (dataset['rtts'][i] > threshold) or (rejected >= 5):
			output['times'].append(dataset['times'][i])
			output['rtts'].append(dataset['rtts'][i])
			rejected = 0
			window.append(dataset['rtts'][i])

		else:
			rejected = rejected + 1
			output['rejected'].append((dataset['times'][i], dataset['rtts'][i]))

	return output

data_spinbit_threshold = reject_reordered_threshold(data_spinbit)
data_spinbit_threshold['legend'] = 'spinbit (one bit) static threshold filtered'
all_datasets.append(data_spinbit_threshold)

data_spinbit_dynamic = reject_reordered_dynamic(data_spinbit)
data_spinbit_dynamic['legend'] = 'spinbit (one bit) dynamic threshold filtered'
all_datasets.append(data_spinbit_dynamic)


add_moving_minimums()
####################################################
## PLOT HISTOGRAM
####################################################
plt.figure()

to_plot = (data_spinbit_pn, data_server, data_client)

plot_bins = [i for i in range(0, 101)]
legend = []

for dataset in to_plot:
	n, bins, patches = plt.hist(dataset['rtts'], plot_bins, (35, 100), True, stacked=True, alpha = 0.7, color=dataset['plot_color'])
	legend.append(dataset['legend'])

plt.xlabel('RTT [ms]')
plt.ylabel('frequency []')
plt.legend(legend)
plt.title("RTT values reported by different mechanisms [{}]".format(run_info))

filename = "{}_rtt-hystogram".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT SPIN, CLIENT, SERVER, PING
####################################################
plt.figure()

to_plot = (data_ping, data_spinbit_pn, data_server, data_client)

f, axarr = plt.subplots(len(to_plot))
f.set_size_inches(20, 9)
axarr[0].set_title("Different forms of RTT measurement versus time [{}]".format(run_info))

for i in range(len(to_plot)):
	dataset = to_plot[i]
	axes = axarr[i]

	line = axes.plot(dataset['times'], dataset['rtts'], dataset['plot_color'], linewidth = .5)
	moving_min = axes.plot(dataset['times'], dataset['moving_min'], 'g', linewidth = .5)
	axes.set_ylabel("RTT [ms]")
	axes.set_xlabel("time [s]")
	axes.legend([dataset['legend'], "moving minimum"], loc = 2)
	axes.set_ylim([35, 100])
	axes.set_xlim([0, max_time-min_time])
	axes.grid()

	for period in client_invalid_intervals:
		axes.axvspan(period[0], period[1], facecolor=INVALID_SPIN_COLOR)

filename = "{}_time-vs-rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT SPIN, CLIENT, SERVER, PING (DETAIL)
####################################################
plt.figure()

to_plot = (data_ping, data_spinbit_pn, data_server, data_client)

f, axarr = plt.subplots(len(to_plot))
f.set_size_inches(20, 9)
axarr[0].set_title("Different forms of RTT measurement versus time [{}]".format(run_info))

for i in range(len(to_plot)):
	dataset = to_plot[i]
	axes = axarr[i]

	line = axes.plot(dataset['times'], dataset['rtts'], dataset['plot_color']+'-x', linewidth = .5)
	moving_min = axes.plot(dataset['times'], moving_minimum_time(dataset['rtts'], dataset['times']), 'g', linewidth = .5)
	axes.set_ylabel("RTT [ms]")
	axes.set_xlabel("time [s]")
	axes.legend([dataset['legend'], "moving minimum"], loc = 2)
	axes.set_ylim([35, 100])
	axes.set_xlim([59, 61])
	axes.grid()

	for period in client_invalid_intervals:
		axes.axvspan(period[0], period[1], facecolor=INVALID_SPIN_COLOR)

filename = "{}_time-vs-rtt-detail".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT PING
####################################################

plt.figure()
plt.plot(data_ping['times'], data_ping['rtts'], linewidth = .5)
plt.ylabel("RTT [ms]")
plt.xlabel("time [s]")
plt.title("Ping based RTT measuremnt {}".format(run_info))
plt.grid()

filename = "{}_ping_rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT SPINBIT VS SPIN
####################################################
plt.figure()
plt.gcf().set_size_inches(20, 9)
plt.plot(data_spinbit['times'], data_spinbit['rtts'], data_spinbit['plot_color'], linewidth = .3)
plt.plot(data_spin['times'], data_spin['rtts'], data_spin['plot_color'], linewidth = .3)
plt.ylabel("RTT [ms]")
plt.xlabel("time [s]")
plt.title("Single and dual bit spin latency measurement {}".format(run_info))
plt.legend(['spinbit (one bit)', 'spin (two bits)'])
plt.ylim([35, 100])
plt.grid()

filename = "{}_one_vs_two_bits_rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## COMPARISON OF REORDERING rejection
####################################################
plt.figure()

to_plot = (data_spinbit, data_spin, data_spinbit_threshold, data_spinbit_dynamic, data_spinbit_pn)

f, axarr = plt.subplots(len(to_plot))
f.set_size_inches(20, 13)
axarr[0].set_title("Different forms of reordering rejection [{}]".format(run_info))

for i in range(len(to_plot)):
	dataset = to_plot[i]
	axes = axarr[i]

	line = axes.plot(dataset['times'], dataset['rtts'], dataset['plot_color'], linewidth = .5)
	if 'moving_min' in dataset:
		moving_min = axes.plot(dataset['times'], dataset['moving_min'], 'g', linewidth = .5)

	if 'rejected' in dataset:
		rejected_times = [i[0] for i in dataset['rejected']]
		rejected_rtt = [40 for i in rejected_times]
		axes.plot(rejected_times, rejected_rtt, 'rx')
	axes.set_ylabel("RTT [ms]")
	axes.set_xlabel("time [s]")
	axes.legend([dataset['legend'], "moving minimum", 'rejected samples'], loc = 2)
	axes.set_ylim([35, 100])
	axes.set_xlim([0, max_time-min_time])
	axes.grid()

	for period in client_invalid_intervals:
		axes.axvspan(period[0], period[1], facecolor=INVALID_SPIN_COLOR)


filename = "{}_reorder-rejection-rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## REMOVE SAMPLES OUTSIDE OF VALID REGIONS
####################################################

def time_in_intervals(time, intervals):
	for interval in intervals:
		if time >= interval[0] and time <= interval[1]:
			return True
		if time < interval[0]:
			return False

def filter_valid_only(dataset, intervals):
	output = copy.deepcopy(dataset)
	output['times'] = list()
	output['rtts'] = list()
	output['rejected'] = list()
	output['legend']= '>>SET ME<<'
	if 'moving_min' in output:
		del(output['moving_min'])
	for i in range(len(dataset['times'])):
		if time_in_intervals(dataset['times'][i], intervals):
			output['times'].append(dataset['times'][i])
			output['rtts'].append(None)
		else:
			output['times'].append(dataset['times'][i])
			output['rtts'].append(dataset['rtts'][i])
	return output

data_spinbit_pn_valid = filter_valid_only(data_spinbit_pn, rtt_invalid_intervals)
data_spinbit_pn_valid['legend'] = 'spinbit (one bit) with Pn and invalid filter'
all_datasets.append(data_spinbit_pn_valid)
add_moving_minimums()
####################################################
## PLOT WITHOUT INVALID SAMPLES
####################################################
plt.figure()

to_plot = (data_ping, data_server, data_client, data_spinbit_pn, data_spinbit_pn_valid)

f, axarr = plt.subplots(len(to_plot))
f.set_size_inches(20, 13)
axarr[0].set_title("Influence of filtering invalid samples [{}]".format(run_info))

for i in range(len(to_plot)):
	dataset = to_plot[i]
	axes = axarr[i]

	line = axes.plot(dataset['times'], dataset['rtts'], dataset['plot_color'], linewidth = .5, label=dataset['legend'])
	if 'moving_min' in dataset:
		moving_min = axes.plot(dataset['times'], dataset['moving_min'], 'g', linewidth = .5, label="moving minimum")

	#if 'rejected' in dataset: # and len(dataset['rejected']) > 0:
		#rejected_times = [i[0] for i in dataset['rejected']]
		#rejected_rtt = [40 for i in rejected_times]
		#axes.plot(rejected_times, rejected_rtt, 'rx', label='rejected samples')
	axes.set_ylabel("RTT [ms]")
	axes.set_xlabel("time [s]")
	axes.legend(loc = 2)
	axes.set_ylim([35, 100])
	axes.set_xlim([0, max_time-min_time])
	axes.grid()

	for period in client_invalid_intervals:
		axes.axvspan(period[0], period[1], facecolor=INVALID_SPIN_COLOR)

filename = "{}_without-invalid-rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT COMPARISON TCP and QUIC style RTT estimates
####################################################
plt.figure()

to_plot = ((data_server, data_server_tcp), (data_client, data_client_tcp))
plot_colors = ('c', 'm')

f, axarr = plt.subplots(len(to_plot))
f.set_size_inches(20, 13)
axarr[0].set_title("Comparison on QUIC vs TCP style RTT estimates [{}]".format(run_info))

for i in range(len(to_plot)):
	axes = axarr[i]
	for j in range(len(to_plot[i])):
		dataset = to_plot[i][j]
		color = plot_colors[j]
		line = axes.plot(dataset['times'], dataset['rtts'], color, linewidth = .5, label=dataset['legend'])

	axes.set_ylabel("RTT [ms]")
	axes.set_xlabel("time [s]")
	axes.legend(loc = 2)
	axes.set_ylim([35, 100])
	axes.set_xlim([0, max_time-min_time])
	axes.grid()

filename = "{}_quic-vs-tcp-rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## UPSAMPLE, to have matched timebases.
####################################################

def in_interval(time, intervals):
	for interval in intervals:
		if time >= interval[0] and time <= interval[1]:
			return True
	return False

def forward_cursor_to_time(cursor, time, dataset):
	if dataset['times'][0] >= time:
		return -1

	#assert(dataset['times'][cursor] < time)

	while ( cursor < len(dataset['times']) )and ( dataset['times'][cursor + 1] < time ):
		cursor = cursor + 1

	#print("time is {}, stopping at {}".format(time, dataset['times'][cursor]))
	return cursor

def interpollate_rtts(times, dataset):
	return_rtts = list()
	return_times = list()
	dataset_cursor = 0

	times.sort()
	for time in times:

		#print(float(time))
		assert(time != None)

		# First, seek to the right point in the array.
		dataset_cursor = forward_cursor_to_time(dataset_cursor, time, dataset)

		# If we are at the first element in the array:
		if dataset_cursor == -1:
			return_rtts.append(dataset['rtts'][0])
			return_times.append(time)
			continue

		# if we are at the last element in the array
		if dataset_cursor == len(dataset['times']) - 1:
			return_rtts.append(dataset['rtts'][len(dataset['rtts'])])
			return_times.append(time)
			continue


		# otherwise, we will have to do some interpollation
		offset = float(time) - float(dataset['times'][dataset_cursor])

		delta_time = float(dataset['times'][dataset_cursor + 1]) - float(dataset['times'][dataset_cursor])
		delta_rtt = float(dataset['rtts'][dataset_cursor + 1]) - float(dataset['rtts'][dataset_cursor])
		slope = delta_rtt / delta_time

		value = float(dataset['rtts'][dataset_cursor]) + offset * slope
		return_rtts.append(value)
		return_times.append(time)

	return return_rtts, return_times

rtts, times = interpollate_rtts(data_spinbit_pn['times'], data_client)

data_rtt_client_pol_pn = dict()
all_datasets.append(data_rtt_client_pol_pn)
data_rtt_client_pol_pn['rtts'] = rtts
data_rtt_client_pol_pn['times'] = times
data_rtt_client_pol_pn['plot_color'] = 'c'
data_rtt_client_pol_pn['legend'] = 'client RTT estimate (interpollated to spinbit_pn)'
data_rtt_client_pol_pn['rejected'] = list()

rtts, times = interpollate_rtts(data_spinbit['times'], data_client)

data_rtt_client_pol = dict()
all_datasets.append(data_rtt_client_pol)
data_rtt_client_pol['rtts'] = rtts
data_rtt_client_pol['times'] = times
data_rtt_client_pol['plot_color'] = 'c'
data_rtt_client_pol['legend'] = 'client RTT estimate (interpollated to spinbit)'
data_rtt_client_pol['rejected'] = list()

####################################################
## PLOT INTERPOLLATED CLIENT_RTT
####################################################
plt.figure()

plt.title("Interpollation check [{}]".format(run_info))

to_plot = (data_rtt_client_pol, data_spinbit_pn)

for dataset in to_plot:
	plt.plot(	dataset['times'],
				dataset['rtts'],
				dataset['plot_color'] + 'x',
				label = dataset['legend']
			)

plt.xlim([10, 11])
plt.grid()
plt.ylim((30, 60))


filename = "{}_rtt_interpollate_check".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT correlation
####################################################
plt.figure()

from scipy.stats.stats import pearsonr

rho, p = pearsonr(data_rtt_client_pol_pn['rtts'], data_spinbit_pn['rtts'])

plt.plot(data_rtt_client_pol_pn['rtts'], data_spinbit_pn['rtts'], '.', markersize=1)
plt.xlabel("client RTT estimates [ms]")
plt.ylabel("spinbit RTT estimate [ms]")
plt.title("Pearson correlation: {:.3}, p-value: {:.3} [{}]".format(rho, p, run_info))
plt.ylim([35, 110])
plt.xlim([35, 110])
plt.grid()

filename = "{}_rtt_spinbit_correlation".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## calculate errors
####################################################

client_rtts = np.array(data_rtt_client_pol['rtts'])
spinbit_rtts = np.array(data_spinbit['rtts'])
error_client_spinbit = dict()
error_client_spinbit['rtts'] = (client_rtts - spinbit_rtts).tolist()
error_client_spinbit['times'] = copy.deepcopy(data_spinbit['times'])
error_client_spinbit['legend'] = "client - spinbit"
error_client_spinbit['plot_color'] = 'y'

client_rtts = np.array(data_rtt_client_pol_pn['rtts'])
spinbit_pn_rtts = np.array(data_spinbit_pn['rtts'])
error_client_spinbit_pn = dict()
error_client_spinbit_pn['rtts'] = (client_rtts - spinbit_pn_rtts).tolist()
error_client_spinbit_pn['times'] = copy.deepcopy(data_spinbit_pn['times'])
error_client_spinbit_pn['legend'] = "client - spinbit with Pn filter"
error_client_spinbit_pn['plot_color'] = 'c'

error_client_spinbit_valid = filter_valid_only(error_client_spinbit, rtt_invalid_intervals)
error_client_spinbit_valid['legend'] = "client - spinbit with invalid filter"
error_client_spinbit_valid['plot_color'] = 'm'


error_client_spinbit_pn_valid = filter_valid_only(error_client_spinbit_pn, rtt_invalid_intervals)
error_client_spinbit_pn_valid['legend'] = "client - spinbit with Pn and invalid filter"
error_client_spinbit_pn_valid['plot_color'] = 'b'

####################################################
## PLOT ERRORS
####################################################

plt.figure()

to_plot = (error_client_spinbit, error_client_spinbit_pn, error_client_spinbit_valid, error_client_spinbit_pn_valid)

f, axarr = plt.subplots(len(to_plot))
f.set_size_inches(20, 13)
axarr[0].set_title("Absolute RTT estimation error for different spinbit flavours [{}]".format(run_info))

for i in range(len(to_plot)):
	dataset = to_plot[i]
	axes = axarr[i]

	line = axes.plot(dataset['times'], dataset['rtts'], dataset['plot_color'], linewidth = .5, label=dataset['legend'])

	axes.set_ylabel("RTT error [ms]")
	axes.set_xlabel("time [s]")
	axes.legend(loc = 2)
	axes.set_ylim([-40, 40])
	axes.set_xlim([0, max_time-min_time])
	axes.grid()

	for period in client_invalid_intervals:
		axes.axvspan(period[0], period[1], facecolor=INVALID_SPIN_COLOR)

filename = "{}_spinbit_absolute_error".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT ECDFs
####################################################

f = plt.figure()
f.set_size_inches(10, 7)

to_plot = (error_client_spinbit, error_client_spinbit_pn, error_client_spinbit_valid, error_client_spinbit_pn_valid)

line_style = ('', '--', '-.', ':')

for  i in range(len(to_plot)):

	dataset = to_plot[i]

	error_data = [x for x in dataset['rtts'] if x != None]
	error_data.sort()
	frequency = [i/len(error_data) for i in range(len(error_data))]

	plt.plot(error_data,  frequency, dataset['plot_color'] + line_style[i], linewidth = 2, label=dataset['legend'], alpha=0.7)

plt.title("spinbit RTT estimation ECDF [{}]".format(run_info))
plt.xlim([-25, 25])
plt.grid()
plt.ylabel("Cumulative relative frequency []")
plt.xlabel("Error [ms]")
plt.legend()

filename = "{}_rtt_spinbit_ECDF".format(output_prefix)
save_figure(plt.gcf(), filename)





#plt.figure()
#plt.plot(error, linewidth = .5, label="client - spinbit with Pn filter")
#plt.ylim([-40, 40])

#filename = "{}_rtt_spinbit_error".format(output_prefix)
#save_figure(plt.gcf(), filename)

#plt.figure()

#error_sorted = np.sort(error)
#count = np.array(range(len(error_sorted)))/len(error_sorted)

#plt.plot(error_sorted, count, linewidth = 1)
#plt.title("client - spinbit ECDF")
#plt.xlim([-25, 25])
#plt.grid()
#plt.ylabel("Cumulative relative frequency []")
#plt.xlabel("Error [ms]")

#filename = "{}_rtt_spinbit_ECDF".format(output_prefix)
#save_figure(plt.gcf(), filename)

#####################################################
### how many are out of "acceptable window"?
#####################################################

#def find_rtts_around_time(dataset, time, window, base_index):
	#start_index = None
	#stop_index = None

	#for index in range(base_index, len(dataset['times'])):
		#if start_index == None and float(dataset['times'][index]) >= float(time) - window:
			#start_index = index

		#if stop_index == None and float(dataset['times'][index]) > float(time) + window:
			#stop_index = index
			#break

	#if stop_index == None:
		#stop_index = len(dataset['times'])

	##print("start: {:.3}, time: {:.3}, stop: {:.3}".format(dataset['times'][start_index], time, dataset['times'][stop_index-1]))

	#return dataset['rtts'][start_index:stop_index], start_index

#out_of_window = 0
#start_index = 0

#for cursor in range(len(data_spinbit_pn['times'])):
	##if cursor % 10 == 0:
	##	print(cursor / len(data_spinbit_pn['times']))
	#time = data_spinbit_pn['times'][cursor]
	#rtt = data_spinbit_pn['rtts'][cursor]
	#window_size = 20e-3
	#window, start_index = find_rtts_around_time(data_client, time, window_size, start_index)
	#if len(window) != 0 and (rtt > max(window) or rtt < min(window)):
		#out_of_window += 1

#print("Out of window ({} s): {}".format(window_size, out_of_window))
