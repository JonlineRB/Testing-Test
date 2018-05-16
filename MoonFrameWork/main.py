# import unittest
import subprocess
import utility
import ConfigParser
import tests

print('Framework: start')

# outFile = open('result', 'w')

# parse the necessary directories
# general setup, unbind all devices so that each test case may set up and tear down
MoonGenPath = ''
dpdkdevlist = list()
utility.initdevices(dpdkdevlist)

# outFile.close()

# just check the parser functionality
parser = ConfigParser.ConfigParser()
parser.read('FrameworkConfig.cfg')
print(parser.sections())  # just for testing
MoonGenPath = parser.get('Meta', 'path')
if parser.get('Section1', 'test') == 'timestamp':
    print('constructing timestamp test')
    index1 = int(parser.get('Section1', 'device1'))
    index2 = int(parser.get('Section1', 'device2'))
    tmpList = list()
    tmpList.append(dpdkdevlist[index1])
    tmpList.append(dpdkdevlist[index2])
    test = tests.TestTimeStampCapabilities(tmpList, MoonGenPath)
    print('running test!')
    test.runTest()
    print('test concluded!')
else:
    print('unknown test case')
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
