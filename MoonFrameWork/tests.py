import unittest
import subprocess
import utility
import time
from FrameworkSubprocess import SubHandler


class BindDevices(unittest.TestCase):
    # devicelist = list()
    testlog = open('testlog', 'w')

    # path = ''

    def __init__(self, devicelist, path):
        super(BindDevices, self).__init__()
        self.devicelist = devicelist
        self.path = path

    @classmethod
    def setUpClass(cls):
        # cls.testlog = open('testlog', 'w')
        print('binding devices')
        utility.binddevices(cls.devicelist)

    @classmethod
    def tearDownClass(cls):
        cls.testlog.close()
        utility.unbinddevices(cls.devicelist)

    def setUp(self):  # set the devices
        utility.binddevices(self.devicelist)

    def tearDown(self):
        utility.unbinddevices(self.devicelist)


class TerminatingTest(BindDevices):
    duration = 20
    casename = ''

    def terminate(self, process):
        time.sleep(self.duration)
        process.terminate()

    def runTest(self):
        print("=====Testing MoonGen Simple Case: %s, this will take %d seconds" % self.casename, self.duration)
        p = self.executetest()
        # p.wait()
        # print 'udp simple test launched, terminates in 20 seconds'
        # time.sleep(20)
        # p.terminate()
        self.terminate(p)
        p.kill()  # this ensures the process has ended
        self.testlog.close()
        print('terminated, closed test log')
        # sucess yet to be specified
        if self.evaluate():
            print('test successful')
        else:
            print'test failed'

    def executetest(self):
        return subprocess.Popen()

    def evaluate(self):
        return self.assertEquals(True, True)


class TestSimpleUDP(TerminatingTest):
    testlog = open('udpSimpleTestLog', 'w')
    casename = 'udp simple'

    # def runTest(self):
    #     print("Testing MoonGen Simple Case: udp-simple")
    #     p = subprocess.Popen([
    #         './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
    #         stdout=self.testlog, cwd=self.path)
    #     # p.wait()
    #     # print 'udp simple test launched, terminates in 20 seconds'
    #     # time.sleep(20)
    #     # p.terminate()
    #     self.terminate(p)
    #     self.testlog.close()
    #     print('terminated, closed test log')
    #     # sucess yet to be specified
    #     self.assertTrue(True)

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
            stdout=self.testlog, cwd=self.path)


class TestLoadLatency(TerminatingTest):
    testlog = open('loadlatencylog', 'w')
    casename = 'load latency'

    # def runTest(self):
    #     print("Testing MoonGen Simple Case: load-latency")
    #     p = subprocess.Popen([
    #         './moongen-simple', 'start', 'load-latency:0:1:rate=1000,timeLimit=10m'],
    #         stdout=self.testlog, cwd=self.path)
    #     self.terminate(p)
    #     self.testlog.close()
    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'load-latency:0:1:rate=1000,timeLimit=10m'],
            stdout=self.testlog, cwd=self.path)


class TestUdpLoad(TerminatingTest):
    testlog = open('udploadlog')
    casename = 'udp load'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-load:0:1:rate=1mp/s,mode=all,timestamp'],
            stdout=self.testlog, cwd=self.path)


class TestQosForeground(TerminatingTest):
    testlog = open('qoslog')
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
