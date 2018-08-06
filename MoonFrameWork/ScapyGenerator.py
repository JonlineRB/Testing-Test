import os, sys
# import logging

# logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from contextlib import contextmanager

@contextmanager
def mute_console():
    with open(os.devnull, "w") as devnull:
        original_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = original_stdout


def generatepcap():
    print 'Generating PCAP file'
    with mute_console():
        pkts = sniff(prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"), count=2000)
        wrpcap('tmp.pcap', pkts)


def cleanpcap():
    os.remove('tmp.pcap')
