#!/usr/bin/env python

import subprocess
import utility
import ConfigParser
import sys

print('Framework: start')

# case of arg -h

try:
    if sys.argv[1] == '-h':
        print 'execute to run the config file.'
        print 'alternatively, use -t followed by desired tests and device1, device2'
        print 'you may use PCI express id or device number like in MoonGen'
        print 'either way, make sure absolute path to MoonGen is present in [Meta]'
        print 'section of the config file FrameworkConfig.cfg'
        print 'please refer to CaseDict.txt for supported cases'
        exit()
except IndexError:


# parse the necessary directories
# general setup, unbind all devices so that each test case may set up and tear down
parser = ConfigParser.ConfigParser()
parser.read('FrameworkConfig.cfg')
MoonGenPath = parser.get('Meta', 'path')
dpdkdevlist = list()
utility.initdevices(dpdkdevlist, MoonGenPath)

utility.parsetestcases(dpdkdevlist, sys.argv)

print('Printing device list before exit')
print(dpdkdevlist)
utility.binddevices(dpdkdevlist, MoonGenPath)

print('Framework: end')

exit()
