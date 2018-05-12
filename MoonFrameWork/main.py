# import unittest
import subprocess

print('Framework: start')

outFile = open('result', 'w')

# parse the necessary directories
# general setup, unbind all devices so that each test case may set up and tear down
# call a subprocess for dpdk-devbind, store the relevant results in a file
# create a file
initialBinds = open('inintialBindState', 'w')
# start this process
p = subprocess.Popen(
    ['./dpdk-devbind.py', '-s'], stdout=initialBinds, cwd='/home/borowski/MoonGen/libmoon/deps/dpdk/usertools'
)
initialBinds.close()
initialBinds = open('inintialBindState', 'r')
# parse and store the results
parsedLines = initialBinds.readlines()
initialBinds.close()
# for x in parsedLines:
for x in initialBinds.readlines():
    print x
    # if 'DPDK-compatible driver' in x:




exit() # tmp

# parse the required test cases
#
# This should be a called test case
print ("Testing MoonGen Simple Case: udp-simple")
p = subprocess.Popen(
    ['./moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
    stdout=outFile, cwd='/home/borowski/MoonGen/')

result = subprocess.Popen.wait(p)
outFile.close()

# move the feedback of tests to the test case
if result == 0:
    print('==TestFramework: test terminated, everything works.')
else:
    print('==TestFramework: exit code %s: Something went wrong!' % result)
    # parse file for known reasons
    errorFile = open('result', 'r')
    if 'Found 0 usable devices' in errorFile.read():
        print('No network devices were available. Suggestion: Try running as su, or binding devices.')
    else:
        print('Unknown error')
    errorFile.close()

print('Framework: end')
