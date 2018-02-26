#!/usr/bin/python3

import sys
import time
import struct
import socket
import select
import random
import collections
import argparse

parser = argparse.ArgumentParser(description='Experimental TCP server|endpoint')
parser.add_argument("role", choices = ['client', 'server'])
parser.add_argument("--server-ip", default="127.0.0.1")
parser.add_argument("--server-port", type=int, default = 45678)
args = parser.parse_args()

tcp_info_field_names = ('state',
						'ca_state',
						'retransmits',
						'probes',
						'backoff',
						'options',
						'wscale',

						'rto',
						'ato',
						'snd_mss',
						'rcv_mss',

						'unacked',
						'sacked',
						'lost',
						'retrans',
						'fackets',

						'last_data_sent',
						'last_ack_sent',
						'last_data_recv',
						'last_ack_recv',

						'pmtu',
						'rcv_ssthresh',
						'rtt',
						'rttvar',
						'snd_ssthresh',
						'snd_cwnd',
						'advmss',
						'reordering')

TcpInfo = collections.namedtuple('TcpInfo', tcp_info_field_names)

def getTCPInfo(s):
		fmt = "B"*7+"I"*21
		anonymous_data = struct.unpack(fmt,
			s.getsockopt(socket.IPPROTO_TCP, socket.TCP_INFO, 92))
		return anonymous_data #TcpInfo._make(anonymous_data)

role = sys.argv[1]

def rolePrint(message):
	print("[{}]: {}".format(role, message))

serverIP = args.server_ip
serverPort = args.server_port

tcpSocket = None

if args.role == 'client':
	tcpSocket = socket.socket()
	rolePrint("Atempting to connect to server")
	tcpSocket.connect((serverIP, serverPort))
	rolePrint("Connected to server")

if args.role == 'server':
	serverSocket = socket.socket()
	serverSocket.bind((serverIP, serverPort))
	serverSocket.listen()
	rolePrint("Waiting for incomming connections on {}:{}".format(serverIP, serverPort))
	tcpSocket, client_address = serverSocket.accept()
	rolePrint("Accepted incomming connection from: {}".format(client_address))

sys.stdin = sys.stdin.detach().detach()

SELECT_WAIT_TIME = 0.01
STDIN_READ_SIZE = 1024
TCP_READ_SIZE = 1024
TCP_INFO_INTERVAL = 0.01

last_tcpinfo_time = time.time()

#sys.stderr.write("time, rtt, rttvar, unacked, snd_cwnd\n")
sys.stderr.write("epoch,")
for item in tcp_info_field_names:
	sys.stderr.write(item + ",")
sys.stderr.write('\n')
sys.stderr.flush()

while True:
	ready = select.select([sys.stdin, tcpSocket], [], [], SELECT_WAIT_TIME)[0]

	if sys.stdin in ready:
		stdin_data = sys.stdin.read(STDIN_READ_SIZE)
		tcpSocket.send(stdin_data)

	if tcpSocket in ready:
		tcp_data = tcpSocket.recv(TCP_READ_SIZE)
		sys.stdout.buffer.write(tcp_data)
		if len(tcp_data) == 0:
			sys.exit(0)
		sys.stdout.flush()

	if  time.time() - last_tcpinfo_time > TCP_INFO_INTERVAL:
		tcp_info = getTCPInfo(tcpSocket)
		sys.stderr.write(str(time.time()) + ",")
		for item in tcp_info:
			sys.stderr.write(str(item) + ',')
		sys.stderr.write('\n')
		sys.stderr.flush()
		last_tcpinfo_time = time.time()
