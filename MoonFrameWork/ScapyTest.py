import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def generatepcap():
    pkts = sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"), count=1000)
    # pkts = ICMP()
    wrpcap('tmp.pcap', pkts)

def cleanpcap():
    return