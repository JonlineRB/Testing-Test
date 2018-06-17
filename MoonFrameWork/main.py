#!/usr/bin/env python

import subprocess
import utility
import ConfigParser
import sys

print('Framework: start')

# outFile = open('result', 'w')

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
