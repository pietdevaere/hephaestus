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


analyzer_names = ["basic", "pn", "pn_valid", "valid", "pn_valid_edge", "valid_edge", 'status', "two_bit", "stat_heur", "rel_heur", "handshake"]

path = sys.argv[1]

return_dir = os.getcwd()
base_path = path
os.chdir(base_path)

vpp_data = list()

with open("switch-2_vpp.csv", newline='') as csvfile:
	reader = csv.DictReader(csvfile, skipinitialspace=True)
	base_time = None
	for row in reader:
		if base_time == None:
			base_time = float(row["time"])

		vpp_entry = collections.defaultdict(lambda: None)
		vpp_entry["time"] = float(row["time"]) - base_time
		vpp_entry["packet_number"] = int(row["pn"])
		vpp_entry["host"] = row["host"].strip()

		for analyzer in analyzer_names:
			if row[analyzer + "_new"] == '1':
				vpp_entry[analyzer] = float(row[analyzer + "_data"]) * 1000

		if vpp_entry['basic'] != None:   # Little hack to remove possible influence of handshake line
			vpp_data.append(vpp_entry)


valid_durations = collections.defaultdict(float)
invalid_durations = collections.defaultdict(float)
valid_samples = collections.defaultdict(int)
invalid_samples = collections.defaultdict(int)

for i in range(len(vpp_data)):
	sample = vpp_data[i]
	time = sample['time']
	for analyzer in analyzer_names:
		if sample[analyzer] != None:
			valid_samples[analyzer] += 1
			if i < len(vpp_data) - 1:
				valid_durations[analyzer] +=  vpp_data[i+1]['time'] - time
		else:
			invalid_samples[analyzer] += 1
			if i < len(vpp_data) - 1:
				invalid_durations[analyzer] +=  vpp_data[i+1]['time'] - time

for analyzer in analyzer_names:
	print("{:>20}:   {:>6} / {:<6}   {:>8.5} / {:<8.5}".format(
		analyzer,
		valid_samples[analyzer], invalid_samples[analyzer],
		valid_durations[analyzer], invalid_durations[analyzer]
		)
	)
