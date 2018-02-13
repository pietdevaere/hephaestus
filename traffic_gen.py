#!/usr/bin/python3

import argparse
import time
import datetime
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--calm-time', type=int, default=15)
parser.add_argument('--heartbeat', type=int, default=100)
parser.add_argument('--burst-size', type=int, default=1)
parser.add_argument('--cycles', type=int, default=5)
parser.add_argument('--start-delay', type=int, default = 0)
args = parser.parse_args()

time.sleep(args.start_delay)

for cycle in range(args.cycles):
	sys.stderr.write("[Traffic Gen] :: cycle: {}".format(cycle))
	# calm time
	sys.stderr.write(" Sending heartbeats")
	sys.stderr.flush()
	num_of_heartbeats = int(args.calm_time / args.heartbeat * 1000)
	for heartbeat in range(num_of_heartbeats):
		sys.stdout.write("Heartbeat at {}\n".format(datetime.datetime.now()))
		sys.stdout.flush()
		time.sleep(args.heartbeat/1000)

	# burst
	sys.stderr.write(", Sending burst\n")
	sys.stderr.flush()
	sys.stdout.write("A"*1024*1024*args.burst_size)
	sys.stdout.flush()
