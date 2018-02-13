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
				 "delay 5ms reorder 50 25"
				 )

for netem_option in netem_options:
	print('#'*80)
	print('Now moving to netem option: {}'.format(netem_option))
	print('#'*80)
	cmd = "/home/piet/eth/msc/hephaestus/simple_for_vpp.py --run-name '{netem}' --dynamic-intf '{netem}' --file 1GiB --time 60"
	#cmd += " --no-baseline"
	#cmd = "/home/piet/eth/msc/hephaestus/simple.py --run-name '{netem}' --dynamic-intf '{netem}' --time 30 --heartbeat 100"
	cmd = cmd.format(netem = netem_option)
	os.system(cmd)

print('#'*80)
print('Now moving to bursty_traffic: {}'.format(netem_option))
print('#'*80)
cmd = "/home/piet/eth/msc/hephaestus/simple_for_vpp.py --run-name 'bursty_traffic' --time 60 --traffic-gen '--cycles 100 --heartbeat 80'"
#cmd += " --no-baseline"
os.system(cmd)
