#!/usr/bin/python3

import matplotlib.pyplot as plt
import sys

moku_path = sys.argv[1]
client_log_path = sys.argv[2]
server_log_path = sys.argv[3]
ping_path = sys.argv[4]
output_prefix = sys.argv[5]

spinbit_rtts = list()
server_rtts = list()
client_rtts = list()
ping_rtts = list()

moku_file = open(moku_path)
for raw_line in moku_file:
    if raw_line.startswith("Delta: "):
        line = raw_line.split()
        rtt = float(line[1][:-2])
        spinbit_rtts.append(rtt)
print("Number of spinbit transitions:", len(spinbit_rtts))
moku_file.close()

server_log_file = open(server_log_path)
for raw_line in server_log_file:
    if raw_line.find("RTT for pn") != -1:
        line = raw_line.split()
        rtt = int(line[-2])
        server_rtts.append(rtt)
print("Number of rtts reported by server:", len(server_rtts))
server_log_file.close()

client_log_file = open(client_log_path)
for raw_line in client_log_file:
    if raw_line.find("RTT for pn") != -1:
        line = raw_line.split()
        rtt = int(line[-2])
        client_rtts.append(rtt)
print("Number of rtts reported by client:", len(client_rtts))
client_log_file.close()

ping_file = open(ping_path)
for raw_line in ping_file:
    if raw_line.startswith("64 bytes from"):
        line = raw_line.split()
        rtt = float(line[-2][-4:])
        ping_rtts.append(rtt)
print("Number of rtts reported by ping:", len(ping_rtts))
ping_file.close()

##
## MAKE CLIENT SMOOTH
##

num_buckets = len(spinbit_rtts)
bucket_size = len(client_rtts)//num_buckets
client_rtts_smooth = list()
for i in range(num_buckets):
	start = i * bucket_size
	end = (i+1) * bucket_size
	smooth = sum(client_rtts[start:end])/bucket_size
	client_rtts_smooth.append(smooth)

##
## MAKE CLIENT SMOOTH
##

num_buckets = len(spinbit_rtts)
bucket_size = len(server_rtts)//num_buckets
server_rtts_smooth = list()
for i in range(num_buckets):
	start = i * bucket_size
	end = (i+1) * bucket_size
	smooth = sum(server_rtts[start:end])/bucket_size
	server_rtts_smooth.append(smooth)



##
## PLOT HISTOGRAM
##

plot_bins = [i for i in range(35, 101)]

n, bins, patches = plt.hist(spinbit_rtts, plot_bins, (35, 100), True, stacked=True, alpha = 0.7, color='y')
n, bins, patches = plt.hist(server_rtts, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='m')
n, bins, patches = plt.hist(client_rtts, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='c')

plt.xlabel('RTT [ms]')
plt.ylabel('frequency []')
plt.legend(['spinbit', 'server', 'client'])
plt.title("RTT values as reported by spinbit observer, server and client")

plt.savefig("{}_rtt-hystogram.png".format(output_prefix))

##
## PLOT VERSUS_TIME
##

def makeTicks(series, upper = 100):
	interval = float(upper) / len(series)
	return [i*interval for i in range(0, len(series))]

#plot_fig = plt.figure()
datasets = (ping_rtts, spinbit_rtts, server_rtts, server_rtts_smooth,  client_rtts, client_rtts_smooth)
legend_data = ['ping client->server', 'spinbit', 'server', 'server smooth', 'client', 'client smooth', ]
formats = ['b', 'y', 'm', 'm', 'c', 'c']

f, axarr = plt.subplots(len(datasets))
f.set_size_inches(20, 9)
axarr[0].set_title("Different forms of RTT measurement versus time")

for i in range(0, len(datasets)):
	line = axarr[i].plot(datasets[i], formats[i])
	axarr[i].set_ylabel("RTT [ms]")
	axarr[i].legend([legend_data[i]], loc = 2)
	axarr[i].set_ylim([35,100])

plt.savefig("{}_time_vs_rtt.png".format(output_prefix))

##
## PLOT SMOOTH
##

plt.figure()

plot_bins = [i for i in range(35, 101)]

n, bins, patches = plt.hist(spinbit_rtts, plot_bins, (35, 100), True, stacked=True, alpha = 0.7, color='y')
n, bins, patches = plt.hist(server_rtts_smooth, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='m')
n, bins, patches = plt.hist(client_rtts_smooth, plot_bins, (35, 100), True, stacked = True, alpha = 0.7, color='c')

plt.xlabel('RTT [ms]')
plt.ylabel('frequency []')
plt.legend(['spinbit', 'server smooth', 'client smooth'])
plt.title("RTT values as reported by spinbit observer, server and client")

plt.savefig("{}_rtt-hystogram-smooth.png".format(output_prefix))



