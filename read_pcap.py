import dpkt

pcap_path = "/home/piet/eth/msc/hephaestus/test.pcap"

f = open(pcap_path)
pcap = dpkt.pcap.Reader(f)
