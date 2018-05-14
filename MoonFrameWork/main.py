# import unittest
import subprocess
import utility

print('Framework: start')

outFile = open('result', 'w')

# parse the necessary directories
# general setup, unbind all devices so that each test case may set up and tear down
dpdkdevlist = list()
utility.parsedevices(dpdkdevlist)
if not dpdkdevlist:
    print('No devices are DPDK bound')
else:
    print('parsed list is:')
    for x in range(0,len(dpdkdevlist)):
        print('device %d: ' + dpdkdevlist[x] %(x))
    # print(dpdkdevlist)
    utility.unbinddevices(dpdkdevlist)

utility.binddevices(dpdkdevlist)
exit()  # tmp

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
