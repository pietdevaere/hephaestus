#!/usr/bin/python3

import matplotlib.pyplot as plt
import sys
import math
import collections
import pickle

moku_path = sys.argv[1]
client_log_path = sys.argv[2]
server_log_path = sys.argv[3]
ping_path = sys.argv[4]
output_prefix = sys.argv[5]
if len(sys.argv) > 6:
	run_info = sys.argv[6]
else:
	run_info = ''

spinbit_rtts = list()
spinbit_times = list()

server_rtts = list()
server_times = list()

client_rtts = list()
client_times = list()

ping_rtts = list()
ping_times = list()

moku_file = open(moku_path)
for raw_line in moku_file:
    if raw_line.startswith("LATENCYFLIP"):
        line = raw_line.split()
        rtt = float(line[4][:-2])
        time = float(line[2])
        spinbit_rtts.append(rtt)
        spinbit_times.append(time)
print("Number of spinbit transitions:", len(spinbit_rtts))
moku_file.close()

server_log_file = open(server_log_path)
for raw_line in server_log_file:
    if raw_line.find("ACK_DELAY") != -1:
        line = raw_line.split()
        rtt = float(line[-1])
        time = float(line[-3])
        server_rtts.append(rtt)
        server_times.append(time)
print("Number of rtts reported by server:", len(server_rtts))
server_log_file.close()

client_log_file = open(client_log_path)
for raw_line in client_log_file:
    if raw_line.find("ACK_DELAY") != -1:
        line = raw_line.split()
        rtt = float(line[-1])
        time = float(line[-3])
        client_rtts.append(rtt)
        client_times.append(time)
print("Number of rtts reported by client:", len(client_rtts))
client_log_file.close()

ping_file = open(ping_path)
for raw_line in ping_file:
	if raw_line.startswith("PING"):
		try:
			line = raw_line.split()
			rtt = float(line[2])
			time = float(line[1])
			ping_rtts.append(rtt)
			ping_times.append(time)
		except:
			pass
	if raw_line.startswith("["):
		line = raw_line.split()
		rtt = float(line[-2][5:])
		time = float(line[0][1:-1])
		ping_rtts.append(rtt)
		ping_times.append(time)

print("Number of rtts reported by ping:", len(ping_rtts))
ping_file.close()

####################################################
## MAKE CLIENT SMOOTH
####################################################


num_buckets = len(spinbit_rtts)
bucket_size = max(len(client_rtts)//num_buckets,1)
client_rtts_smooth = list()
for i in range(num_buckets):
	start = i * bucket_size
	end = (i+1) * bucket_size
	if bucket_size > 0:
		smooth = sum(client_rtts[start:end])/bucket_size
	else:
		smooth = 0
	client_rtts_smooth.append(smooth)


####################################################
## MAKE SERVER SMOOTH
####################################################


num_buckets = len(spinbit_rtts)
bucket_size = max(len(server_rtts)//num_buckets,1)
server_rtts_smooth = list()
for i in range(num_buckets):
	start = i * bucket_size
	end = (i+1) * bucket_size
	smooth = sum(server_rtts[start:end])/bucket_size
	server_rtts_smooth.append(smooth)

####################################################
## SAVE PLOT
####################################################

def save_figure(figure, filename):
	figure.savefig("{}.pdf".format(filename))
	figure.savefig("{}.png".format(filename))
	pickle.dump(figure, open("{}.fig.pickle".format(filename), 'wb'))



####################################################
## PLOT HISTOGRAM
####################################################


plot_bins = [i for i in range(0, 101)]

n, bins, patches = plt.hist(spinbit_rtts, plot_bins, (35, 100), True, stacked=True, alpha = 0.7, color='y')
n, bins, patches = plt.hist(server_rtts, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='m')
n, bins, patches = plt.hist(client_rtts, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='c')
#n, bins, patches = plt.hist(ping_rtts, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='b')

plt.xlabel('RTT [ms]')
plt.ylabel('frequency []')
plt.legend(['spinbit', 'server', 'client'])
plt.title("RTT values as reported by spinbit observer, server and client {}".format(run_info))

filename = "{}_rtt-hystogram".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT VERSUS_TIME
####################################################

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

#def moving_minimum_time(serie, epochs, seconds = 0.5):
	#result = list()

	#for i in range(len(serie)):
		##print(i)
		#window = list()
		#base_epoch = epochs[i]

		#for j in range(i, -1, -1):
			#if epochs[j] > base_epoch - seconds:
				#window.append(serie[j])
			#else:
				#break

		#result.append(min(window))

	#return result

#def moving_minimum_time(serie, epochs, seconds = 0.5):
	#result = list()
	#window = list()
	#serie_indexes = list()

	#for i in range(len(serie)):
		#window.append(serie[i])
		#serie_indexes.append(i)
		#base_epoch = epochs[i]

		#for window_index in range(len(window)):
			#serie_index = serie_indexes[window_index]
			#if epochs[serie_index] >= base_epoch - seconds:
				#break

		#window = window[window_index:]
		#serie_indexes = serie_indexes[window_index:]

		#result.append(min(window))

	#return result

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
			if epochs[serie_index] >= base_epoch - seconds:
				break

		window = window[window_index:]
		serie_indexes = serie_indexes[window_index:]

		result.append(min(window))
		seconds = result[-1] * rtts / 1000

	return result


def makeTicks(series, upper = 100):
	interval = float(upper) / len(series)
	return [i*interval for i in range(0, len(series))]

#plot_fig = plt.figure()
datasets = (ping_rtts,  spinbit_rtts,  server_rtts,  server_rtts_smooth,  client_rtts,  client_rtts_smooth)
x_values = (ping_times, spinbit_times, server_times, None,                client_times, None)
legend_data = ['ping client->server', 'spinbit', 'server', 'server smooth', 'client', 'client smooth', ]
formats = ['b', 'y', 'm', 'm', 'c', 'c']

# find time and RTT limits, make time series relative

max_time = 0
min_time = math.inf
for times in x_values:
	if times:
		max_time = max(max_time, max(times))
		min_time = min(min_time, min(times))

for times in x_values:
	if times  != None:
		for i in range(len(times)):
			times[i] = times[i] - min_time

max_rtt = 0
min_rtt = math.inf
for rtts in datasets:
	if rtt:
		max_rtt = max(max_rtt, max(rtts))
		min_rtt = min(min_rtt, min(rtts))

toplot = (0, 1, 2, 4)
f, axarr = plt.subplots(len(toplot))
f.set_size_inches(20, 9)
axarr[0].set_title("Different forms of RTT measurement versus time {}".format(run_info))

for plot in range(len(toplot)):
	dataset = toplot[plot]
	if x_values[dataset]:
		line = axarr[plot].plot(x_values[dataset], datasets[dataset], formats[dataset], linewidth = .5)
		line2 = axarr[plot].plot(x_values[dataset], moving_minimum_time(datasets[dataset], x_values[dataset]), 'g', linewidth = .5)
	else:
		line = axarr[plot].plot(datasets[dataset], formats[dataset])
	axarr[plot].set_ylabel("RTT [ms]")
	axarr[plot].set_xlabel("time [s]")
	axarr[plot].legend([legend_data[dataset], "moving minimum"], loc = 2)
	axarr[plot].set_ylim([35, 100])
	axarr[plot].set_xlim([0, max_time-min_time])
	axarr[plot].grid()

filename = "{}_time-vs-rtt".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## DETAILED PLOT
####################################################

toplot = (0, 1, 2, 4)
f, axarr = plt.subplots(len(toplot))
f.set_size_inches(20, 9)
axarr[0].set_title("Different forms of RTT measurement versus time {}".format(run_info))

for plot in range(len(toplot)):
	dataset = toplot[plot]
	if x_values[dataset]:
		line = axarr[plot].plot(x_values[dataset], datasets[dataset], formats[dataset]+'-x', markersize= 5, linewidth = .5)
	else:
		line = axarr[plot].plot(datasets[dataset], formats[dataset]+'x')
	axarr[plot].set_ylabel("RTT [ms]")
	axarr[plot].set_xlabel("time [s]")
	axarr[plot].legend([legend_data[dataset], "moving minimum"], loc = 2)
	axarr[plot].set_ylim([35, 80])
	axarr[plot].set_xlim([29, 30])
	axarr[plot].grid()

	line2 = axarr[plot].plot(x_values[dataset], moving_minimum_time(datasets[dataset], x_values[dataset]), 'g', linewidth = .5)

filename = "{}_time-vs-rtt-detail".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT SMOOTH
####################################################

plt.figure()

plot_bins = [i for i in range(0, 101)]

n, bins, patches = plt.hist(spinbit_rtts, plot_bins, (35, 100), True, stacked=True, alpha = 0.7, color='y')
n, bins, patches = plt.hist(server_rtts_smooth, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='m')
n, bins, patches = plt.hist(client_rtts_smooth, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='c')

plt.xlabel('RTT [ms]')
plt.ylabel('frequency []')
plt.legend(['spinbit', 'server smooth', 'client smooth'])
plt.title("RTT values as reported by spinbit observer, server and client {}".format(run_info))

filename = "{}_rtt-hystogram-smooth".format(output_prefix)
save_figure(plt.gcf(), filename)

####################################################
## PLOT PING
####################################################

plt.figure()
plt.plot(ping_times, ping_rtts, linewidth = .5)
plt.ylabel("RTT [ms]")
plt.xlabel("time [s]")
plt.title("Ping based RTT measuremnt {}".format(run_info))

filename = "{}_ping_rtt".format(output_prefix)
save_figure(plt.gcf(), filename)
