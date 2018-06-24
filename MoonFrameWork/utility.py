import os
import subprocess
import ConfigParser
# from FrameworkSubprocess import SubHandler
import tests  # dont remove this, it is actually used on eval() calls
from tap import TAPTestRunner
import unittest


# utility class for the MoonGen Testing framework

def parsedevices(dpdkdevlist, path):
    print('Framework: Parsing DPDK bound devices')
    # call a subprocess for dpdk-devbind, store the relevant results in a file
    # create a file
    initialbinds = open('initialBindState', 'w')
    # start this process
    p = subprocess.Popen(
        ['./dpdk-devbind.py', '-s'], stdout=initialbinds, cwd=path + 'libmoon/deps/dpdk/usertools'
    )
    p.wait()
    # parse and store the results
    initialbinds.close()
    initialbinds = open('initialBindState', 'r')
    parsedlines = initialbinds.readlines()
    initialbinds.close()

    for x in parsedlines:
        if 'Network devices using DPDK-compatible driver' in x:
            dpdkindex = parsedlines.index(x) + 2
            while parsedlines[dpdkindex] != '\n' and parsedlines[dpdkindex] != '<none>\n':
                dpdkdevlist.append(parsedlines[dpdkindex])
                dpdkindex += 1
            break
    os.remove('initialBindState')
    return dpdkdevlist


# removes dpdk bound device
def unbinddevices(devicelist, path):
    for x in devicelist:
        p = subprocess.Popen(
            ['./dpdk-devbind.py', '-u', x.split()[0]], cwd=path + 'libmoon/deps/dpdk/usertools'
        )
        p.wait()


# initialize devices at the start
def initdevices(devicelist, path):
    parsedevices(devicelist, path)
    if not devicelist:
        print('No devices are DPDK bound')
    else:
        print('parsed list is:')
        for x in range(0, len(devicelist)):
            print('device %d: ' % x + devicelist[x])
        unbinddevices(devicelist, path)


# binds devices to dpdk
def binddevices(devicelist, path):
    if not devicelist:
        return
    for x in devicelist:
        p = subprocess.Popen(
            ['./dpdk-devbind.py', '--bind=igb_uio', x.split()[0]],
            cwd=path + 'libmoon/deps/dpdk/usertools'
        )
        p.wait()


# returns the index of the device in the list of devices
def getdeviceindex(devicelist, arg):
    # case of PCI express handeled
    if ':' in arg:
        for i in range(0, len(devicelist)):
            if arg == devicelist[i].split()[0]:
                return i
        return -1
    elif int(arg) >= len(devicelist) or int(arg) < 0:
        return -1
    else:
        return int(arg)


def handletags(name, devicelist, cases, path, suite):
    parser = ConfigParser.ConfigParser()
    parser.read('TagConfig.cfg')
    if name == 'all':
        # generate all tests for this piar
        for key in cases:
            test = eval(cases[key])(devicelist, path)
            suite.addTest(test)
    else:
        for section in parser.sections():
            if name == section:
                for option in parser.options(section):
                    testname = parser.get(section, option)
                    test = eval(cases[testname])(devicelist, path)
                    suite.addTest(test)

    return suite


class TestExecutor:
    parser = ConfigParser.ConfigParser()
    parser.read('FrameworkConfig.cfg')
    path = None
    suite = unittest.TestSuite()
    casedictionary = {}

    def __init__(self, path):
        self.path = path
        dictfile = open('CaseDict.txt', 'r')
        dictlines = dictfile.readlines()
        dictfile.close()
        for line in dictlines:
            (key, value) = line.split()
            self.casedictionary[key] = value

    def parsefromargs(self, devicelist, args):
        casename, index1, index2 = (None,) * 3
        for i in range(2, len(args)):
            if casename is None:
                casename = args[i]
            elif index1 is None:
                index1 = getdeviceindex(devicelist, args[i])
                if index1 == -1:
                    print 'index error'
                    casename, index1, index2 = (None,) * 3
                    continue
                elif i == (len(args) - 1):
                    tmplist = [devicelist[index1]]
                    self.suite = handletags(casename, tmplist, self.casedictionary, self.path, self.suite)
                    test = eval(self.casedictionary[casename])(tmplist, self.path)
                    self.suite.addTest(test)
                    casename, index1, index2 = (None,) * 3
            elif index2 is None:
                try:
                    index2 = getdeviceindex(devicelist, args[i])
                    if index1 == index2 or index2 == -1:
                        print'index error'
                        casename, index1, index2 = (None,) * 3
                        continue
                    tmplist = [devicelist[index1], devicelist[index2]]
                    try:
                        self.suite = handletags(casename, tmplist, self.casedictionary, self.path, self.suite)
                        test = eval(self.casedictionary[casename])(tmplist, self.path)
                        self.suite.addTest(test)
                    except KeyError:
                        print 'unknown test'
                    casename, index1, index2 = (None,) * 3
                except TypeError:
                    # in this case, only 1 device is given
                    tmplist = [devicelist[index1]]
                    self.suite = handletags(casename, tmplist, self.casedictionary, self.path, self.suite)
                    test = eval(self.casedictionary[casename])(tmplist, self.path)
                    self.suite.addTest(test)
                    casename, index1, index2 = (None,) * 3

        self.execute()

    def parsefromconfig(self, devicelist):

        for section in self.parser.sections():
            try:
                # handle case where the devices are not index, but rather PCI ports
                index1 = getdeviceindex(devicelist, self.parser.get(section, 'device1'))
                if index1 == -1:
                    print 'Error parsing device, please use an index or PCI port'
                    continue
                tmplist = list()
                tmplist.append(devicelist[index1])
                try:
                    index2 = getdeviceindex(devicelist, self.parser.get(section, 'device2'))
                    if index2 == -1 or index1 == index2:
                        print 'Error parsing device, please use an index or PCI port'
                        continue
                    tmplist.append(devicelist[index2])
                except ConfigParser.NoOptionError:
                    print 'only 1 device'
                print('devices to test are:')
                print tmplist
                parsedcase = self.parser.get(section, 'test')
                try:
                    self.suite = handletags(parsedcase, tmplist, self.casedictionary, self.path, self.suite)
                    # if handletags(parsedcase, tmplist, dictionary, path):
                    #     continue
                    test = eval(self.casedictionary[parsedcase])(tmplist, self.path)
                except KeyError:
                    print 'unknown test'
                    test = None

                if test is not None:
                    self.suite.addTest(test)
            except ConfigParser.NoOptionError:
                if section == 'Meta':
                    pass
                else:
                    print ('section %s has no test option, or devices' % section)
        self.execute()

    def execute(self):
        runner = TAPTestRunner()
        runner.set_outdir('logs/TAP/')
        runner.set_format('{method_name} and {short_description}')
        runner.set_combined(True)
        runner.run(self.suite)
