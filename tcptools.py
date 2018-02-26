import struct
import socket
import collections

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

TcpInfo = namedtuple('TcpInfo', tcp_info_field_names)

def getTCPInfo(s):
        fmt = "B"*7+"I"*21
        anonymous_data = struct.unpack(fmt,
			s.getsockopt(socket.IPPROTO_TCP, socket.TCP_INFO, 92))
		return TcpInfo._make(anonymous_data)
