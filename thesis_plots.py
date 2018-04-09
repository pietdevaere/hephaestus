#!/usr/bin/python3
import analyze_vpp

import math
import matplotlib.pyplot as plt
from matplotlib.markers import *
import pickle
import collections
#plt.style.use(['seaborn-deep', 'seaborn-paper'])
#plt.style.use('ggplot')
#plt.style.use('seaborn-deep')


RED =    "#E24A33"
BLUE =   "#348ABD"
PURPLE = "#988ED5"
GRAY =   "#777777"
YELLOW = "#FBC15E"
GREEN =  "#8EBA42"
PINK =   "#FFB5B8"

RED =    "#C44E52"
BLUE =   "#4C72B0"
PURPLE = "#8172B2"
GRAY =   "#777777"
YELLOW = "#CCB974"
GREEN =  "#55A868"
LIGHT_BLUE =   "#64B5CD"

COLORS = (RED, BLUE, YELLOW, GREEN, PINK, PURPLE, GRAY)
#COLORS = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD', GRAY]
MARKERS    = (("o", 6), ('s', 6), ("v", 6), ("^", 6), ('p', 6), ('D', 5), ('x', 6), ("+", 6), ("8", 6), ("h", 6))
#MARKERS = list((('${}$'.format(x), 6) for x in 'ABCDEFGHI'))
#MARKERS = (((0, 3, 0),   8),
		   #((3, 0, 0),   8),
		   #((3, 0, -90), 8),
		   #((4, 0, 0),   8),
		   #((4, 0, 45),  8),
		   #((5, 0, 0),   8),
		   #((8, 2, 0),   8),
		   #)

GRIDLINEPROPS = {'linewidth': 0.75, 'color': (0.9, 0.9, 0.9)}



PLOT_DIR = "/home/piet/eth/msc/thesis/plots/"

def cm2inch(value):
    return value/2.54

def set_fig_size(f, x, y):
	f.set_size_inches(cm2inch(x), cm2inch(y))

params = {
   'figure.figsize' : "{}, {}".format(cm2inch(16.18), cm2inch(10)),
   'axes.labelsize': 9,
   'text.fontsize': 9,
   'legend.fontsize': 8,
   'xtick.labelsize': 9,
   'ytick.labelsize': 9,
   'text.usetex': False,
   'markers.fillstyle': 'none',
   'legend.fancybox': False,
   'legend.facecolor': '0.9',
   'legend.edgecolor': '0.9',
   'legend.frameon': True,
   'axes.linewidth': 1,
   'axes.grid': 0,
   'grid.color': '0.9',
   'grid.linestyle': '-',
   'grid.linewidth': '.75',
   'axes.spines.left' : True,
   'axes.spines.bottom' : True,
   'axes.spines.top' : False,
   'axes.spines.right' : False,
   'axes.unicode_minus'  : True,

   }
rcParams.update(params)


INTERVAL_OF_INTEREST = (90,150)

analyzer_names = ["basic", "pn", "pn_valid", "valid", "pn_valid_edge",
						"valid_edge", 'status', "two_bit", "stat_heur", "rel_heur", "handshake"]

analyzers_to_plot = (("basic", "Basic"),
					 ("pn", "Packet number"),
					 ("stat_heur", "Static heur."),
					 ("rel_heur", "Dynamic heur."),
					 ("two_bit", "Two bit spin"),
					 ("valid_edge", "Valid edge"),
					 ("status", "VEC"),
					)

def cm2inch(value):
    return value/2.54

def set_fig_size(f, x, y):
	f.set_size_inches(cm2inch(x), cm2inch(y))

def save_figure(figure, filename):
	print("\tGenerating figure: {} ...".format(filename), end="")
	figure.savefig(PLOT_DIR + "{}.pdf".format(filename))
	#figure.savefig(PLOT_DIR + "{}.svg".format(filename))
	figure.savefig(PLOT_DIR + "{}.png".format(filename))
	pickle.dump(figure, open(PLOT_DIR + "{}.fig.pickle".format(filename), 'wb'))
	plt.close(figure)
	print("Done")

def count_valid_edges_endpoint(mbytes, mtimes, interval = None):
	counter = 0
	for i in range(len(mbytes)):
		time = mtimes[i]
		byte = mbytes[i]
		if interval and not (time > interval[0] and time < interval[1]):
			continue
		if byte & 0x01:
			counter += 1

	return counter

def count_samples_observer(run, analyzer, interval = None):
	counter = 0
	times, rtts, times_rej = analyze_vpp.make_analyzer_data(run, analyzer)
	for time in times:
		if time > interval[0] and time < interval[1]:
			counter += 1
	return counter

##############################################################################
#### BASIC SPIN RESULT
##############################################################################

r_cc_delay_10 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522403057-3JiB8_cc_delay-10ms")

f, ax = plt.subplots(1)
ax.axhline(80, **GRIDLINEPROPS)
ax.axhline(40, **GRIDLINEPROPS)


ax.plot(r_cc_delay_10['server_times'], r_cc_delay_10['server_rtts'], label="Server", color = PURPLE)
ax.plot(r_cc_delay_10['client_times'], r_cc_delay_10['client_rtts'], label="Client", color = YELLOW)

x, y, rejected = analyze_vpp.make_analyzer_data(r_cc_delay_10, 'basic')
ax.plot(x, y, label="Spin bit (basic)", color = RED)
ax.set_xlim((70, 90))
ax.set_ylim((35, 140))
ax.set_xticks((70, 75, 80, 85, 90))
ax.set_xlabel("Time [s]")
ax.set_ylabel("RTT [ms]")
ax.legend()
#ax.grid(True)
save_figure(f, "basic_cc_time")

##############################################################################
#### BURSTY TRAFFIC
##############################################################################

r_cc_bursty = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522414307-Tl8ax_cc_bursty_traffic_100_5")

f, ax = plt.subplots(1)


ax.plot(r_cc_bursty['client_times'], r_cc_bursty['client_rtts'], label="Client", color = YELLOW)


x, y, rejected_x = analyze_vpp.make_analyzer_data(r_cc_bursty, 'basic')
ax.plot(x, y, label="Basic", color = RED)
x, y, rejected_x = analyze_vpp.make_analyzer_data(r_cc_bursty, 'valid_edge')

rejected_y = [None for x in rejected_x]
x = x + rejected_x
y = y + rejected_y
x, y = zip(*sorted(zip(x,y)))

ax.plot(x, y, label="Valid edge", color = PURPLE)
ax.set_xlim((100, 115))
ax.set_ylim((35, 120))
#ax.set_xticks((70, 75, 80, 85, 90))
ax.set_xlabel("Time [s]")
ax.set_ylabel("RTT [ms]")
ax.legend()
#ax.grid(True)
save_figure(f, "bursty_traffic_cc")


##############################################################################
#### ECDF SHOWING INFLUENCE OF DIFFERENT PACKET SCHEDULERS
##############################################################################

ps_plot_interval = (15, 75)

r_cc_delay_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522399850-Cbe8b_cc_delay-5ms")
r_w50_delay_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522223664-dftfx_w50_delay-5ms")
r_1r5_delay_0  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523032863-NTne9_1r5_delay-0")

runs_to_plot = (
				(r_cc_delay_5, "Dynamic window (CC)"),
				(r_w50_delay_5, "50 packet window"),
				(r_1r5_delay_0, "1.5 MBps pacer"),
			    )

f, ax = plt.subplots(1)
#ax.axhline(0.5, **GRIDLINEPROPS)
ax.axvline(0, **GRIDLINEPROPS)
#ax.axvline(1, **GRIDLINEPROPS)


for i in range(len(runs_to_plot)):
	run, label = runs_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run, 'basic', ps_plot_interval)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markevery = (0.1*i, 0.2))

ax.legend(title="Packet scheduler")
ax.set_xlim((-15, 15))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.grid(True)
save_figure(f, "scheduler_effect_ecdf")


##############################################################################
#### ECDF SHOWING INFLUENCE OF WINDOW
##############################################################################

r_cc_delay_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522399850-Cbe8b_cc_delay-5ms")
r_w10_delay_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522222982-cP3rG_w10_delay-5ms")
r_w20_delay_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522227153-KOfPB_w20_delay-5ms")
r_w30_delay_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522223166-Ry0sh_w30_delay-5ms")
r_w40_delay_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522223390-Llxqm_w40_delay-5ms")
r_w50_delay_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522223664-dftfx_w50_delay-5ms")
r_w60_delay_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522223858-1vndu_w60_delay-5ms")

runs_to_plot = (
				(r_w10_delay_5, "10 packets"),
				(r_w20_delay_5, "20 packets"),
				#(r_w30_delay_5, "30 packets"),
				(r_w40_delay_5, "40 packets"),
				#(r_w50_delay_5, "50 packets"),
				(r_w60_delay_5, "60 packets"),
				#(r_cc_delay_5,  "Dynamic"),
			    )

f, ax = plt.subplots(1)
#ax.axhline(0.5, **GRIDLINEPROPS)
ax.axvline(0, **GRIDLINEPROPS)


for i in range(len(runs_to_plot)):
	run, label = runs_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run, 'basic', ps_plot_interval)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markevery = (0.1*i, 0.2))

ax.legend(title="Window size")
ax.set_xlim((-15, 15))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.grid(True)
save_figure(f, "window_effect_basic")


##############################################################################
#### EFFECT OF REORDERING
##############################################################################

#r_w60_delay_1     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522152222-QLvJW_w60_delay-1ms")
#r_w60_reorder_1   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522151325-usEce_w60_delay-1ms-reorder-1")
#r_w60_reorder_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522151502-7cCvD_w60_delay-1ms-reorder-5")
#r_w60_reorder_10  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521968715-EJ9xZ_W60_delay-1ms-reorder-10")
#r_w60_reorder_20  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521968894-gp4H7_W60_delay-1ms-reorder-20")
#r_w60_reorder_30  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521969072-l7rKA_W60_delay-1ms-reorder-30")
#r_w60_reorder_40  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521969251-Uwiwn_W60_delay-1ms-reorder-40")

r_w60_delay_1     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522827221-bHosL_w60_delay-1ms")
r_w60_reorder_1   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522826145-R1EMm_w60_delay-1ms-reorder-1")
r_w60_reorder_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522826321-AUuPr_w60_delay-1ms-reorder-5")
r_w60_reorder_10  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522826501-QkHFG_w60_delay-1ms-reorder-10")
r_w60_reorder_20  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522826681-LJBr8_w60_delay-1ms-reorder-20")
r_w60_reorder_30  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522826861-wXE4m_w60_delay-1ms-reorder-30")
r_w60_reorder_40  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522827043-BdV25_w60_delay-1ms-reorder-40")

runs_to_plot = ((r_w60_delay_1, 0),
				(r_w60_reorder_1, 1),
				(r_w60_reorder_5, 5),
				(r_w60_reorder_10, 10),
				(r_w60_reorder_20, 20),
				(r_w60_reorder_30, 30),
				(r_w60_reorder_40, 40),
			   )


##
## ECDF for a single loss reorederin rate
##

run_for_ecdf = r_w60_reorder_40

f, ax = plt.subplots(1)
#ax.axhline(0.5, **GRIDLINEPROPS)
ax.axvline(0, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run_for_ecdf, analyzer, INTERVAL_OF_INTEREST)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markevery = (0.1*i, 0.2))

ax.legend()
ax.set_xlim((-55, 15))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.grid(True)
save_figure(f, "reordering_w60_ECDF")


##
## Do analyzer error over various reoerder rates
##

X_VALUE_TO_CMP = 20

f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, reorder_grade in runs_to_plot:
		y_val = analyze_vpp.find_ecdf_y_value(run, analyzer, abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST) - \
				analyze_vpp.find_ecdf_y_value(run, analyzer, -abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST)
		y_values.append(y_val)
		x_values.append(reorder_grade)

	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(x_values)
ax.set_xlabel("Packet reordering rate [%]")
ax.set_ylabel("Fraction of samples with |error| < 10 ms")
#ax.grid(True)
save_figure(f, "reordering_w60_effect_error")

##
## Do analyzer valid samples over various loss rates
##
f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, reorder_grade in runs_to_plot:
		valid_edges = 0
		valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
												  run['server_mtimes'],
												  INTERVAL_OF_INTEREST)
		valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
												  run['client_mtimes'],
												  INTERVAL_OF_INTEREST)
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)
		y_values.append(sampled_edges/valid_edges)
		x_values.append(reorder_grade)
		#print(reorder_grade, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend(loc='upper left')
ax.set_xticks(x_values)
ax.set_xlabel("Packet reordering rate [%]")
ax.set_ylabel("Edges sampled / valid edges transmitted")
#ax.grid(True)
save_figure(f, "reordering_w60_effect_samples")

##
## Do analyzer valid samples over various loss rates, absolute numbers
##
f, ax = plt.subplots(1)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, reorder_grade in runs_to_plot:
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)
		y_values.append(sampled_edges)
		x_values.append(reorder_grade)
		#print(reorder_grade, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend(loc='upper left')
ax.set_xticks(x_values)
ax.set_xlabel("Packet reordering rate [%]")
ax.set_ylabel("Edges sampled")
#ax.grid(True)
save_figure(f, "reordering_w60_effect_samples_absolute")

##############################################################################
#### EFFECT OF JITTER
##############################################################################

print("== Moving on to JITTER==")

r_w60_delay_5       = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522223858-1vndu_w60_delay-5ms")
r_w60_delay_5_1     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522224035-YJX6d_w60_delay-5ms-1ms")
r_w60_delay_5_2     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522224214-dlybj_w60_delay-5ms-2ms")
r_w60_delay_5_3     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522224394-D3gBk_w60_delay-5ms-3ms")
r_w60_delay_5_4     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522224575-WA47J_w60_delay-5ms-4ms")
r_w60_delay_5_5     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522224754-w3fz4_w60_delay-5ms-5ms")

#r_w60_delay_5       = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522828597-jfFTp_w60_delay-5ms")
#r_w60_delay_5_1     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522827401-wBrXn_w60_delay-5ms-1ms")
#r_w60_delay_5_2     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522827580-bEnDX_w60_delay-5ms-2ms")
#r_w60_delay_5_3     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522827759-OzzHf_w60_delay-5ms-3ms")
#r_w60_delay_5_4     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522827938-OgBjg_w60_delay-5ms-4ms")
#r_w60_delay_5_5     = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522828116-Q3mTJ_w60_delay-5ms-5ms")


runs_to_plot = ((r_w60_delay_5,   0),
				(r_w60_delay_5_1, 1),
				(r_w60_delay_5_2, 2),
				(r_w60_delay_5_3, 3),
				(r_w60_delay_5_4, 4),
				(r_w60_delay_5_5, 5),
			   )

##
## ECDF for a single jitter rate
##

run_for_ecdf = r_w60_delay_5_1

f, ax = plt.subplots(1)
ax.axvline(0, **GRIDLINEPROPS)
#ax.axhline(0.5, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run_for_ecdf, analyzer, INTERVAL_OF_INTEREST)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markeredgewidth = 1,
			markevery = (0.015*i, 0.2))

ax.legend(loc='upper left')
ax.set_xlim((-65, 15))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.grid(True, axis='both')
#ax.spines['top'].set_visible(False)
#ax.spines['right'].set_visible(False)
#ax.spines['left'].set_visible(False)
save_figure(f, "jitter_w60_ECDF")

##
## Do analyzer error over various loss rates
##

X_VALUE_TO_CMP = 10

f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, reorder_grade in runs_to_plot:
		high = analyze_vpp.find_ecdf_y_value(run, analyzer, abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST)
		low = analyze_vpp.find_ecdf_y_value(run, analyzer, -abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST)
		y_val = high - low
		y_values.append(y_val)
		x_values.append(reorder_grade)
		#print("ERROR analyzer: {}, jitter: {} ms, X: {} ms, {} - {} = {}".format(analyzer, reorder_grade, X_VALUE_TO_CMP, high, low, high-low))


	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(x_values)
ax.set_xlabel("Jitter [ms]")
ax.set_ylabel("Fraction of samples with |error| < 10 ms")
#ax.grid(True)
save_figure(f, "jitter_w60_effect_error")

##
## Do analyzer valid samples over various loss rates
##
f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, reorder_grade in runs_to_plot:
		valid_edges = 0
		valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
												  run['server_mtimes'],
												  INTERVAL_OF_INTEREST)
		valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
												  run['client_mtimes'],
												  INTERVAL_OF_INTEREST)
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		y_values.append(sampled_edges/valid_edges)
		x_values.append(reorder_grade)
		#print(reorder_grade, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

#valid_edges = 0
#valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
											#run['server_mtimes'],
											#INTERVAL_OF_INTEREST)
#valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
											#run['client_mtimes'],
											#INTERVAL_OF_INTEREST)
#sampled_edges = count_samples_observer(r_w60_delay_5_5, 'status', INTERVAL_OF_INTEREST)
#status_d5_5_value = sampled_edges / valid_edges

#valid_edges = 0
#valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
											#run['server_mtimes'],
											#INTERVAL_OF_INTEREST)
#valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
											#run['client_mtimes'],
											#INTERVAL_OF_INTEREST)
#sampled_edges = count_samples_observer(r_w60_delay_5_5, 'valid_edge', INTERVAL_OF_INTEREST)
#valid_edge_d5_5_value = sampled_edges / valid_edges

ax.text(3.8, 0.3, "VEC: 0.020")
ax.text(3.8, 0.5, "Valid edge: 0.004")
ax.arrow(4.7, 0.35, 0.12, -0.15, width=0.005, head_width=0.06, facecolor=(0,0,0,1))


#ax.annotate("VEC: {:.3}".format(status_d5_5_value), xy=(5-0.1, status_d5_5_value+0.1), xytext=(4, 0.3),
							#arrowprops=dict(facecolor='black', shrink=0.05, width=.5, headwidth=3, headlength=5))

#ax.annotate("Valid edge: {:.3}".format(valid_edge_d5_5_value), xy=(5, valid_edge_d5_5_value), xytext=(4, 0.5))

ax.legend(loc='upper left')
ax.set_xticks(x_values)
ax.set_xlabel("Jitter [ms]")
ax.set_ylabel("Edges sampled / valid edges transmitted")
#ax.grid(True)
ax.set_ylim((0, None))
save_figure(f, "jitter_w60_effect_samples")

##
## Do analyzer valid samples over various loss rates, ABSOLUTE
##
f, ax = plt.subplots(1)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, reorder_grade in runs_to_plot:
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		y_values.append(sampled_edges)
		x_values.append(reorder_grade)
		#print(reorder_grade, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend(loc='upper left')
ax.set_xticks(x_values)
ax.set_xlabel("Jitter [ms]")
ax.set_ylabel("Edges sampled")
#ax.grid(True)
ax.set_ylim((0, None))
save_figure(f, "jitter_w60_effect_samples_absolute")






##############################################################################
#### EFFECT OF BURST LOSS, WINDOW
##############################################################################

#r_w20_delay_0        = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522226977-dcdQK_w20_delay-0")
#r_w20_loss_burst_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522059294-aY3mB_w20_loss-gemodel-1-5")
#r_w20_loss_burst_7   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522225364-kMGrD_w20_loss-gemodel-1-7")
#r_w20_loss_burst_8   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522225541-6pqI3_w20_loss-gemodel-1-8")
#r_w20_loss_burst_10  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522059469-NaYHc_w20_loss-gemodel-1-10")
#r_w20_loss_burst_15  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522059647-Dr6iA_w20_loss-gemodel-1-15")
#r_w20_loss_burst_20  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522059825-q4sk8_w20_loss-gemodel-1-20")
#r_w20_loss_burst_25  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522060003-8EYWc_w20_loss-gemodel-1-25")
#r_w20_loss_burst_30  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522060180-MFR1d_w20_loss-gemodel-1-30")

r_w20_delay_0        = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522831927-4bloa_w20_delay-0")
r_w20_loss_burst_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522829244-6MCCk_w20_loss-gemodel-1-5")
r_w20_loss_burst_7   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522829423-fElX0_w20_loss-gemodel-1-7")
r_w20_loss_burst_8   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522829602-CqHLQ_w20_loss-gemodel-1-8")
r_w20_loss_burst_10  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522829781-mZovb_w20_loss-gemodel-1-10")
r_w20_loss_burst_15  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522829960-KHXoA_w20_loss-gemodel-1-15")
r_w20_loss_burst_20  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522830140-EE0id_w20_loss-gemodel-1-20")
r_w20_loss_burst_25  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522830318-1z2kQ_w20_loss-gemodel-1-25")
r_w20_loss_burst_30  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522830498-wiUkE_w20_loss-gemodel-1-30")


#r_1r5_loss_burst_15 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522092116-oKbY1_1r5_loss-gemodel-1-15")
#r_1r5_loss_burst_20 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522092295-mpzYr_1r5_loss-gemodel-1-20")
#r_1r5_loss_burst_25 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522092476-AIGYO_1r5_loss-gemodel-1-25")
#r_1r5_loss_burst_30 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522092656-sTpjo_1r5_loss-gemodel-1-30")

runs_to_plot = (
				(r_w20_delay_0, math.inf),
				(r_w20_loss_burst_30, 30),
				(r_w20_loss_burst_25, 25),
				(r_w20_loss_burst_20, 20),
				(r_w20_loss_burst_15, 15),
				(r_w20_loss_burst_10, 10),
				(r_w20_loss_burst_8, 8),
				(r_w20_loss_burst_7, 7),
				(r_w20_loss_burst_5, 5),
			   )

##
## ECDF for a single burst loss rate
##

run_for_ecdf = r_w20_loss_burst_10

f, ax = plt.subplots(1)
#ax.axhline(0.5, **GRIDLINEPROPS)
ax.axvline(0, **GRIDLINEPROPS)


for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run_for_ecdf, analyzer, INTERVAL_OF_INTEREST)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markevery = (0.1*i, 0.2))

ax.legend()
ax.set_xlim((-10, 30))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.set_ylim((-0.01,1.01))
#ax.grid(True)
save_figure(f, "loss_burst_w20_ECDF")

##
## Do analyzer error over various loss rates
##

X_VALUE_TO_CMP = 10
GOOD_LENGTH = 100
X_TICKS = (0, 5, 10, 15, 20)

f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		y_val = analyze_vpp.find_ecdf_y_value(run, analyzer, abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST) - \
				analyze_vpp.find_ecdf_y_value(run, analyzer, -abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST)
		y_values.append(y_val)
		burst_length = 1 / (burst_parameter / 100)
		x_values.append(burst_length)

	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Fraction of samples with |error| < 10 ms")
#ax.grid(True)
save_figure(f, "loss_burst_w20_effect_error")

##
## Do analyzer valid samples over various loss rates
##
f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		valid_edges = 0
		valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
												  run['server_mtimes'],
												  INTERVAL_OF_INTEREST)
		valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
												  run['client_mtimes'],
												  INTERVAL_OF_INTEREST)
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		burst_length = 1 / (burst_parameter / 100)
		#loss_rate = burst_length / (burst_length + GOOD_LENGTH)

		y_values.append(sampled_edges/valid_edges)
		x_values.append(burst_length)
		#print(burst_parameter, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Edges sampled / valid edges transmitted")
#ax.grid(True)
save_figure(f, "loss_burst_w20_effect_samples")

##
## Do analyzer valid samples over various loss rates, absolute numbers
##
f, ax = plt.subplots(1)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		burst_length = 1 / (burst_parameter / 100)
		#loss_rate = burst_length / (burst_length + GOOD_LENGTH)

		y_values.append(sampled_edges)
		x_values.append(burst_length)
		#print(burst_parameter, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Edges sampled")
#ax.grid(True)
save_figure(f, "loss_burst_w20_effect_samples_absolute")

##############################################################################
#### EFFECT OF BURST LOSS RATE 1R5
##############################################################################

r_1r5_delay_0        = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523032863-NTne9_1r5_delay-0")
r_1r5_loss_burst_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523086323-yPsJs_1r5_loss-gemodel-1-5")
r_1r5_loss_burst_7   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523031628-0GbwW_1r5_loss-gemodel-1-7")
r_1r5_loss_burst_8   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523031803-xZQme_1r5_loss-gemodel-1-8")
r_1r5_loss_burst_10  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523031979-n133X_1r5_loss-gemodel-1-10")
r_1r5_loss_burst_15  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523032155-HS6pf_1r5_loss-gemodel-1-15")
r_1r5_loss_burst_20  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523032333-8xOg4_1r5_loss-gemodel-1-20")
r_1r5_loss_burst_25  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523032510-Q1DQW_1r5_loss-gemodel-1-25")
r_1r5_loss_burst_30  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523083607-4PQnb_1r5_loss-gemodel-1-30")


runs_to_plot = (
				(r_1r5_delay_0, math.inf),
				(r_1r5_loss_burst_30, 30),
				(r_1r5_loss_burst_25, 25),
				(r_1r5_loss_burst_20, 20),
				(r_1r5_loss_burst_15, 15),
				(r_1r5_loss_burst_10, 10),
				(r_1r5_loss_burst_8, 8),
				(r_1r5_loss_burst_7, 7),
				(r_1r5_loss_burst_5, 5),
			   )

##
## ECDF for a single burst loss rate
##

run_for_ecdf = r_1r5_loss_burst_10

f, ax = plt.subplots(1)
#ax.axhline(0.5, **GRIDLINEPROPS)
ax.axvline(0, **GRIDLINEPROPS)


for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run_for_ecdf, analyzer, INTERVAL_OF_INTEREST)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markevery = (0.1*i, 0.2))

ax.legend()
ax.set_xlim((-10, 30))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.set_ylim((-0.01,1.01))
#ax.grid(True)
save_figure(f, "loss_burst_1r5_ECDF")

##
## Do analyzer error over various loss rates
##

X_VALUE_TO_CMP = 10
GOOD_LENGTH = 100
X_TICKS = (0, 5, 10, 15, 20)

f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		y_val = analyze_vpp.find_ecdf_y_value(run, analyzer, abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST) - \
				analyze_vpp.find_ecdf_y_value(run, analyzer, -abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST)
		y_values.append(y_val)
		burst_length = 1 / (burst_parameter / 100)
		x_values.append(burst_length)

	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Fraction of samples with |error| < 10 ms")
#ax.grid(True)
save_figure(f, "loss_burst_1r5_effect_error")

##
## Do analyzer valid samples over various loss rates
##
f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		valid_edges = 0
		valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
												  run['server_mtimes'],
												  INTERVAL_OF_INTEREST)
		valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
												  run['client_mtimes'],
												  INTERVAL_OF_INTEREST)
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		burst_length = 1 / (burst_parameter / 100)
		#loss_rate = burst_length / (burst_length + GOOD_LENGTH)
		#print(sampled_edges, valid_edges)
		if sampled_edges != 0:
			y_values.append(sampled_edges/valid_edges)
		else:
			y_values.append(0)
		x_values.append(burst_length)
		#print(burst_parameter, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Edges sampled / valid edges transmitted")
#ax.grid(True)
save_figure(f, "loss_burst_1r5_effect_samples")

##
## Do analyzer valid samples over various loss rates ABSOLUTE
##
f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		burst_length = 1 / (burst_parameter / 100)
		#loss_rate = burst_length / (burst_length + GOOD_LENGTH)
		y_values.append(sampled_edges)
		x_values.append(burst_length)
		#print(burst_parameter, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Edges sampled")
#ax.grid(True)
save_figure(f, "loss_burst_1r5_effect_samples_absolute")

##############################################################################
#### EFFECT OF BURST LOSS RATE 0R6
##############################################################################

r_0r6_delay_0        = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523166429-m5D2D_0r6_delay-0")
r_0r6_loss_burst_5   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523165017-VEHV9_0r6_loss-gemodel-1-5")
r_0r6_loss_burst_7   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523165193-Mpm9k_0r6_loss-gemodel-1-7")
r_0r6_loss_burst_8   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523165370-lSD5D_0r6_loss-gemodel-1-8")
r_0r6_loss_burst_10  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523165546-lJYMt_0r6_loss-gemodel-1-10")
r_0r6_loss_burst_15  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523165722-DLsM6_0r6_loss-gemodel-1-15")
r_0r6_loss_burst_20  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523165899-wWySr_0r6_loss-gemodel-1-20")
r_0r6_loss_burst_25  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523171249-Y6BoF_0r6_loss-gemodel-1-25")
r_0r6_loss_burst_30  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1523166254-1gghL_0r6_loss-gemodel-1-30")


runs_to_plot = (
				(r_0r6_delay_0, math.inf),
				(r_0r6_loss_burst_30, 30),
			#	(r_0r6_loss_burst_25, 25),
				(r_0r6_loss_burst_20, 20),
				(r_0r6_loss_burst_15, 15),
				(r_0r6_loss_burst_10, 10),
				(r_0r6_loss_burst_8, 8),
				(r_0r6_loss_burst_7, 7),
				(r_0r6_loss_burst_5, 5),
			   )

##
## ECDF for a single burst loss rate
##

run_for_ecdf = r_0r6_loss_burst_10

f, ax = plt.subplots(1)
#ax.axhline(0.5, **GRIDLINEPROPS)
ax.axvline(0, **GRIDLINEPROPS)
#ax.axvline(1, **GRIDLINEPROPS)
#ax.axvline(2, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run_for_ecdf, analyzer, INTERVAL_OF_INTEREST)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markevery = (0.1*i, 0.2))

ax.legend()
ax.set_xlim((-10, 30))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.set_ylim((-0.01,1.01))
#ax.grid(True)
save_figure(f, "loss_burst_0r6_ECDF")

##
## Do analyzer error over various loss rates
##

X_VALUE_TO_CMP = 10
GOOD_LENGTH = 100
X_TICKS = (0, 5, 10, 15, 20)

f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		y_val = analyze_vpp.find_ecdf_y_value(run, analyzer, abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST) - \
				analyze_vpp.find_ecdf_y_value(run, analyzer, -abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST)
		y_values.append(y_val)
		burst_length = 1 / (burst_parameter / 100)
		x_values.append(burst_length)

	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Fraction of samples with |error| < 10 ms")
#ax.grid(True)
save_figure(f, "loss_burst_0r6_effect_error")

##
## Do analyzer valid samples over various loss rates
##
f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		valid_edges = 0
		valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
												  run['server_mtimes'],
												  INTERVAL_OF_INTEREST)
		valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
												  run['client_mtimes'],
												  INTERVAL_OF_INTEREST)
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		burst_length = 1 / (burst_parameter / 100)
		#loss_rate = burst_length / (burst_length + GOOD_LENGTH)
		#print(sampled_edges, valid_edges)
		if sampled_edges != 0:
			y_values.append(sampled_edges/valid_edges)
		else:
			y_values.append(0)
		x_values.append(burst_length)
		#print(burst_parameter, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Edges sampled / valid edges transmitted")
#ax.grid(True)
save_figure(f, "loss_burst_0r6_effect_samples")

##
## Do analyzer valid samples over various loss rates ABSOLUTE
##
f, ax = plt.subplots(1)
#ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, burst_parameter in runs_to_plot:
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		burst_length = 1 / (burst_parameter / 100)
		#loss_rate = burst_length / (burst_length + GOOD_LENGTH)
		y_values.append(sampled_edges)
		x_values.append(burst_length)
		#print(burst_parameter, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Average burst length [packets]")
ax.set_ylabel("Edges sampled")
#ax.grid(True)
save_figure(f, "loss_burst_0r6_effect_samples_absolute")

##############################################################################
#### EFFECT OF RANDOM LOSS
##############################################################################

##TODO change this to w20

#r_w60_delay_0 = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522151683-RKtPJ_w60_delay-0")
#r_w60_loss_random_0L1  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521967820-4lnKj_W60_loss-random--0.1")
#r_w60_loss_random_0L5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521967999-xYT9g_W60_loss-random--0.5")
#r_w60_loss_random_1  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521968178-DeTgY_W60_loss-random--1")
#r_w60_loss_random_5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521968357-q6fc9_W60_loss-random--5")
#r_w60_loss_random_10  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1521968535-KOH5R_W60_loss-random--10")

#r_w20_delay_0          = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522226977-dcdQK_w20_delay-0")
#r_w20_loss_random_0L1  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522225721-JeqVJ_w20_loss-random--0.1")
#r_w20_loss_random_0L5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522225900-ty3h0_w20_loss-random--0.5")
#r_w20_loss_random_1    = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522226079-DV9rg_w20_loss-random--1")
#r_w20_loss_random_5    = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522226259-t2wFJ_w20_loss-random--5")
#r_w20_loss_random_10   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522226438-6BcTv_w20_loss-random--10")
#r_w20_loss_random_15   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522226617-4iG3E_w20_loss-random--15")
#r_w20_loss_random_20   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis/1522226797-LFRcD_w20_loss-random--20")

r_w20_delay_0          = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522831927-4bloa_w20_delay-0")
r_w20_loss_random_0L1  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522830677-Zv24C_w20_loss-random--0.1")
r_w20_loss_random_0L5  = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522830856-CvB6R_w20_loss-random--0.5")
r_w20_loss_random_1    = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522831035-v5TKt_w20_loss-random--1")
r_w20_loss_random_5    = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522831214-jPL8g_w20_loss-random--5")
r_w20_loss_random_10   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522831393-rHFxh_w20_loss-random--10")
r_w20_loss_random_15   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522831571-Um0dQ_w20_loss-random--15")
r_w20_loss_random_20   = analyze_vpp.analyze_run("/home/piet/eth/msc/vpp-data/for_thesis_new_vec/1522831749-ApnBE_w20_loss-random--20")

#runs_to_plot = ((r_w60_delay_0, 0),
				#(r_w60_loss_random_0L1, 0.1),
				#(r_w60_loss_random_0L5, 0.5),
				#(r_w60_loss_random_1, 1),
				#(r_w60_loss_random_5, 5),
				#(r_w60_loss_random_10, 10),
			   #)

runs_to_plot = ((r_w20_delay_0, 0),
#				(r_w20_loss_random_0L1, 0.1),
#				(r_w20_loss_random_0L5, 0.5),
				(r_w20_loss_random_1, 1),
				(r_w20_loss_random_5, 5),
				(r_w20_loss_random_10, 10),
				(r_w20_loss_random_15, 15),
				(r_w20_loss_random_20, 20),
			   )

##
## ECDF for a single burst loss rate
##

run_for_ecdf = r_w20_loss_random_10

f, ax = plt.subplots(1)
#ax.axhline(0.5, **GRIDLINEPROPS)
ax.axvline(0, **GRIDLINEPROPS)


for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	x_values, y_values = analyze_vpp.make_ecdf_data(run_for_ecdf, analyzer, INTERVAL_OF_INTEREST)
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0),
			markevery = (0.1*i, 0.2))

ax.legend()
ax.set_xlim((-15, 15))
ax.set_xlabel("Error [ms]")
ax.set_ylabel("Cumulative fraction of data")
ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
#ax.grid(True)
save_figure(f, "loss_random_w20_ECDF")

##
## Do analyzer error over various loss rates
##

X_VALUE_TO_CMP = 10
X_TICKS = (0, 5, 10, 15, 20)

f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)


for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, loss_rate in runs_to_plot:
		y_val = analyze_vpp.find_ecdf_y_value(run, analyzer, abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST) - \
				analyze_vpp.find_ecdf_y_value(run, analyzer, -abs(X_VALUE_TO_CMP), INTERVAL_OF_INTEREST)
		y_values.append(y_val)
		x_values.append(loss_rate)

	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_yticks((0.97, 0.98, 0.99, 1))
ax.set_xlabel("Loss rate [%]")
ax.set_ylabel("Fraction of samples with |error| < 10 ms")
#ax.grid(True)
save_figure(f, "loss_random_w20_effect_error")

##
## Do analyzer valid samples over various loss rates
##
f, ax = plt.subplots(1)
ax.axhline(1, **GRIDLINEPROPS)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, loss_rate in runs_to_plot:
		valid_edges = 0
		valid_edges += count_valid_edges_endpoint(run['server_mbytes'],
												  run['server_mtimes'],
												  INTERVAL_OF_INTEREST)
		valid_edges += count_valid_edges_endpoint(run['client_mbytes'],
												  run['client_mtimes'],
												  INTERVAL_OF_INTEREST)
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		y_values.append(sampled_edges/valid_edges)
		x_values.append(loss_rate)
		#print(loss_rate, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Loss rate [%]")
ax.set_ylabel("Edges sampled / valid edges transmitted")
#ax.grid(True)
save_figure(f, "loss_random_w20_effect_samples")

##
## Do analyzer valid samples over various loss rates, absoulte numbers
##
f, ax = plt.subplots(1)

for i in range(len(analyzers_to_plot)):
	analyzer, label = analyzers_to_plot[i]
	## First build the data series
	y_values = list()
	x_values = list()
	for run, loss_rate in runs_to_plot:
		sampled_edges = count_samples_observer(run, analyzer, INTERVAL_OF_INTEREST)

		y_values.append(sampled_edges)
		x_values.append(loss_rate)
		#print(loss_rate, valid_edges)

	#print()
	ax.plot(x_values, y_values,
			label=label,
			color = COLORS[i],
			marker = MARKERS[i][0],
			markersize = MARKERS[i][1],
			markeredgecolor = COLORS[i],
			markerfacecolor = (0,0,0,0))

ax.legend()
ax.set_xticks(X_TICKS)
ax.set_xlabel("Loss rate [%]")
ax.set_ylabel("Edges sampled")
#ax.grid(True)
save_figure(f, "loss_random_w20_effect_samples_absolute")
