import os
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def generatepcap():
    # pcapfile = open(path + 'tmp.pcap', 'w+')
    pkts = sniff(prn=lambda x: x.sprintf(""), count=2000)
    wrpcap('tmp.pcap', pkts)
    # pcapfile.close()


def cleanpcap():
    os.remove('tmp.pcap')
