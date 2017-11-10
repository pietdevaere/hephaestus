#!/usr/bin/python2

from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController
from mininet.link import TCLink

import datetime
import os
import subprocess
import shutil
import shlex
import time
import sys

d = dict(
	OUTPUT_BASE_PATH = "/home/piet/eth/msc/outputs/",
	MINQ_PATH = "/home/piet/go/src/github.com/ekr/minq/",
	MOKU_PATH = "/home/piet/go/src/github.com/britram/mokumokuren/",
	SCRIPT_PATH = "/home/piet/eth/msc/hephaestus/",
	USER = "piet",
	MINQ_LOG_LEVEL = "stats",
	)

LOCAL = None

####################################################
## MAKE FOLDER AND ARCHIVE CODE
####################################################

timestamp = datetime.datetime.now().isoformat()
outputdir = "{OUTPUT_BASE_PATH}/{timestamp}".format(timestamp=timestamp, **d)

run_name = raw_input("Name for run: ").strip()
run_name = run_name.replace(' ', '-')
if run_name:
	outputdir += '_' + run_name

os.makedirs(outputdir)
os.chdir(outputdir)

shutil.make_archive("minq", "zip", d['MINQ_PATH'])
shutil.make_archive("moku", "zip", d['MOKU_PATH'])
shutil.make_archive("script", "zip", d['SCRIPT_PATH'])

####################################################
## BUILD NETWORK
####################################################

linkops = dict( bw = 10,
			    delay = '10ms'
		      )

net = Mininet(link = TCLink)

controllers = []
switches = []
servers = []
clients = []
links = []

switches.append(net.addSwitch('switch-1'))
controllers.append(net.addController('controller-1'))
servers.append(net.addHost('server-1', ip='10.0.0.1'))
clients.append(net.addHost('client-1', ip='10.0.0.101'))

links.append(net.addLink(switches[0], servers[0], **linkops))
links.append(net.addLink(switches[0], clients[0], **linkops))

setLogLevel('info')
net.start()
net.pingAll()

####################################################
## RUN MEASUREMENT COMMANDS
####################################################

running_commands = list()

def popenWrapper(prefix, command, host = None, stdin = None):
	args = shlex.split(command)
	stdout = open("{}_stdout.txt".format(prefix), 'w')
	stderr = open("{}_stderr.txt".format(prefix), 'w')
	if not stdin:
		stdin = subprocess.PIPE

	if host:
		host_name = host.name
		handle = host.popen(args, stdout=stdout, stderr=stderr, stdin=stdin)
	else:
		host_name = "local"
		handle = subprocess.Popen(args, stdout=stdout, stderr=stderr, stdin=stdin)

	print("[{}] running:: {}".format(host_name, command))

	return handle

# Start tcpdump on client
cmd = """tcpdump -i {interface} -n udp port 4433 -w {tcpdump_file}"""
cmd = cmd.format(interface = "client-1-eth0", tcpdump_file = "client-1_tcpdump.pcap")
handle = popenWrapper("client-1_tcmpdump", cmd, clients[0])
running_commands.append(handle)

# Start tcpdump on switch
cmd = """tcpdump -i {interface} -n udp port 4433 -w {tcpdump_file}"""
cmd = cmd.format(interface = "switch-1-eth1", tcpdump_file = "switch-1_tcpdump.pcap")
handle = popenWrapper("switch-1_tcpdump", cmd, LOCAL)
running_commands.append(handle)

#start ping on client
#cmd = """{SCRIPT_PATH}/ping.py {target_ip}"""
cmd = """ping -D -i 0.001 {target_ip}"""
cmd = cmd.format(target_ip = servers[0].IP(), **d)
handle = popenWrapper("client-1_ping", cmd, clients[0])
running_commands.append(handle)

# Start Minq Server
cmd = """sudo -u {USER} MINQ_LOG={MINQ_LOG_LEVEL} /usr/local/go/bin/go run {MINQ_PATH}/bin/server/main.go -addr {server_ip}:4433 -server-name {server_ip}"""
cmd = cmd.format(server_ip = servers[0].IP(), **d)
handle = popenWrapper("server-1_minq", cmd, servers[0])
running_commands.append(handle)

# Start Minq Client
cmd = """sudo -u {USER} MINQ_LOG={MINQ_LOG_LEVEL} /usr/local/go/bin/go run {MINQ_PATH}/bin/client/main.go -heartbeat 1 -addr {server_ip}:4433"""
cmd = cmd.format(server_ip = servers[0].IP(), **d)
handle = popenWrapper("client-1_minq", cmd, clients[0])
running_commands.append(handle)

####################################################
## DELAY AND STOP MEASUREMENT
####################################################

def fancyWait(wait_time, steps = 50):
	elapsed_time = 0
	total_time = wait_time

	print("Will run for {} seconds".format(wait_time))
	print("|"+"-"*(steps-2)+"|")

	step_size = float(total_time) / steps
	while wait_time > step_size:
		time.sleep(step_size)
		wait_time -= step_size
		sys.stdout.write('*')
		sys.stdout.flush()
	time.sleep(wait_time)
	sys.stdout.write('\n')

#net.startTerms()

def reconfigureLinkDelay():
	print("Reconfiguring link delay to: {}".format(linkops["delay"]))
	for link in links:
		for intf in (link.intf1, link.intf2):
			node = intf.node
			intf_name = intf.name

			cmd = "tc qdisc change dev {interface} parent 5:1 handle 10: netem delay {delay}"
			cmd = cmd.format(interface = intf_name, delay = linkops["delay"])
			node.cmd(cmd)


fancyWait(60)

linkops["delay"] = "15ms"
reconfigureLinkDelay()

fancyWait(60)

linkops["delay"] = "10ms"
reconfigureLinkDelay()

fancyWait(60)

linkops["delay"] = "20ms"
reconfigureLinkDelay()

fancyWait(60)

linkops["delay"] = "5ms"
reconfigureLinkDelay()

fancyWait(60)

while len(running_commands) > 0:
	handle = running_commands.pop()
	handle.terminate()

print('Done, shutting down mininet')
net.stop()

####################################################
## RUN MOKUMOKUREN
####################################################

cmd = """sudo -u {USER} /usr/local/go/bin/go run {MOKU_PATH}/tmoku/main.go --file {inputfile}"""
cmd = cmd.format(inputfile = "switch-1_tcpdump.pcap", **d)
handle = popenWrapper("switch-1_moku", cmd, LOCAL)
handle.wait()

####################################################
## RUN ANALYZER SCRIPT
####################################################

cmd = """python3 {SCRIPT_PATH}/analyze_spinbit.py switch-1_moku_stdout.txt client-1_minq_stderr.txt server-1_minq_stderr.txt client-1_ping_stdout.txt client-1"""
cmd = cmd.format(**d)
handle = popenWrapper("client-1_analyze", cmd, LOCAL)
handle.wait()

####################################################
## CLEAN UP
####################################################

os.system("chown piet:piet . -R")
