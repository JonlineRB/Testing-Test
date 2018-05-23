import unittest
import subprocess
import utility
import signal
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


class TestSimpleUDP(BindDevices):
    def runTest(self):
        print("Testing MoonGen Simple Case: udp-simple")
        p = subprocess.Popen([
            './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
            stdout=self.testlog, cwd=self.path)
        p.wait()
# this subprocess does not terminate if it runs correctly
# TO DO: solve this issue


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
