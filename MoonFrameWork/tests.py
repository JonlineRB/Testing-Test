import unittest
import subprocess
import utility


class BindDevices(unittest.TestCase):
    devicelist = list()
    testlog = open('testlog', 'w')
    path = ''

    def __init__(self, devicelist, path):
        super(BindDevices, self).__init__()
        self.devicelist = devicelist
        self.path = path

    @classmethod
    def setUpClass(cls):
        # cls.testlog = open('testlog', 'w')
        utility.binddevices(self.devicelist)

    @classmethod
    def tearDownClass(cls):
        cls.testlog.close()
        utility.unbinddevices(self.devicelist)
    # def setUp(self):  # set the devices


class TestSimpleUDP(BindDevices):
    def runTest(self):
        print("Testing MoonGen Simple Case: udp-simple")
        p = subprocess.Popen([
            './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
            stdout=self.testlog, cwd=self.path)
        # this subprocess does not terminate if it runs correctly
        # TO DO: solve this issue


class TestTimeStampCapabilities(BindDevices):
    # test timestamp between NICs
    def runTest(self):
        print("Testing MoonGen TimeStamp Capabilities of devices: %d and %d"
              % (self.devicelist[0], self.devicelist[1]))
        p = subprocess.Popen(['./build/MoonGen',
                              './examples/timestamping-tests/test-timestamping-capabilities.lua',
                              '0', '1'], stdout=self.testlog, cwd=self.path)
        self.assertEquals(p.wait(), 0)
