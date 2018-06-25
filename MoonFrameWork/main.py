# !/usr/bin/env python

import utility
import ConfigParser
import sys
import os.path


print('Framework: start')

# case of arg -h
try:
    if sys.argv[1] == '-h':
        print'===================================================================='
        print 'Welcome to the dedicated testing framework for MoonGen.'
        print 'execute as is to run the tests according to the config file:'
        print 'FrameworkConfig.cfg'
        print 'alternatively, use -t followed by desired tests and device1, device2.'
        print 'you may use PCI express id or device number like in MoonGen'
        print 'either way, make sure absolute path to MoonGen is present in [Meta]'
        print 'section of the config file FrameworkConfig.cfg'
        print 'please refer to CaseDict.txt for supported cases'
        print'===================================================================='
        exit()
except IndexError:
    pass

# create logs dir if it does not exist already
if not os.path.exists('logs'):
    os.makedirs('logs')

# parse the necessary directories
# general setup, unbind all devices so that each test case may set up and tear down
parser = ConfigParser.ConfigParser()
parser.read('FrameworkConfig.cfg')
try:
    MoonGenPath = parser.get('Meta', 'path')
except ConfigParser.NoSectionError or ConfigParser.NoOptionError:
    print 'Please set the path to moongen in the config file Meta section'
    exit()
dpdkdevlist = list()
utility.initdevices(dpdkdevlist, MoonGenPath)

testexecutor = utility.TestExecutor(MoonGenPath)

if len(sys.argv) >= 2:
    if sys.argv[1] == '-t':
        print 'parsing from command line'
        testexecutor.parsefromargs(dpdkdevlist, sys.argv)
else:
    print 'parsing from config file'
    testexecutor.parsefromconfig(dpdkdevlist)

# utility.parsetestcases(dpdkdevlist, sys.argv)

utility.binddevices(dpdkdevlist, MoonGenPath)

print('Framework: end')

exit()
