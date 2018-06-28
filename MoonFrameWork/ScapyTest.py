import os
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def generatepcap(path):
    pcapfile = open(path + 'tmp.pcap', 'w+')
    pkts = sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"), count=1000)
    wrpcap(pcapfile, pkts)
    pcapfile.close()

def cleanpcap(path):
    return
    # os.remove()