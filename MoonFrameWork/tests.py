import unittest
import subprocess
import utility
import time
import sys
import os.path
from FrameworkSubprocess import SubHandler


class BindDevices(unittest.TestCase):
    # devicelist = list()
    logdir = 'logs/'
    logname = 'defaultLog'
    casename = 'default case name'
    testlog = None

    # testlog = open(logname, 'w') # this has to be overridden by subclass

    def __init__(self, devicelist, path):
        super(BindDevices, self).__init__()
        self.devicelist = devicelist
        self.path = path

    def setUp(self):  # set the devices
        print'printing setup'
        utility.binddevices(self.devicelist)
        self.initTestlog()

    def tearDown(self):
        print'printing teardown'
        utility.unbinddevices(self.devicelist)
        self.testlog.close()

    def initTestlog(self):
        self.logname = self.logdir + self.logname
        # check if a file exists with this name
        if os.path.isfile(self.logname):
            i = 2
            while os.path.isfile(self.logname + str(i)):
                i += 1
            self.logname += str(i)
        self.testlog = open(self.logname, 'w')

    def writetoread(self):
        self.testlog.close()
        self.testlog = open(self.logname, 'r')


class TerminatingTest(BindDevices):
    duration = 20
    pollrate = 2
    casename = 'default terminating / simple case name'
    termtimelimit = 2  # was 4
    termloopdelta = 0.5
    resulttolorance = 0.9  # type: float
    testlog = None

    def terminate(self, process):
        timecounter = 0
        while timecounter < self.duration:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(self.pollrate)
            timecounter += self.pollrate
        print''
        process.terminate()
        # check if process terminated, if not report a bug
        print'Printing process.poll():-----'
        # time.sleep(20)  # trying a delay before the poll
        timecounter = 0
        while process.poll() is None or timecounter <= self.termtimelimit:
            time.sleep(self.termloopdelta)
            timecounter += self.termloopdelta
            sys.stdout.write('.')
            sys.stdout.flush()
        print''
        print process.poll()
        print('Time it took to terminate: %d' % timecounter)
        # if process.poll() is None:
        if process.returncode is None:
            process.kill()
            print'Process not terminated!--'

    def runTest(self):
        print("=====Testing MoonGen Simple Case: %s, this will take %d seconds" % (self.casename, int(self.duration)))
        p = self.executetest()
        # p.wait()
        # print 'udp simple test launched, terminates in 20 seconds'
        # time.sleep(20)
        # p.terminate()
        self.terminate(p)
        self.writetoread()
        print('terminated, closed test log')
        # sucess yet to be specified
        self.checkresult()

    def executetest(self):
        return subprocess.Popen()

    def evaluate(self, lines, index):
        result = True
        for i in range(index, len(lines)):
            if not result:
                break
            # if '[FATAL]' in lines[i]:
            #     self.assertTrue(False, msg='FATAL error')
            if '[Device: id=0]' in lines[i]:
                line1 = lines[i].split()
                for j in range(0, len(line1)):
                    if 'TX' in line1[j]:
                        txvalue = float(line1[j + 1])
                        if '[Device: id=1]' not in lines[i + 1]:
                            continue
                        line2 = lines[i + 1].split()
                        for k in range(0, len(line2)):
                            if 'RX' in line2[k]:
                                rxvalue = float(line2[k + 1])
                                self.checkvaluesarezero(txvalue, rxvalue)
                                result = result and (rxvalue > txvalue * self.resulttolorance)
                                break
                        break
        self.assertTrue(result,
                        msg='This means that the RX values were not over 90 percent of TX values at all times')

    # def getloglines(self):
    #     self.testlog = open(self.logname, 'r')
    #     lines = self.testlog.readlines()
    #     self.testlog.close()
    #     return lines

    def checkdevicesfound(self, lines):
        for i in range(0, len(lines)):
            if 'Found 0 usable devices:' in lines[i]:
                self.assertTrue(False, msg='Found 0 usable devices. Possible reasons: no devices, hugepages')
            elif '2 devices are up' in lines[i]:
                return i
        self.assertTrue(False, msg='Devices are not up')

    def checkresult(self):
        lines = self.testlog.readlines()
        index = self.checkdevicesfound(lines)
        print 'value of index is: '
        print index
        self.evaluate(lines, index)

    def checkvaluesarezero(self, value1, value2):
        if value1 == 0.0 and value2 == 0.0:
            self.assertTrue(False, msg='TX / RX values are 0. Test might not be suited for testd devices')


class TestSimpleUDP(TerminatingTest):
    logname = 'udpSimpleTestLog'
    # testlog = open(logname, 'w')
    casename = 'udp simple'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
            stdout=self.testlog, cwd=self.path)

    # def evaluate(self, lines, index):
    #     # parse the log file, assert crateria
    #     # self.testlog = open(self.logname, 'r')
    #     # lines = self.testlog.readlines()
    #     # self.testlog.close()
    #     result = True
    #     for i in range(index, len(lines)):
    #         if not result:
    #             break
    #         if '[FATAL]' in lines[i]:
    #             self.assertTrue(False, msg='FATAL error')
    #         # exit condition: found 0 usable devices
    #         # if 'Found 0 usable devices:' in lines[i]:
    #         #     self.assertTrue(False, msg='There are no usable devices')
    #         # make sure device: id=0
    #         if '[Device: id=0]' in lines[i]:
    #             # store value
    #             line1 = lines[i].split()
    #             for j in range(0, len(line1)):
    #                 if '[0m: ' in line1[j]:
    #                     txvalue = float(line1[j + 1])
    #                     if '[Device: id=1]' not in lines[i + 1]:
    #                         continue
    #                     line2 = lines[i + 1].split()
    #                     for k in range(0, len(line2)):
    #                         if '[0m: ' in line2[k]:
    #                             rxvalue = float(line2[k + 1])
    #                             self.checkvaluesarezero(txvalue, rxvalue)
    #                             result = result and (rxvalue > txvalue * self.resulttolorance)
    #                             break
    #                     break
    #     self.assertTrue(result,
    #                     msg='This means that the RX values were not over %d \% of TX values at all times'
    #                         % (self.resulttolorance * 100.0))


class TestLoadLatency(TerminatingTest):
    logname = 'loadlatencylog'
    # testlog = open(logname, 'w')
    casename = 'load latency'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'load-latency:0:1:rate=1000,timeLimit=10m'],
            stdout=self.testlog, cwd=self.path)

    # def evaluate(self, lines, index):
    #     result = True
    #     for i in range(index, len(lines)):
    #         if not result:
    #             break
    #         if '[Device: id=0]' in lines[i]:
    #             line1 = lines[i].split()
    #             for j in range(0, len(line1)):
    #                 if 'TX:' in line1[j]:
    #                     txvalue = float(line1[j + 1])
    #                     if '[Device: id=1]' not in lines[i + 1]:
    #                         continue
    #                     line2 = lines[i + 1].split()
    #                     for k in range(0, len(line2)):
    #                         if 'RX:' in line2[k]:
    #                             rxvalue = float(line2[k + 1])
    #                             self.checkvaluesarezero(txvalue, rxvalue)
    #                             result = result and (rxvalue > txvalue * self.resulttolorance)
    #                             break
    #                     break
    #     self.assertTrue(result,
    #                     msg='This means that the RX values were not over %d \% of TX values at all times'
    #                         % (self.resulttolorance * 100.0))


class TestUdpLoad(TerminatingTest):
    logname = 'udploadlog'
    # testlog = open(logname, 'w')
    casename = 'udp load'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-load:0:1:rate=1mp/s,mode=all,timestamp'],
            stdout=self.testlog, cwd=self.path)


class TestQosForeground(TerminatingTest):
    logname = 'qosforegroundlog'
    # testlog = open(logname, 'w')
    casename = 'qos-foreground'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'qos-foreground:0:1'],
            stdout=self.testlog, cwd=self.path)


class TestQosBackground(TerminatingTest):
    logname = 'qosbackgroundlog'
    casename = 'qos-background'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'qos-background:0:1'],
            stdout=self.testlog, cwd=self.path)


class TestDeviceStatistics(TerminatingTest):
    logname = 'devicestatisticslog'
    casename = 'device statistics'

    def executetest(self):
        return subprocess.Popen([
            './build/Moongen', './examples/device-statistics.lua', '0', '1'],
            stdout=self.testlog, cwd=self.path)


class TestTimeStampCapabilities(BindDevices):
    reqpasses = 2
    logname = 'timestamplog'
    waitinterval = 2

    # testlog = open(logname, 'w')

    # test timestamp between NICs
    def runTest(self):
        print("Testing MoonGen TimeStamp Capabilities of devices: %s and %s"
              % (self.devicelist[0], self.devicelist[1]))
        p = subprocess.Popen(['./build/MoonGen',
                              './examples/timestamping-tests/test-timestamping-capabilities.lua',
                              '0', '1'], stdout=self.testlog, cwd=self.path)
        while p.poll() is None:
            time.sleep(self.waitinterval)
            sys.stdout.write('.')
            sys.stdout.flush()
        print''
        self.testlog.close()
        self.testlog = open(self.logname, 'r')
        lines = self.testlog.readlines()
        testquant = 0
        errorcounter = 0
        for index in range(0, len(lines)):
            if 'Testing' in lines[index]:
                testquant += 1
            if 'Error' in lines[index] or 'ERROR' in lines[index]:
                errorcounter += 1
                print 'Found error in a line!'
                print(lines[index])
                target = ''
                out = ''
                backtrack = 0
                while target != '\n':
                    out = target
                    target = lines[index - backtrack]
                    backtrack += 1
                print'Following case failed:'
                print(out)

        print'Timestamping conducted %d tests, %d errors came up' % (testquant, errorcounter)
        self.assertTrue(testquant - errorcounter > self.reqpasses,
                        msg='Selected devices have passed less than %d tests in Test Timestamping Capabilities'
                            % self.reqpasses)
