#!/usr/bin/python3

import matplotlib.pyplot as plt
import sys
import math
import collections
import pickle
import copy
import functools

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
data_server['legend'] = 'server ACK delays'
data_server['rejected'] = list()

data_client = dict()
all_datasets.append(data_client)
data_client['rtts'] = list()
data_client['times'] = list()
data_client['plot_color'] = 'c'
data_client['legend'] = 'client ACK delays'
data_client['rejected'] = list()

data_ping = dict()
all_datasets.append(data_ping)
data_ping['rtts'] = list()
data_ping['times'] = list()
data_ping['plot_color'] = 'b'
data_ping['legend'] = 'ping client->server'
data_ping['rejected'] = list()

server_invalid_periods = list()
client_invalid_periods = list()
rtt_invalid_periods = list()
client_invalid_time = None
server_invalid_time = None

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
		return str(self.epoch)

	def __eq__(self, other):
		return float(self) == float(other)

	def __lt__(self, other):
		return float(self) < float(other)


####################################################
## EXTRACT DATA FROM FILES
####################################################

#moku_file = open(moku_path)
#for raw_line in moku_file:
#	if raw_line.startswith("LATENCY_VALID_CLIENT:"):
#		line = raw_line.split()
#		time = float(line[2])
#		client_valid = bool(line[-1])
#		if client_invalid_time == None and client_valid == false:
#			client_invalid_time = time
#moku_file.close()

moku_file = open(moku_path)
for raw_line in moku_file:
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
print("Number of spin transitions:", len(data_spin['rtts']),
	  'rejected:', len(data_spin['rejected']))
moku_file.close()

moku_file = open(moku_path)
for raw_line in moku_file:
    if raw_line.startswith("ONE_BIT_LATENCY_FLIP:"):
        line = raw_line.split()
        rtt = float(line[4][:-2])
        time = Time(line[2])
        data_spinbit['rtts'].append(rtt)
        data_spinbit['times'].append(time)
print("Number of spinBIT transitions:", len(data_spinbit['rtts']))
moku_file.close()

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
    if raw_line.find("ACK_DELAY") != -1:
        line = raw_line.split()
        rtt = float(line[-1])
        time = Time(line[-3])
        data_server['rtts'].append(rtt)
        data_server['times'].append(time)
print("Number of rtts reported by server:", len(data_server['rtts']))
server_log_file.close()

client_log_file = open(client_log_path)
for raw_line in client_log_file:
    if raw_line.find("ACK_DELAY") != -1:
        line = raw_line.split()
        rtt = float(line[-1])
        time = Time(line[-3])
        data_client['rtts'].append(rtt)
        data_client['times'].append(time)
print("Number of rtts reported by client:", len(data_client['rtts']))
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

def save_figure(figure, filename):
	figure.savefig("{}.pdf".format(filename))
	figure.savefig("{}.png".format(filename))
	pickle.dump(figure, open("{}.fig.pickle".format(filename), 'wb'))

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

####################################################
## MAKE MOVING MINIMUMS
####################################################

def add_moving_minimums():
	for dataset in all_datasets:
		if 'moving_min' not in dataset:
			dataset['moving_min'] = moving_minimum_time(dataset['rtts'], dataset['times'])

add_moving_minimums()
####################################################
## PLOT HISTOGRAM
####################################################
plt.figure()

to_plot = (data_spin, data_server, data_client)

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

to_plot = (data_ping, data_spin, data_server, data_client)

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

filename = "{}_time-vs-rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT SPIN, CLIENT, SERVER, PING (DETAIL)
####################################################
plt.figure()

to_plot = (data_ping, data_spin, data_server, data_client)

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
	axes.set_xlim([29, 31])
	axes.grid()

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
## FILTER SPINBIT FOR REORDERING
####################################################

def reject_reordered_threshold(dataset, threshold = 1):
	output = copy.deepcopy(dataset)
	output['times'] = list()
	output['rtts'] = list()
	output['rejected'] = list()
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
			print('.', end='')
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

filename = "{}_reorder-rejection-rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

