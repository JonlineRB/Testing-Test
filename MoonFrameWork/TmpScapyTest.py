import scapy
import time

pkts = scapy.sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"))

time.sleep(10)

scapy.wrpcap("tmp.pcap", pkts)




