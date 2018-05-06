# import unittest
import subprocess

print ("Testing MoonGen Simple")

outFile = open('result', 'w')

# p = subprocess.Popen(['/home/borowski/Moongen/moongen-simple', 'start',
#                       'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'], stdout=outFile)
p = subprocess.Popen('/home/borowski/Moongen/moongen-simple start udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson',
                     shell=True, stdout=outFile)

subprocess.Popen.wait(p)

# class TestMoonGenSimple(unittest.TestCase):

# def testSimpleUdp(self):
# use a file for output
# outFile = open('result', 'w')
# execute MoonGenSimple: udp-simple
# p = self.subprocess.Popen([])


# go to MoonGen repo and execute a simple flow

# def callsimple1():
#     # moonGenPath = "~/MoonGen/"
#     # simpleFlow = "moongen-simple start load-latency:0:1:rate=10Mp/s,time=3m"
#     call("./../../../MoonGen/moongen-simple start load-latency:0:1:rate=10Mp/s,time=3m",shell=True)

# def callsimplelocal():
#     call("./moongen-simple start load-latency:0:1:rate=10Mp/s,time=3m",shell=True)

# def echotest():
#     call("echo TEST",shell=True)
