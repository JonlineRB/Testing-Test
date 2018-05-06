# import unittest
import subprocess

print ("Testing MoonGen Simple Case: udp-simple")

outFile = open('result', 'w')

# p = subprocess.Popen(['/home/borowski/Moongen/moongen-simple', 'start',
#                       'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'], stdout=outFile)
p = subprocess.Popen(
    ['./../../../MoonGen/moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
    stdout=outFile)

result = subprocess.Popen.wait(p)

if result == 0:
    print('==TestFramework: test terminated, everything worked out.')
else:
    print('==TestFramework: exit code %s: Something went wrong!' % result)
    # parse file

outFile.close()

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
