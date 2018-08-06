from scapy.all import *

print 'Generating PCAP file'
    pkts = sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"), count=2000)
    wrpcap('tmp.pcap', pkts)