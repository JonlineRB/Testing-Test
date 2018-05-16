import unittest
import subprocess
import utility


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


# class TestSimpleUDP(BindDevices):
#     def runTest(self):
#         print("Testing MoonGen Simple Case: udp-simple")
#         p = subprocess.Popen([
#             './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
#             stdout=self.testlog, cwd=self.path)
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
        if self.assertEquals(p.wait(), 0):
            print("Test result: everything works!")
            # in this case, parse the out file in order to recieve information
            #  about the possible capabilities of these NICs
        else:
            print'Test result: something went wrong...'
            # parse out file for the cause of the test
# if __name__ == '__main__':
#     unittest.main()
