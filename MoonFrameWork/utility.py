import os
import subprocess
import ConfigParser
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
    # modifying: only PCIe allowed
    for i in range(0, len(devicelist)):
        if arg == devicelist[i].split()[0]:
            return i
    print 'device not found! use PCI Express only!'
    return -1


# returns the testdir value from FrameworkConfig.cfg
def gettestdir():
    parser = ConfigParser.ConfigParser()
    parser.read('FrameworkConfig.cfg')
    try:
        return parser.get('Meta', 'testdir')
    except ConfigParser.NoOptionError or ConfigParser.NoSectionError:
        return None


class TestExecutor:
    parser = ConfigParser.ConfigParser()
    parser.read('FrameworkConfig.cfg')
    path = None
    suite = unittest.TestSuite()
    metadevice1 = -1
    metadevice2 = -1
    # adding a tag sotring variable
    tags = None

    def __init__(self, path, devicelist):
        self.path = path

        # construct tags
        self.tags = ConfigParser.ConfigParser()
        self.tags.read('TagConfig.cfg')

    def handletags(self, name, devicelist):
        result = unittest.TestSuite()
        # check whether the name is a tag or class
        if self.tags.has_section(name):  # check for a tag
            for option in self.tags.options(name):
                testname = self.tags.get(name, option)
                test = eval(testname)(devicelist, self.path)
                result.addTest(test)
            return result
        else:  # add the case as an individual
            try:
                test = eval(name)(devicelist, self.path)
                return test
            except NameError:
                print 'Unrecognized test: %s' % name

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
                    test = self.handletags(casename, tmplist)
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
                        test = self.handletags(casename, tmplist)
                        self.suite.addTest(test)
                    except KeyError:
                        print 'unknown test'
                    casename, index1, index2 = (None,) * 3
                except TypeError:
                    # in this case, only 1 device is given
                    tmplist = [devicelist[index1]]
                    test = self.handletags(casename, tmplist)
                    self.suite.addTest(test)
                    casename, index1, index2 = (None,) * 3

        self.execute()

    def parsefromconfig(self, devicelist):

        # set the values of default devices
        try:
            self.metadevice1 = getdeviceindex(devicelist, self.parser.get('Meta', 'device1'))
            print('default devices set: %d' % self.metadevice1)
        except ConfigParser.NoOptionError:
            print('no default device1 set')
        try:
            self.metadevice2 = getdeviceindex(devicelist, self.parser.get('Meta', 'device2'))
            print('default devices set: %d' % self.metadevice2)
        except ConfigParser.NoOptionError:
            print('no default device2 set')

        for section in self.parser.sections():

            if section == 'Meta':  # skip the meta section, it should not contain a test case
                continue

            try:
                # handle case where the devices are not index, but rather PCI ports
                if not self.parser.has_option(section, 'device1'):
                    index1 = self.metadevice1
                else:
                    index1 = getdeviceindex(devicelist, self.parser.get(section, 'device1'))
                if index1 == -1:
                    print 'Error parsing device, please use an index or PCI port'
                    continue
                tmplist = list()
                tmplist.append(devicelist[index1])
                if not self.parser.has_option(section, 'device2'):
                    index2 = self.metadevice2
                else:
                    index2 = getdeviceindex(devicelist, self.parser.get(section, 'device2'))
                if index2 == -1 or index1 == index2:
                    print 'device2 not included. This can also be an error' \
                          'due to value of -1, or identical value to device1'
                else:
                    tmplist.append(devicelist[index2])
                parsedcase = self.parser.get(section, 'test')
                try:
                    test = self.handletags(parsedcase, tmplist)
                except KeyError:
                    print 'unknown test'
                    test = None

                if test is not None:
                    self.suite.addTest(test)
            except ConfigParser.NoOptionError:
                print ('section %s has no test option' % section)
        self.execute()

    def execute(self):
        runner = TAPTestRunner()
        runner.set_outdir('logs/TAP/')
        runner.set_format('{method_name} and {short_description}')
        runner.set_combined(True)
        runner.run(self.suite)
