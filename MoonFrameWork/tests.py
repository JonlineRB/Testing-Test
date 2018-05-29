import unittest
import subprocess
import utility
import time
import sys
from FrameworkSubprocess import SubHandler


class BindDevices(unittest.TestCase):
    # devicelist = list()
    logname = 'defaultLog'
    casename = 'default case name'

    # testlog = open(logname, 'w') # this has to be overridden by subclass

    def __init__(self, devicelist, path):
        super(BindDevices, self).__init__()
        self.devicelist = devicelist
        self.path = path

    # @classmethod
    # def setUpClass(cls):
    #     # cls.testlog = open('testlog', 'w')
    #     print('called setup class')
    #     utility.binddevices(cls.devicelist)
    #
    # @classmethod
    # def tearDownClass(cls):
    #     print('called teardown class')
    #     cls.testlog.close()
    #     utility.unbinddevices(cls.devicelist)

    def setUp(self):  # set the devices
        print'printing setup'
        utility.binddevices(self.devicelist)

    def tearDown(self):
        print'printing teardown'
        utility.unbinddevices(self.devicelist)


class TerminatingTest(BindDevices):
    duration = 20
    pollrate = 2
    casename = 'default terminating / simple case name'
    termtimelimit = 2  # was 4
    termloopdelta = 0.5
    resulttolorance = 0.9

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
        self.testlog.close()
        print('terminated, closed test log')
        # sucess yet to be specified
        self.evaluate()
        # if self.evaluate():
        #     print('test successful')
        # else:
        #     print'test failed'

    def executetest(self):
        return subprocess.Popen()

    def evaluate(self):
        return self.assertEquals(True, True)


class TestSimpleUDP(TerminatingTest):
    logname = 'udpSimpleTestLog'
    testlog = open(logname, 'w')
    casename = 'udp simple'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
            stdout=self.testlog, cwd=self.path)

    def evaluate(self):
        # parse the log file, assert crateria
        self.testlog = open(self.logname, 'r')
        lines = self.testlog.readlines()
        result = True
        for i in range(0, len(lines)):
            # exit condition: found 0 usable devices
            if 'Found 0 usable devices:' in lines[i]:
                self.testlog.close()
                self.assertTrue(False, msg='There are no usable devices')
            # make sure device: id=0
            if '[Device: id=0]' in lines[i]:
                # store value
                line1 = lines[i].split()
                for j in range(0, len(line1)):
                    if '[0m: ' in line1[j]:
                        txvalue = float(line1[j + 1])
                        if '[Device: id=0]' not in lines[i + 1]:
                            pass
                        line2 = lines[i + 1].split()
                        for k in range(0, len(line2)):
                            if '[0m: ' in line2[k]:
                                rxvalue = float(line2[k + 1])
                                # return self.assertGreaterEqual(rxvalue, txvalue * self.resulttolorance)
                                result = result and (rxvalue < txvalue * self.resulttolorance)
        self.testlog.close()
        self.assertTrue(result,
                        msg='This means that the RX values were not over d% percent of TX values at all times'
                            % (self.resulttolorance * 100.0))


class TestLoadLatency(TerminatingTest):
    logname = 'loadlatencylog'
    testlog = open(logname, 'w')
    casename = 'load latency'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'load-latency:0:1:rate=1000,timeLimit=10m'],
            stdout=self.testlog, cwd=self.path)

    def evaluate(self):
        self.assertTrue(False)  # just to experiment


class TestUdpLoad(TerminatingTest):
    testlog = open('udploadlog', 'w')
    casename = 'udp load'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-load:0:1:rate=1mp/s,mode=all,timestamp'],
            stdout=self.testlog, cwd=self.path)


class TestQosForeground(TerminatingTest):
    testlog = open('qoslog', 'w')
    casename = 'qos-foreground'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'qos-foreground:0:1 qos-background:0:1'],
            stdout=self.testlog, cwd=self.path)


class TestTimeStampCapabilities(BindDevices):
    # test timestamp between NICs
    def runTest(self):
        print("Testing MoonGen TimeStamp Capabilities of devices: %s and %s"
              % (self.devicelist[0], self.devicelist[1]))
        p = subprocess.Popen(['./build/MoonGen',
                              './examples/timestamping-tests/test-timestamping-capabilities.lua',
                              '0', '1'], stdout=self.testlog, cwd=self.path)
        p.wait()
        self.testlog.close()
        self.testlog = open('testlog', 'r')
        lines = self.testlog.readlines()
        testquant = 0
        print("number of tests is: %d" % testquant)
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

        if not self.assertEquals(errorcounter, testquant):
            print('Tests successful, Conducted %d tests, %d occured' % testquant, errorcounter)
        else:
            print 'All tests failed'
        self.testlog.close()
