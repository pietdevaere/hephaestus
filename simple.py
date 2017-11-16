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
	FILES_PATH = "/home/piet/eth/msc/input_files/",
	USER = "piet",
	MINQ_LOG_LEVEL = "stats,congestion,flow",
	)

LOCAL = None

####################################################
## MAKE FOLDER AND ARCHIVE CODE
####################################################

timestamp = datetime.datetime.now().isoformat()

run_name = raw_input("Name for run: ").strip()
run_name = run_name.replace(' ', '-')
if run_name:
	outputdir = "{OUTPUT_BASE_PATH}/{timestamp}_{run_name}"
	outputdir = outputdir.format(timestamp=timestamp, run_name=run_name, **d)
else:
	outputdir = "{OUTPUT_BASE_PATH}/nameless_runs/{timestamp}"
	outputdir = outputdir.format(timestamp=timestamp, **d)


os.makedirs(outputdir)
os.chdir(outputdir)

shutil.make_archive("minq", "zip", d['MINQ_PATH'])
shutil.make_archive("moku", "zip", d['MOKU_PATH'])
shutil.make_archive("script", "zip", d['SCRIPT_PATH'])

####################################################
## BUILD NETWORK
####################################################

linkops = dict( bw = 100,
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

def popenWrapper(prefix, command, host = None, stdin = None, stdout = None, stderr = None):
	args = shlex.split(command)

	if not stdin:
		stdin = subprocess.PIPE
	elif type(stdin) == str:
		stdin = open(stdin, 'r')

	if not stdout:
		stdout = open("{}_stdout.txt".format(prefix), 'w')
	elif type(stdout) == str:
		stdout = open(stdout, 'w')

	if not stderr:
		stderr = open("{}_stderr.txt".format(prefix), 'w')
	elif type(stderr) == str:
		stderr = open(stderr, 'w')

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

# Start tcpdump on server
cmd = """tcpdump -i {interface} -n udp port 4433 -w {tcpdump_file}"""
cmd = cmd.format(interface = "server-1-eth0", tcpdump_file = "server-1_tcpdump.pcap")
handle = popenWrapper("server-1_tcmpdump", cmd, servers[0])
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
server_stdout_path = "server-1_minq_stdout"
handle = popenWrapper("server-1_minq", cmd, servers[0], stdout = server_stdout_path)
running_commands.append(handle)

# Start Minq Client
#cmd = """sudo -u {USER} MINQ_LOG={MINQ_LOG_LEVEL} /usr/local/go/bin/go run {MINQ_PATH}/bin/client/main.go -heartbeat 1 -addr {server_ip}:4433"""
cmd = """sudo -u {USER} MINQ_LOG={MINQ_LOG_LEVEL} /usr/local/go/bin/go run {MINQ_PATH}/bin/client/main.go -addr {server_ip}:4433"""
cmd = cmd.format(server_ip = servers[0].IP(), **d)
client_stdin_path = "{FILES_PATH}/50MiB".format(**d)
#client_stdin_path = None
handle = popenWrapper("client-1_minq", cmd, clients[0], stdin=client_stdin_path)
#running_commands.append(handle)
client_handle = handle

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

wait_time = 0

if wait_time:
	fancyWait(wait_time)
	client_handle.terminate()
else:
	print("Now waiting for client to terminate")
	startTime = datetime.datetime.now()
	client_handle.wait()
	print("Client is done :) {}".format(datetime.datetime.now() - startTime))

cmd = "cmp {} {}"
cmd = cmd.format(client_stdin_path, server_stdout_path)
args = shlex.split(cmd)
if subprocess.call(args):
	print("input and output file equal!")

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
## RUN ANALYZER SCRIPTS
####################################################

cmd = """python3 {SCRIPT_PATH}/analyze_spinbit.py switch-1_moku_stdout.txt client-1_minq_stderr.txt server-1_minq_stderr.txt client-1_ping_stdout.txt client-1"""
cmd = cmd.format(**d)
handle = popenWrapper("client-1_spin_", cmd, LOCAL)
handle.wait()

cmd = """python3 {SCRIPT_PATH}/analyze_congestion.py client-1_minq_stderr.txt client-1"""
cmd = cmd.format(**d)
handle = popenWrapper("client-1_congestion_", cmd, LOCAL)
handle.wait()

cmd = """python3 {SCRIPT_PATH}/analyze_congestion.py server-1_minq_stderr.txt server-1"""
cmd = cmd.format(**d)
handle = popenWrapper("server-1_congestion_", cmd, LOCAL)
handle.wait()

####################################################
## VERIFY THAT FILE WAS SUCESSFULLY COPIED
####################################################

cmd = "cmp {} {}"
cmd = cmd.format(client_stdin_path, server_stdout_path)
args = shlex.split(cmd)
not_equal = subprocess.call(args)

if client_stdin_path and not_equal:
	print(">>>OUTPUT FILES ARE NOT EQUAL<<<")
	in_size = os.path.getsize(client_stdin_path)
	out_size = os.path.getsize(server_stdout_path)
	print("File size original: {}, copy: {}".format(in_size, out_size))
	open(" FAIL", 'w').close()
elif client_stdin_path:
	print("> output files are equal :) ")
	open(" SUCCESS", 'w').close()

os.system("rm server-1_minq_stdout")

####################################################
## CLEAN UP
####################################################

os.system("chown piet:piet . -R")
