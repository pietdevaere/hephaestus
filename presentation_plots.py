#!/usr/bin/python3
import analyze_vpp

import matplotlib.pyplot as plt
from matplotlib.markers import *
plt.style.use('ggplot')

RED =    "#E24A33"
BLUE =   "#348ABD"
PURPLE = "#988ED5"
GRAY =   "#777777"
YELLOW = "#FBC15E"
GREEN =  "#8EBA42"
PINK =   "#FFB5B8"

COLORS = (RED, BLUE, YELLOW, GREEN, PINK, PURPLE, GRAY)
MARKERS = ("o", "v", 's', 'p', 'D', 'x', "*", "h", "8", "1")

PLOT_DIR = "/home/piet/eth/msc/presentation/plots/"

def cm2inch(value):
    return value/2.54

def set_fig_size(f, x, y):
	f.set_size_inches(cm2inch(x), cm2inch(y))

def save_figure(figure, filename):
	print("\tGenerating figure: {} ...".format(filename), end="")
	figure.savefig(PLOT_DIR + "{}.pdf".format(filename))
	#figure.savefig(PLOT_DIR + "{}.svg".format(filename))
	figure.savefig(PLOT_DIR + "{}.png".format(filename))
	print("Done")

###
### SLIDE: Basic spinbit result
###

r_cc = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/std_congestion_controller_10ms_80s/1520177626-mQzsO_delay-10ms")
#r_delay_1ms = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/one_direction_10ms_80s/1520172327-7y4Rk_delay-1ms")


## ECDF

# Just plot the result of the basic analyzer ECDF

f, ax = plt.subplots(1)
set_fig_size(f, 10, 7.5)
#f.set_size_inches(10, 7)
x_limits = (-20, 20)

x, y = analyze_vpp.make_ecdf_data(r_cc, 'basic')

ax.plot(x, y)
ax.set_xlim(x_limits)
#ax.set_xlabel("Spin bit RTT - client reported RTT")
#ax.set_ylabel("Relative cumulative frequency")

save_figure(f, "basic_ecdf")

## TIME SERIE
f, ax = plt.subplots(1)
set_fig_size(f, 20, 6)
ax.plot(r_cc['server_times'], r_cc['server_rtts'], label="Server")
ax.plot(r_cc['client_times'], r_cc['client_rtts'], label="Client")
#ax.plot(r_cc['ping_times'], r_cc['ping_rtts'], label="Ping")


x, y, rejected = analyze_vpp.make_analyzer_data(r_cc, 'basic')
ax.plot(x, y, label="Spin bit")
ax.set_xlim((60, 100))
ax.set_ylim((35, 140))
ax.set_yticks((40, 80, 120))
ax.set_xticks((60, 100))
ax.legend(loc='upper left')
f.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.15)

save_figure(f, "basic_time")



###
### SLIDE: Influence of congestion window size
###

r_w20 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/window_20_10ms_80s/1520245309-LbJsm_delay-10ms/")
r_w40 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/window_40_10ms_80s/1520237764-PLHeq_delay-10ms/")
r_w60 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/window_60_10ms_80s/1520254781-FREym_delay-10ms/")

f, ax = plt.subplots(1)

x20, y20 = analyze_vpp.make_ecdf_data(r_w20, 'basic')
x40, y40 = analyze_vpp.make_ecdf_data(r_w40, 'basic')
x60, y60 = analyze_vpp.make_ecdf_data(r_w60, 'basic')
xcc, ycc = analyze_vpp.make_ecdf_data(r_cc, 'basic')

ax.plot(x20, y20, label='20 Packets')
ax.plot(x40, y40, label='40 Packets')
ax.plot(x60, y60, label='60 Packets')
ax.plot(xcc, ycc, label='CC')

set_fig_size(f, 10, 8)
f.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
plt.xlim((-20, 20))
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
ax.set_xticks((-20, -10, 0, 10, 20))

plt.legend()
save_figure(f, "window_sizes_ecdf")

###
### SLIDE: Influence of reordering.
###

f, ax = plt.subplots(1)
data_interval = (90, 150)

r_w60_reorder = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/window_60_10ms_80s/1520257101-GOHtN_delay-1ms-reorder-50-25")

to_plot = (
		   (r_w60, 'basic', 'Vanilla w/o reordering'),
		   (r_w60_reorder, 'basic', 'Vanilla'),
		   (r_w60_reorder, 'stat_heur', 'Heuristic'),
		   (r_w60_reorder, 'pn', 'With packet number'),
		   (r_w60_reorder, 'two_bit', 'Two bit spin'),
		   (r_w60_reorder, 'valid_edge', 'With edge bit'),
		#   (r_w60_reorder, 'status', 'status'),
		#   (r_w60_reorder, 'status', 'Status'),
		   )

for i in range(len(to_plot)):
	x, y = analyze_vpp.make_ecdf_data(to_plot[i][0], to_plot[i][1], data_interval)
	ax.plot(x, y,
			label=to_plot[i][2],
			color = COLORS[i-1],
			linewidth = 1,

			marker = MARKERS[i],
			markevery = (0.025*i, 0.1),
			markeredgecolor = COLORS[i-1],
			markerfacecolor = (0,0,0,0))

set_fig_size(f, 16, 9)
f.subplots_adjust(left=0.1, right=0.90, top=0.95, bottom=0.1)
ax.legend()
ax.set_xlim((-60, 20))
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))


save_figure(f, "reordering")

###
### SLIDE: Influence burst loss WINDOW SIZE
###

f, ax = plt.subplots(1)
data_interval = (90, 150)


r_w20_burst = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/window_20_10ms_80s/1520248518-4Wjqn_loss-gemodel-1-10-100-0.1")
r_w40_burst = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/window_40_10ms_80s/1520240973-ABN1n_loss-gemodel-1-10-100-0.1")
r_w60_burst = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/window_60_10ms_80s/1520258531-TFuc0_loss-gemodel-0.1-10-100-0.1/")
r_cc_burst = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/std_congestion_controller_10ms_80s/1520180839-2S3cd_loss-gemodel-1-10-100-0.1")

to_plot = (
		   (r_w20_burst, 'basic', '20 Packets'),
		   (r_w40_burst, 'basic', '40 Packets'),
		   (r_w60_burst, 'basic', '60 Packets'),
		   (r_cc_burst, 'basic', 'CC'),
		 #  (r_w40, 'basic', 'w60 nl'),
		 #  (r_w60_burst, 'status', 'W60 status'),
		#   (r_w60_reorder, 'status', 'status'),
		#   (r_w60_reorder, 'status', 'Status'),
		   )

for i in range(len(to_plot)):
	x, y = analyze_vpp.make_ecdf_data(to_plot[i][0], to_plot[i][1], data_interval)
	ax.plot(x, y,
			label=to_plot[i][2],
			color = COLORS[i],
			linewidth = 1,

			marker = MARKERS[i],
			markevery = (0.025*i, 0.1),
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

set_fig_size(f, 16, 9)
f.subplots_adjust(left=0.1, right=0.90, top=0.95, bottom=0.1)

ax.set_xlim((-20, 20))
ax.legend()
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))

save_figure(f, "burst_loss_vs_window_sizes")

###
### SLIDE: Influence burst loss SOLUTIONS
###

f, ax = plt.subplots(1)
data_interval = (90, 150)

to_plot = (
		   (r_w20, 'basic', 'Vanilla w/o loss'),
		   (r_w20_burst, 'basic', 'Vanilla'),
		   (r_w20_burst, 'valid_edge', 'With edge bit'),
		   (r_w20_burst, 'status', 'With handshake bits'),
		   )

for i in range(len(to_plot)):
	x, y = analyze_vpp.make_ecdf_data(to_plot[i][0], to_plot[i][1], data_interval)
	ax.plot(x, y,
			label=to_plot[i][2],
			color = COLORS[i-1],
			linewidth = 1,

			marker = MARKERS[i],
			markevery = (0.025*i, 0.1),
			markeredgecolor = COLORS[i-1],
			markerfacecolor = (0,0,0,0))

set_fig_size(f, 16, 9)
f.subplots_adjust(left=0.1, right=0.90, top=0.95, bottom=0.1)

ax.set_xlim((-10, 20))
ax.legend()
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))

save_figure(f, "burst_loss_solutions")

###
### SLIDE: bursty traffic, ECDF
###

r_cc_bursty_traffic = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/std_congestion_controller_10ms_80s/1520181557-sqYqt_bursty_traffic")

f, ax = plt.subplots(1)
data_interval = (10, 70)

to_plot = (
		   (r_cc_bursty_traffic, 'basic', 'Vanilla'),
		   (r_cc_bursty_traffic, 'valid_edge', 'With edge bit'),
		   (r_cc_bursty_traffic, 'valid_edge', 'With handshake bits'),
		   #(r_cc_bursty_traffic, 'status', 'With handshake bits'),
		   )

for i in range(len(to_plot)):
	x, y = analyze_vpp.make_ecdf_data(to_plot[i][0], to_plot[i][1], data_interval)
	ax.plot(x, y,
			label=to_plot[i][2],
			color = COLORS[i-1],
			linewidth = 1,

			marker = MARKERS[i],
			markevery = (0.025*i, 0.1),
			markeredgecolor = COLORS[i-1],
			markerfacecolor = (0,0,0,0))

set_fig_size(f, 20, 5)
f.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)

ax.set_xlim((-10, 10))
ax.legend()
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
ax.set_xticks((-10, -5, 0, 5, 10))

save_figure(f, "bursty_traffic_ecdf")

### TIME series

colors = (GREEN, GRAY, RED, YELLOW, BLUE, PINK, PURPLE, GRAY)


f, ax = plt.subplots(1)
set_fig_size(f, 20, 4)

#ax.plot(r_cc['ping_times'], r_cc['ping_rtts'], label="Ping")
to_plot = (
		   (r_cc_bursty_traffic, 'client', 'Client'),
		   (r_cc_bursty_traffic, 'basic', 'Vanilla'),
		   (r_cc_bursty_traffic, 'valid_edge', 'with edge bit'),
		   #(r_cc_bursty_traffic, 'status', 'With handshake bits'),
		   )

for i in range(len(to_plot)):

	if to_plot[i][1] in ('client', 'server', 'ping'):
		x = to_plot[i][0][to_plot[i][1]+'_times']
		y = to_plot[i][0][to_plot[i][1]+'_rtts']
		reject = list()
	else:
		x, y, reject = analyze_vpp.make_analyzer_data(to_plot[i][0], to_plot[i][1])

	ax.plot(x, y,
			label=to_plot[i][2],
			color = colors[i],
			linewidth = 1,
			)

ax.set_xlim((10, 40))
ax.set_ylim((35, 100))
ax.set_yticks((40, 80))
ax.set_xticks((10, 40))
ax.legend(loc='lower right')
f.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)

save_figure(f, "bursty_trafic_time")
