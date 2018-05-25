import os
import subprocess
import ConfigParser
from FrameworkSubprocess import SubHandler
import tests


# utility class for the MoonGen Testing framework

def parsedevices(dpdkdevlist):
    print('Framework: Parsing DPDK bound devices')
    # call a subprocess for dpdk-devbind, store the relevant results in a file
    # create a file
    initialbinds = open('initialBindState', 'w')
    # start this process
    p = subprocess.Popen(
        ['./dpdk-devbind.py', '-s'], stdout=initialbinds, cwd='/home/borowski/MoonGen/libmoon/deps/dpdk/usertools'
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


def unbinddevices(devicelist):
    for x in devicelist:
        p = subprocess.Popen(
            ['./dpdk-devbind.py', '-u', x.split()[0]], cwd='/home/borowski/MoonGen/libmoon/deps/dpdk/usertools'
        )
        p.wait()


def initdevices(devicelist):
    parsedevices(devicelist)
    if not devicelist:
        print('No devices are DPDK bound')
    else:
        print('parsed list is:')
        for x in range(0, len(devicelist)):
            print('device %d: ' % x + devicelist[x])
        unbinddevices(devicelist)


def binddevices(devicelist):
    if not devicelist:
        return
    for x in devicelist:
        p = subprocess.Popen(
            ['./dpdk-devbind.py', '--bind=igb_uio', x.split()[0]],
            cwd='/home/borowski/MoonGen/libmoon/deps/dpdk/usertools'
        )
        p.wait()
    # print('bound devices as they were')


def parsetestcases(devicelist):
    parser = ConfigParser.ConfigParser()
    parser.read('FrameworkConfig.cfg')
    try:
        path = parser.get('Meta', 'path')
    except ConfigParser.NoOptionError:
        print 'Path is not set. Please set a path in the config file in the [Meta] section'
    # for i in range(0, len(parser.sections())):
    for section in parser.sections():
        # parse the list, and handle test cases with respect to the listed NICs
        # switch case statements here: look for all known tests, execute relevant test cases with relevant devices
        # test with print
        try:
            index1 = int(parser.get(section, 'device1'))
            index2 = int(parser.get(section, 'device2'))
            tmplist = list()
            tmplist.append(devicelist[index1])
            tmplist.append(devicelist[index2])
            print('devices to test are:')
            print tmplist
            parsedcase = parser.get(section, 'test')
            print(' ==== parsed case is: %s ==== ' % parsedcase)
            # the following section should be a dictionary...
            if parsedcase == 'timestamp':
                # run timestamp test
                test = tests.TestTimeStampCapabilities(tmplist, path)
                # test.run()
            elif parsedcase == 'udpsimple':
                test = tests.TestSimpleUDP(tmplist, path)
                # test.run()
            elif parsedcase == 'loadlatency':
                test = tests.TestLoadLatency(tmplist, path)
                # test.run()
            elif parsedcase == 'qos':
                test = tests.TestQosForeground(tmplist, path)
                # test.run()
            elif parsedcase == 'udpload':
                test = tests.TestUdpLoad(tmplist, path)
                # test.run()
            else:
                print 'unknown test'
            if test is not None:
                test.run()
        except ConfigParser.NoOptionError:
            if section == 'Meta':
                pass
            else:
                print ('section %s has no test option, or devices' % section)
