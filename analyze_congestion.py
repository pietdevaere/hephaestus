#!/usr/bin/python3

import matplotlib.pyplot as plt
import sys
import math
import collections

minq_log_path = sys.argv[1]
#output_prefix = sys.argv[2]
if len(sys.argv) > 3:
	run_info = sys.argv[3]
else:
	run_info = ''

window_times = list()
window_sizes = list()

inflight_times = list()
inflight_sizes = list()

minq_log_file = open(minq_log_path)
for raw_line in minq_log_file:
	if raw_line.find("CONGESTION_WINDOW") != -1:
		line = raw_line.split()
		size = int(line[-1])
		time = float(line[-3])
		window_sizes.append(size)
		window_times.append(time)
	if raw_line.find("BYTES_IN_FLIGHT") != -1:
		line = raw_line.split()
		size = int(line[-1])
		time = float(line[-3])
		inflight_sizes.append(size)
		inflight_times.append(time)

print("Number of BYTES_IN_FLIGHT reports:", len(inflight_sizes))
print("Number of CONGESTION_WINDOW reports:", len(window_sizes))
minq_log_file.close()

####################################################
## DEFINE SERIES AND TIME
####################################################

x_values = (window_times, inflight_times)
y_values = (window_sizes, inflight_sizes)
legend_data = ('congestion window', 'data in flight')
formats = ('b', 'r')

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

####################################################
## PLOT
####################################################

toplot = (1, 0)

for plot_index in toplot:
	plt.plot(x_values[plot_index], y_values[plot_index], formats[plot_index], linewidth = .5, alpha=0.8)
	plt.grid()
	plt.ylabel("[bytes]")
	plt.xlabel("time [s]")
	#plt.title("{} congestion overview {}".format(output_prefix, run_info))
	plt.legend([legend_data[i] for i in toplot])

#plt.savefig("{}_congestion.pdf".format(output_prefix))
#plt.savefig("{}_congestion.png".format(output_prefix), dpi = 300)

if len(inflight_sizes):
	print("Inflight data (max/mean/min): {}/{}/{}".format(
		max(inflight_sizes), sum(inflight_sizes)//len(inflight_sizes), min(inflight_sizes)))
else:
	print("Inflight data (max/mean/min): -/-/-")

if len(window_sizes):
	print("Window size (max/mean/min): {}/{}/{}".format(
		max(window_sizes), sum(window_sizes)//len(window_sizes), min(window_sizes)))
else:
	print("Window size (max/mean/min): -/-/-")
