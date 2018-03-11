#!/usr/bin/python2
import os
import sys

if os.geteuid() != 0:
	print("I am not root, goodnight")
	sys.exit()
else:
	print("Bow before me for I am root")

os.system("killall ovs-testcontroller")
os.system("mn -c")

#RUN_TYPE

d = dict()
with open('config') as config_file:
	for line in config_file:
		line = line.strip().split()
		if len(line) == 2:
			d[line[0]] = line[1]

netem_options = (
				 "delay 10ms",
				 "delay 1ms",
				 "delay 500us",
				 "delay 10ms 10ms 99",
				 "delay 10ms 3ms 25",
				 "loss random 0.01",
				 "loss random 0.1",
				 "loss random 1",
				 "loss random 2",
				 "delay 100us reorder 1 25",
				 "delay 100us reorder 10 25",

				 "delay 1ms reorder 1 25",
				 "delay 1ms reorder 10 25",
				 "delay 1ms reorder 50 25",
				 "delay 5ms reorder 10 25",
				 "delay 5ms reorder 50 25",


				 "loss gemodel 1 10 25 0.1",
				 "loss gemodel 1 10 75 0.1",
				 "loss gemodel 1 10 100 0.1",

				 #"loss gemodel 1 25 70 0.1",
				 #"loss gemodel 1 25 100 0",
				 #"loss gemodel 1 20 70 0.1",
				 #"loss gemodel 1 20 100 0",
				 #"loss gemodel 1 15 70 0.1",
				 #"loss gemodel 1 15 100 0",
				 #"loss gemodel 1 30 70 0.1",
				 #"loss gemodel 1 30 100 0",
				 #"loss gemodel 1 30 25 0.1",
				 #"loss gemodel 1 10 25 0.1",s
				 #"loss gemodel 1 10 75 0.1",

				 #"loss gemodel 1 10 100 0.1",

				 "loss gemodel 0.1 10 25 0.1",
				 "loss gemodel 0.1 10 75 0.1",
				 "loss gemodel 0.1 10 100 0.1",

				 #"loss gemodel 0.01 5 25 0.1",
				 #"loss gemodel 0.01 5 75 0.1",
				 #"loss gemodel 0.01 5 100 0.1",
				 )

for netem_option in netem_options:
	print('#'*80)
	print('Now moving to netem option: {}'.format(netem_option))
	print('#'*80)
	cmd = "{SCRIPT_PATH}/simple_for_vpp.py --run-name '{netem}' --dynamic-intf '{netem}' --file 10GiB --time 80"
	#cmd += " --tcp"
	#cmd += " --one-direction"
	#cmd += " --no-baseline"
	#cmd = "/home/piet/eth/msc/hephaestus/simple.py --run-name '{netem}' --dynamic-intf '{netem}' --time 30 --heartbeat 100"
	cmd = cmd.format(netem = netem_option, **d)
	os.system(cmd)

print('#'*80)
print('Now moving to bursty_traffic')
print('#'*80)
cmd = "{SCRIPT_PATH}/simple_for_vpp.py --run-name 'bursty_traffic' --time 80 --traffic-gen '--cycles 100 --heartbeat 80'"
#cmd += " --no-baseline"
cmd = cmd.format(**d)
os.system(cmd)
