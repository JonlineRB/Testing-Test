import shutil
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def generatepcap():
    # pcapfile = open(path + 'tmp.pcap', 'w+')
    pkts = sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"), count=2000)
    wrpcap('tmp.pcap', pkts)
    # pcapfile.close()


def cleanpcap():
    shutil.rmtree('/tmp', ignore_errors=True)
