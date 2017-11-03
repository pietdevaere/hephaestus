#!/usr/bin/python2

from mininet.topo import Topo
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

config = {
	"short_name" : "tcp_dump_on_switch",
	"link_params" : dict(bw=10, delay='10ms'),
	"output_base_path" : "/home/piet/eth/msc/outputs/",
	"minq_path" : "/home/piet/go/src/github.com/ekr/minq/",
	"moku_path" : "/home/piet/go/src/github.com/britram/mokumokuren/",
	"script_path" : "/home/piet/eth/msc/hephaestus/",
	"num_servers" : 1,
	"num_clients" : 1,
	"runtime" : 300,
	"user" : "piet",
	"minq_server_command" : """sudo -u {user} MINQ_LOG={minq_log_level} /usr/local/go/bin/go run {minq_path}/bin/server/main.go -addr {server_ip}:4433 -server-name {server_ip}""",
	"minq_client_command" : """sudo -u {user} MINQ_LOG={minq_log_level} /usr/local/go/bin/go run {minq_path}/bin/client/main.go -heartbeat 1 -addr {server_ip}:4433""",
	"minq_log_level": "stats",
	"ping_command" : "ping -i 0.001 {target_ip}",
	"tcpdump_command" : """tcpdump -i {interface} -n udp port 4433 -w {tcpdump_file}""",
	"moku_command" : """sudo -u {user} /usr/local/go/bin/go run {moku_path}/tmoku/main.go --file {inputfile}""",
	"spinbit_command" : """python3 {script_path}/analyze_spinbit.py {outputdir}/{switch}-eth1_moku_stdout.txt {outputdir}/{client}_minq_stderr.txt {outputdir}/{server}_minq_stderr.txt {outputdir}/{client}_ping_stdout.txt {outputdir}/{client}"""
		}

class MinqBasicTestTopo(Topo):

	def build(self, num_clients, num_servers, config = {}):

		self.servers = list()
		self.clients = list()
		self.switch_names = list()

		switch = self.addSwitch('switch-1')
		self.switch_names.append(switch)

		for i in xrange(num_servers):
			server_num = i + 1
			ip = "10.0.0.{}".format(server_num)
			server = self.addHost("server-{}".format(server_num), ip = ip)
			self.addLink(server, switch, **config["link_params"])
			self.servers.append(server)

		for i in xrange(num_clients):
			client_num = i + 1
			ip = "10.0.0.{}".format(100 + client_num)
			client = self.addHost("client-{}".format(client_num), ip = ip)
			self.addLink(client, switch, **config["link_params"])
			self.clients.append(client)


def startMinqServer(hostName, net):
	server = net[hostName]



def printConfig(config):
	print("==== CONFIG ====")
	for key, entry in sorted(config.items(), key=lambda x: x[0]):
		print ("    {:20} : {}".format(key, entry))
	print("==== END CONFIG ====")
	print

class BasicMinqTestbed:

	def __init__(self, config):
		self.config = config
		self.config["timestamp"] = datetime.datetime.now().isoformat()

		self.makeOutputFolder()
		self.archiveScriptCode()
		self.archiveMokuCode()
		self.archiveMinqCode()

		self.servers = list()
		self.clients = list()

		self.running = list()

		printConfig(config)

	def start(self):
		# setup the network
		self.topo = MinqBasicTestTopo(self.config["num_clients"], self.config["num_servers"], self.config)
		self.net = Mininet(self.topo, link = TCLink)
		self.net.start()

		# confirm connectivity
		print("Testing network connectivity")
		self.net.pingAll()

		print("Starting minq servers")
		self.startSwitches()
		self.startServers()
		self.startClients()

	def makeOutputFolder(self):
		self.outputdir = "{output_base_path}/{timestamp}_{short_name}".format(**self.config)
		self.config["outputdir"] = self.outputdir
		os.makedirs(self.outputdir)
		os.chdir(self.outputdir)

	def archiveMinqCode(self):
		shutil.make_archive(	"{}/minq".format(self.outputdir),
								"zip",
								self.config["minq_path"],
							)

	def archiveMokuCode(self):
		shutil.make_archive(	"{}/moku".format(self.outputdir),
								"zip",
								self.config["moku_path"],
							)

	def archiveScriptCode(self):
		shutil.make_archive(	"{}/script".format(self.outputdir),
								"zip",
								self.config["script_path"],
							)

	def stop(self):
		for handle in self.running:
			handle.terminate()

		self.net.stop()

	def startSwitches(self):
		for switch_name in self.topo.switch_names:
			switch = self.net[switch_name]
			interface = "{}-eth1".format(switch)
			self.startLocalTcpDump(interface)

	def startServers(self):
		for server_name in self.topo.servers:
			server = self.net[server_name]
			self.startMinqServer(server)

	def startClients(self):
		for client_name in self.topo.clients:
			client = self.net[client_name]
			server = self.net[self.topo.servers[0]]
			self.startPing(client, server)
			self.startPing(server, client)
			self.startTcpDump(client)
			self.startMinqClient(client, server)

	def startTcpDump(self, host, iface = None):
		if not iface:
			iface = host.intf()
		print("--> Starting TCP dump on host {}, interface {}".format(host.name, iface))
		output_path = "{outputdir}/{hostname}_tcpdump.pcap".format(hostname=host.name, **self.config)
		cmd_string = self.config["tcpdump_command"].format(interface=iface, tcpdump_file=output_path, **self.config)
		print(cmd_string)
		args = shlex.split(cmd_string)
		stdout = open("{}_tcpdump_stdout.txt".format(host.name), 'w')
		stderr = open("{}_tcpdump_stderr.txt".format(host.name), 'w')
		handle = host.popen(args, stdout=stdout, stderr=stderr)
		self.running.append(handle)

	def startLocalTcpDump(self, iface):
		print("--> Starting local TCP dump on interface {}".format(iface))
		output_path = "{outputdir}/{iface}_tcpdump.pcap".format(iface=iface, **self.config)
		cmd_string = self.config["tcpdump_command"].format(interface=iface, tcpdump_file=output_path, **self.config)
		print(cmd_string)
		args = shlex.split(cmd_string)
		stdout = open("{}_tcpdump_stdout.txt".format(iface), 'w')
		stderr = open("{}_tcpdump_stderr.txt".format(iface), 'w')
		handle = subprocess.Popen(args, stdout=stdout, stderr=stderr)
		self.running.append(handle)

	def startMinqServer(self, host):
		cmd_string = self.config["minq_server_command"].format(server_ip = host.IP(), **self.config)
		print(cmd_string)
		args = shlex.split(cmd_string)
		stdout = open("{}_minq_stdout.txt".format(host.name), 'w')
		stderr = open("{}_minq_stderr.txt".format(host.name), 'w')
		handle = host.popen(args, stdout=stdout, stderr=stderr,stdin=subprocess.PIPE)
		self.running.append(handle)

	def startMinqClient(self, host, server):
		cmd_string = self.config["minq_client_command"].format(server_ip=server.IP(), **self.config)
		print(cmd_string)
		args = shlex.split(cmd_string)
		stdout = open("{}_minq_stdout.txt".format(host.name), 'w')
		stderr = open("{}_minq_stderr.txt".format(host.name), 'w')
		handle = host.popen(args, stdout=stdout, stderr=stderr, stdin=subprocess.PIPE)
		self.running.append(handle)

	def startPing(self, host, target):
		cmd_string = self.config["ping_command"].format(target_ip = target.IP(), **self.config)
		print(cmd_string)
		args = shlex.split(cmd_string)
		stdout = open("{}_ping_stdout.txt".format(host.name), 'w')
		stderr = open("{}_ping_stderr.txt".format(host.name), 'w')
		handle = host.popen(args, stdout=stdout, stderr=stderr,stdin=subprocess.PIPE)
		self.running.append(handle)

	def analyze(self):
		for switch in self.topo.switch_names:
			self.analyzeWithMoku("{}-eth1".format(switch))
		for client in self.topo.clients:
			self.analyzeWithMoku(client)
			self.analyzeSpinbit(client, self.topo.servers[0], self.topo.switch_names[0])


	def analyzeWithMoku(self, hostname):
		inputpath = "{}_tcpdump.pcap".format(hostname)
		cmd_string = self.config["moku_command"].format(inputfile=inputpath, **self.config)
		print(cmd_string)
		args = shlex.split(cmd_string)
		stdout = open("{}_moku_stdout.txt".format(hostname), 'w')
		stderr = open("{}_moku_stderr.txt".format(hostname), 'w')
		handle = subprocess.Popen(args, stdout=stdout, stderr=stderr)
		handle.wait()

	def analyzeSpinbit(self, client, server, switch):
		cmd_string = self.config["spinbit_command"].format(client=client, server=server, switch=switch, **self.config)
		print(cmd_string)
		args = shlex.split(cmd_string)
		stdout = open("{}_spinbit_stdout.txt".format(client), 'w')
		stderr = open("{}_spinbit_stderr.txt".format(client), 'w')
		handle = subprocess.Popen(args, stdout=stdout, stderr=stderr)
		handle.wait()

def fancyWait(wait_time):
	elapsed_time = 0
	total_time = wait_time
	while wait_time >= 60:
		percentage = int(100* elapsed_time / total_time)
		print("Time elapsed: {:5} s | time remaning: {:5} s | {:2}%".format(elapsed_time, wait_time, percentage))
		time.sleep(60)
		elapsed_time += 60
		wait_time -= 60
	percentage = int(100* elapsed_time / total_time)
	print("Time elapsed: {:5} s | time remaning: {:5} s | {:2}%".format(elapsed_time, wait_time, percentage))
	time.sleep(wait_time)
	print("Done, shutting down mininet")

def fancyWait2(wait_time, steps = 50):
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
	print('Done, shutting down mininet')



if __name__ == '__main__':
	# Tell mininet to print useful information
	setLogLevel('info')
	testbed = BasicMinqTestbed(config)
	testbed.start()
	fancyWait2(config["runtime"])
	testbed.stop()
	testbed.analyze()




