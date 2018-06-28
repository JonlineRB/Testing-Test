import shutil
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def generatepcap(path):
    # pcapfile = open(path + 'tmp.pcap', 'w+')
    pkts = sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"), count=2000)
    wrpcap(path + 'tmp/tmp.pcap', pkts)
    # pcapfile.close()


def cleanpcap(path):
    shutil.rmtree(path + '/tmp', ignore_errors=True)
