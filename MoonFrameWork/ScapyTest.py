import os
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def generatepcap(path):
    pkts = sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"), count=1000)
    pcapfile = open(path + 'tmp/tmp.pcap', 'w')
    wrpcap(pcapfile, pkts)
    pcapfile.close()

def cleanpcap(path):
    return
    # os.remove()