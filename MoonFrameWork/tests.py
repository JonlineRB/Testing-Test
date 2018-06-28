import unittest
import subprocess
import utility
import time
import sys
import os.path
from datetime import datetime
from DisplayValue import DisplayValue
import ScapyTest


# from FrameworkSubprocess import SubHandler


# stores all of the relevant test cases for MoonGen
# how to expand: run the script you wish to expand and identify
# to what it fits. For example, simple UDP will be a direct subclass
# of TerminatingTest, but dump.lua will inherit from SingleDevice.
# once a suitable superclass has been found, following need to be overriden:
# logname - name of the log files, casename - name to print while running the test,
# self.executetest - should return a subprocess.Popen that runs the desired test.
# for any further handling, look into the other methods and override them as needed.

class BindDevices(unittest.TestCase):
    # devicelist = list()
    logdir = 'logs/'
    logname = 'defaultLog'
    casename = 'default case name'
    testlog = None
    summarylog = None

    def __init__(self, devicelist, path):
        super(BindDevices, self).__init__()
        self.devicelist = devicelist
        self.path = path

    def setUp(self):  # set the devices
        utility.binddevices(self.devicelist, self.path)
        self.initTestlog()

    def tearDown(self):
        utility.unbinddevices(self.devicelist, self.path)
        self.testlog.close()
        self.summarylog.write('\n=== END OF SUMMARY ===\n')
        self.summarylog.close()

    def initTestlog(self):
        # check if, in the log dir, a dir with this date is available
        now = datetime.now()
        datesuffix = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
        self.logdir += datesuffix + '/'
        if not os.path.isdir(self.logdir):
            os.mkdir('logs/' + datesuffix)
        self.logname = self.logdir + self.logname
        self.logname += '_' + str(now.hour) + ':' + str(now.minute) + ':' + str(now.second)
        self.testlog = open(self.logname + '.txt', 'w')
        self.summarylog = open(self.logname + '_summary.txt', 'w')
        self.summarylog.write('=== SUMMARY ===\n\n')

    def writetoread(self):
        self.testlog.close()
        self.testlog = open(self.logname + '.txt', 'r')


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
        # check if process terminated
        print'Waiting for termination'
        timecounter = 0
        while process.poll() is None or timecounter <= self.termtimelimit:
            time.sleep(self.termloopdelta)
            timecounter += self.termloopdelta
            sys.stdout.write('.')
            sys.stdout.flush()
        print''
        print('Time it took to terminate: %d sec' % timecounter)
        # if process.poll() is None:
        if process.returncode is None:
            process.kill()
            print'Process not terminated!'
            self.assertTrue(False, msg='Process has not terminated')

    def runTest(self):
        print("\nTesting MoonGen Case: %s, this will take %d seconds" % (self.casename, int(self.duration)))
        p = self.executetest()
        self.terminate(p)
        self.writetoread()
        print('terminated, closed test log')
        self.checkresult()

    def executetest(self):
        return subprocess.Popen()

    def checkalerts(self, lines, index):
        if 'not supported on this device' in lines[index]:
            self.assertTrue(False, msg='Device is not suited for this test')
        elif 'NICs incompatible' in lines[index]:
            self.assertTrue(False, msg='Devices are not compatible')
        if '[FATAL]' in lines[index] or '[ERROR]' in lines[index] or '[WARN]' in lines[index]:
            print lines[index]
            self.summarylog.write(lines[index] + '\n')
        elif 'Saving histogram to' in lines[index]:
            for i in range(index, len(lines)):
                self.summarylog.write(lines[i])
            self.summarylog.write('\n')
            return False
        return True

    def evaluate(self, lines, index):
        result = True
        # tx / rx values
        txvalues = DisplayValue('Mpps', 'TX Values')
        rxvalues = DisplayValue('Mpps', 'RX Values')
        firstvalueskip = True

        # method parses relevant data from the log file
        for i in range(index, len(lines)):
            if not result:
                break
            if self.checkalerts(lines, i) is False:
                break
            elif '[Device: id=0]' in lines[i]:
                if firstvalueskip:
                    firstvalueskip = False
                    continue
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
                                if self.checkvaluesarezero(txvalue, rxvalue) is True:
                                    result = False
                                # adjust values
                                txvalues.aggregate(txvalue)
                                rxvalues.aggregate(rxvalue)
                                result = result and (rxvalue > txvalue * self.resulttolorance)
                                break
                        break

        self.summarylog.write(txvalues.tostring())
        self.summarylog.write(rxvalues.tostring())

        self.summarylog.write(
            '\nConclusion: has RX value always been at least ' + str(self.resulttolorance * 100) + ' % of TX? : ' + str(
                result) + '\n')
        self.assertTrue(result,
                        msg='This means that the RX values were not over 90 percent of TX values at all times')

    def checkdevicesfound(self, lines):
        for i in range(0, len(lines)):
            self.checkalerts(lines, i)
            if 'Found 0 usable devices:' in lines[i]:
                msg = 'Found 0 usable devices. Possible reasons: no devices, hugepages'
                self.summarylog.write(msg + '\n')
                self.assertTrue(False, msg=msg)
            elif '2 devices are up' in lines[i]:
                return i
        self.summarylog.write('Devices were not up\n')
        self.assertTrue(False, msg='Devices are not up')

    def checkresult(self):
        lines = self.testlog.readlines()
        index = self.checkdevicesfound(lines)
        self.evaluate(lines, index)

    def checkvaluesarezero(self, value1, value2):
        if value1 == 0.0 and value2 == 0.0:
            msg = 'TX / RX values are 0. Test might not be suited for testd devices'
            self.summarylog.write(msg + '\n')
            self.assertTrue(False, msg=msg)
            return True


class SingleDevice(TerminatingTest):

    def checkdevicesfound(self, lines):
        for i in range(0, len(lines)):
            if 'Found 0 usable devices:' in lines[i]:
                msg = 'Found 0 usable devices. Possible reasons: no devices, hugepages'
                self.summarylog.write(msg + '\n')
                self.assertTrue(False, msg=msg)
            elif '1 device is up' in lines[i] or ('Device 0' in lines[i] and 'is up' in lines[i]):
                return i
        self.summarylog.write('Device is not up\n')
        self.assertTrue(False, msg='Device is not up')


class SingleZeroRXValue(SingleDevice):

    def evaluate(self, lines, index):
        result = True
        for i in range(index, len(lines)):
            self.checkalerts(lines, index)
            if 'Packets counted' in lines[i]:
                result = result and (float(lines[i].split()[3]) == 0.0)
        self.summarylog.write('Condition: Have all values been 0? ' + '\nResult: ' + str(result))
        self.assertTrue(result, msg='Not all values were zero')


class SingleNonZeroTXValue(SingleDevice):

    def checkvaluesarezero(self, value1):
        if value1 == 0.0:
            return True
        return False

    def adjustvalues(self, vallist, txvalue, firstrun):
        if txvalue > vallist[0]:
            vallist[0] = txvalue
            if firstrun:
                vallist[2] = txvalue
        if txvalue < vallist[2]:
            vallist[2] = txvalue
        vallist[1] += txvalue
        vallist[3] += 1

        return vallist

    def evaluate(self, lines, index):
        result = True
        ignorefirst = True
        txvalues = DisplayValue('Mpps', 'TX Values')
        for i in range(index, len(lines)):
            if not result:
                break
            self.checkalerts(lines, i)
            if 'TX' in lines[i]:
                if ignorefirst:
                    ignorefirst = False
                    continue
                value = float(lines[i].split()[3])
                txvalues.aggregate(value)
                result = result and not self.checkvaluesarezero(value)

        self.summarylog.write(txvalues.tostring())
        self.summarylog.write('\nVerdict: have all values been greater than zero at all times: ' + str(result))
        self.assertTrue(result, msg='This means a value has been zero')


class TwoWayTerminatingTest(TerminatingTest):

    def initvalues(self):
        device1tx = DisplayValue('Mpps', 'Device 1 TX Values')
        device2tx = DisplayValue('Mpps', 'Device 2 TX Values')
        device1rx = DisplayValue('Mpps', 'Device 1 RX Values')
        device2rx = DisplayValue('Mpps', 'Device 2 RX Values')

        reslist = [device1tx, device2tx, device1rx, device2rx]
        return reslist

    def extractvalues(self, lines, index):
        reslist = list()
        if '[Device: id=0]' in lines[index]:
            reslist.append(float(lines[index].split()[3]))
        if '[Device: id=1]' in lines[index + 1]:
            reslist.append(float(lines[index].split()[3]))
        if '[Device: id=0]' in lines[index + 2]:
            reslist.append(float(lines[index].split()[3]))
        if '[Device: id=1]' in lines[index + 3]:
            reslist.append(float(lines[index].split()[3]))

        if None not in reslist and len(reslist) == 4:
            return reslist
        else:
            return None

    def checkvaluesarezero(self, values):
        result = False
        for value in values:
            result = result or (value != 0.0)
        if result is False:
            msg = 'All values are 0.0\n'
            self.summarylog.write(msg)
            self.assertTrue(False, msg=msg)

    def evaluate(self, lines, index):
        result = True
        vallist = self.initvalues()
        firstvalueskip = True
        for i in range(index, len(lines)):
            if not result:
                break
            if self.checkalerts(lines, i) is False:
                break
            elif '[Device: id=0]' in lines[i] and 'TX' in lines[i]:
                if firstvalueskip is True:
                    i += 3
                    firstvalueskip = False
                    continue
                else:
                    tmpval = self.extractvalues(lines, i)
                    if tmpval is not None:
                        self.checkvaluesarezero(tmpval)
                        for j in range(0, len(vallist)):
                            vallist[j].aggregate(tmpval[j])
                        result = result and (tmpval[3] > self.resulttolorance * tmpval[0] and
                                             tmpval[2] > self.resulttolorance * tmpval[1])

        for value in vallist:
            self.summarylog.write(value.tostring())

        self.summarylog.write(
            'Conclusion: has RX value always been at least ' + str(
                self.resulttolorance * 100) + ' % of TX on both ways? : ' + str(
                result) + '\n')
        self.assertTrue(result,
                        msg='This means that the RX values were not over'
                            '90 percent of TX values at all times on both ways')


class OneTXTwoRXQueues(TerminatingTest):

    def checkvaluesarezero(self, value1, value2, value3):
        if value1 == 0 and value2 == 0 and value3 == 0:
            self.assertTrue(False, msg='Values are 0')

    def evaluate(self, lines, index):
        result = True
        ignorefirst = True
        vallist = [DisplayValue('Mpps', 'TX Values'), DisplayValue('Mpps', 'RX 1 Values'),
                   DisplayValue('Mpps', 'RX 2 Values')]
        for i in range(index, len(lines)):
            if (not result) and (not self.checkalerts(lines, i)):
                break
            if 'TX' in lines[i]:
                if ignorefirst:
                    ignorefirst = False
                    continue
                try:
                    txvalue = float(lines[i].split()[3])
                    if 'qid=1' in lines[i + 1] and 'qid=2' in lines[i + 2]:
                        rx1value = float(lines[i + 1].split()[4])
                        rx2value = float(lines[i + 2].split()[4])
                        result = result and ((rx1value + rx2value) > self.resulttolorance * txvalue)
                        curvalues = [txvalue, rx1value, rx2value]
                        for j in range(0, len(vallist)):
                            vallist[j].aggregate(curvalues[j])
                except IndexError:
                    continue

        for i in range(0, len(vallist)):
            self.summarylog.write(vallist[i].tostring())

        self.summarylog.write('\nVerdict: Has the sum of RX values been at least ' + str(
            self.resulttolorance * 100) + '% at all times: ' + str(True))
        self.assertTrue(result,
                        msg='This means RX sum has not been ' + str(self.resulttolorance * 100) + '% at all times')


class DevicesUpCheckedSeperately(TerminatingTest):

    def checkdevicesfound(self, lines):
        for i in range(0, len(lines)):
            self.checkalerts(lines, i)
            if 'Found 0 usable devices:' in lines[i]:
                msg = 'Found 0 usable devices. Possible reasons: no devices, hugepages'
                self.summarylog.write(msg + '\n')
                self.assertTrue(False, msg=msg)
            elif 'Device 0' in lines[i] and 'is up' in lines[i]:
                if len(self.devicelist) == 1:
                    return i
                else:
                    for j in range(i, len(lines)):
                        if 'Device 1' in lines[j] and 'is up' in lines[j]:
                            return j
        self.summarylog.write('Devices were not up\n')
        self.assertTrue(False, msg='Devices are not up')


class TestSimpleUDP(TerminatingTest):
    logname = 'udpSimpleTestLog'
    casename = 'udp simple'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
            stdout=self.testlog, cwd=self.path)


class TestLoadLatency(TerminatingTest):
    logname = 'loadlatencylog'
    casename = 'load latency'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'load-latency:0:1:rate=1000,timeLimit=10m'],
            stdout=self.testlog, cwd=self.path)


class TestUdpLoad(TerminatingTest):
    logname = 'udploadlog'
    casename = 'udp load'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-load:0:1:rate=1mp/s,mode=all,timestamp'],
            stdout=self.testlog, cwd=self.path)


class TestQosForeground(TerminatingTest):
    logname = 'qosforegroundlog'
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
            './build/MoonGen', './examples/device-statistics.lua', '0', '1'],
            stdout=self.testlog, cwd=self.path)


class TestL2LoadLatency(TwoWayTerminatingTest):
    logname = 'l2loadlatencylog'
    casename = 'L2 Load Latency'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/l2-load-latency.lua', '0', '1'],
            stdout=self.testlog, cwd=self.path)


class TestL2PoissonLoadLatency(TerminatingTest):
    logname = 'l2poissonloadlatencylog'
    casename = 'L2 Poisson Load Latency'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/l2-poisson-load-latency.lua', '0', '1'],
            stdout=self.testlog, cwd=self.path)


class TestL3LoadLatency(TerminatingTest):
    logname = 'l3loadlatencylog'
    casename = 'L3 Load Latency'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/l3-load-latency.lua', '0', '1'],
            stdout=self.testlog, cwd=self.path)


class TestDump(SingleZeroRXValue):
    logname = 'dumplog'
    casename = 'Dump'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/dump.lua', '0'
        ], stdout=self.testlog, cwd=self.path)


class TestL3TcpSynFlood(DevicesUpCheckedSeperately):
    logname = 'l3tcpsynfloodlog'
    casename = 'L3 TCP-Syn-Flood'

    def initvalues(self):
        if len(self.devicelist) == 2:
            reslist = [DisplayValue('Mpps', 'TX Values of Device 1'),
                       DisplayValue('Mpps', 'TX Values of Device 2')]
            return reslist
        else:
            return [DisplayValue('Mpps', 'TX Values')]

    def executetest(self):
        args = ['./build/MoonGen', './examples/l3-tcp-syn-flood.lua', '0']
        if len(self.devicelist) == 2:
            args.append('1')
        return subprocess.Popen(args, stdout=self.testlog, cwd=self.path)

    def evaluate(self, lines, index):
        result = True
        vallist = self.initvalues()
        firstvalueskip = True
        for i in range(index, len(lines)):
            self.checkalerts(lines, index)
            if 'Device: id=0' in lines[i]:
                if firstvalueskip:
                    firstvalueskip = False
                    continue
                tx1value = float(lines[i].split()[3])
                if tx1value == 0.0:
                    self.assertTrue(False, msg='TX value was 0')
                if len(self.devicelist) == 1:
                    # vallist = self.adjustvalues(vallist, tx1value, None, firstminmax)
                    vallist[0].aggregate(tx1value)
                    # firstminmax = False
                    # avgcounter += 1
                else:
                    try:
                        tx2value = float(lines[i + 1].split()[3])
                        self.checkvaluesarezero(tx1value, tx2value)
                        # vallist = self.adjustvalues(vallist, tx1value, tx2value, firstminmax)
                        # firstminmax = False
                        # avgcounter += 1
                        vallist[0].aggregate(tx1value)
                        vallist[1].aggregate(tx2value)
                    except IndexError:
                        continue

        for value in vallist:
            self.summarylog.write(value.tostring())

        # might be temporary, this test has no conditions to live up to
        #  other than it's values aren't 0 and device/s are up
        self.assertTrue(result, msg='Something went wrong')


class TestQualityOfService(TerminatingTest):
    logname = 'qualityofservicelog'
    casename = 'Quality of Service'

    def executetest(self):
        return subprocess.Popen(['./build/MoonGen', './examples/quality-of-service-test.lua', '0', '1'],
                                stdout=self.testlog, cwd=self.path)

    def extractport(self, port):
        result = ''
        for c in port:
            if not str(c).isdigit():
                break
            result += str(c)
        return result

    def evaluate(self, lines, index):
        result = True
        # firstvalueskip = True

        firstportline = lines[index + 1].split()
        firstport = firstportline[len(firstportline) - 1]

        firstport = self.extractport(firstport)
        self.summarylog.write("value of firstport is: " + firstport + '\n')
        secondportline = lines[index + 2].split()
        secondport = secondportline[len(secondportline) - 1]
        secondport = self.extractport(secondport)

        firstporttxvalues = DisplayValue('Mpps', 'First Port TX Values')
        firstportrxvalues = DisplayValue('Mpps', 'First Port RX Values')
        secondporttxvalues = DisplayValue('Mpps', 'Second Port TX Values')
        secondportrxvalues = DisplayValue('Mpps', 'Second Port RX Values')

        for i in range(index, len(lines)):

            self.checkalerts(lines, i)
            if '[Port' in lines[i]:
                value = float(lines[i].split()[3])
                if str(firstport) in lines[i]:
                    if 'TX' in lines[i]:
                        firstporttxvalues.aggregate(value)
                    elif 'RX' in lines[i]:
                        firstportrxvalues.aggregate(value)
                elif secondport in lines[i]:
                    if 'TX' in lines[i]:
                        secondporttxvalues.aggregate(value)
                    elif 'RX' in lines[i]:
                        secondportrxvalues.aggregate(value)

        printlist = [firstporttxvalues, firstportrxvalues, secondporttxvalues, secondportrxvalues]
        for value in printlist:
            self.summarylog.write(value.tostring())

        result = result and firstportrxvalues.maxval != 0 and firstportrxvalues.maxval != 0 and secondporttxvalues.maxval != 0 and secondportrxvalues.maxval != 0
        self.assertTrue(result, 'Some values were 0')  # tmp, may be refined


class TestRateControlMethods(SingleNonZeroTXValue):
    logname = 'ratecontrolmethodslog'
    casename = 'Rate Control Methods'

    def executetest(self):
        return subprocess.Popen(
            ['./build/MoonGen', './examples/rate-control-methods.lua', '0', '2', 'moongen', 'cbr', '1'],
            stdout=self.testlog, cwd=self.path)


class TestRSS(OneTXTwoRXQueues):
    logname = 'rsslog'
    casename = 'RSS'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/rss.lua', '0', '1', '2'
        ], stdout=self.testlog, cwd=self.path)


class TestRXPktsDistribution(SingleZeroRXValue):
    logname = 'rxpktsdistributionlog'
    casename = 'RX Pkts Distribution'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/rx-pkts-distribution.lua', '0', '60'
        ], stdout=self.testlog, cwd=self.path)


class TestVXLANexample(DevicesUpCheckedSeperately):
    logname = 'vxlanexamplelog'
    casename = 'VXLAN Example'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/vxlan-example.lua', '0', '1', '0', '0', '0'
        ], stdout=self.testlog, cwd=self.path)


class TestInterArrivalTimes(SingleDevice):
    logname = 'interarrivaltimeslog'
    casename = 'Inter Arrival Times'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/inter-arrival-times.lua', '0', '0'
        ], stdout=self.testlog, cwd=self.path)

    def evaluate(self, lines, index):
        result = False
        for i in range(index, len(lines)):
            self.checkalerts(lines, i)
            if 'Lost packets: ' in lines[i]:
                value = int(lines[i].split()[3])
                result = value == 0
                self.summarylog.write('Verdict: 0 packets have been lost: ' + str(result))
                self.assertTrue(result, 'This means packets have been lost')

        self.assertTrue(result, 'Unable to parse amount of packets lost')


class TestTimeStampsSoftware(SingleNonZeroTXValue):
    logname = 'timestampssoftwarelog'
    casename = 'Time Stamps Software'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/timestamping-tests/timestamps-software.lua', '0', '1', '1'
        ], stdout=self.testlog, cwd=self.path)


class TestTimeStampsDrift(TerminatingTest):
    logname = 'timestampdriftlog'
    casename = 'Time Stamping tests - Drift'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/timestamping-tests/drift.lua', '0', '1'
        ], stdout=self.testlog, cwd=self.path)

    def getvalue(self, string):
        result = ''
        for i in range(1, len(string)):
            result += string[i]
        return float(result)

    def evaluate(self, lines, index):
        ignorefirst = True
        values = DisplayValue('Nano Seconds', 'Clock difference values')
        for i in range(index, len(lines)):
            self.checkalerts(lines, i)
            if lines[i][0] == '-':
                if ignorefirst:
                    ignorefirst = False
                    continue
                value = self.getvalue(lines[i])
                values.aggregate(value)

        self.summarylog.write(values.tostring())
        self.assertTrue(True)


class TestPcapReply(SingleDevice):
    logname = 'pcapreplylog'
    casename = 'PCAP Reply'

    def executetest(self):
        # prefix = os.path.commonprefix([self.path, os.path.dirname(os.path.abspath(__file__))])
        relpath = os.path.relpath(os.path.dirname(os.path.abspath(__file__)), self.path)
        ScapyTest.generatepcap()
        print 'relpath is: ' + relpath
        return subprocess.Popen([
            # './build/MoonGen', './examples/pcap/replay-pcap.lua', '0', '../Testing-Test/MoonFrameWork/tmp.pcap'
            './build/MoonGen', './examples/pcap/replay-pcap.lua', '0', relpath + 'tmp.pcap'
        ], stdout=self.testlog, cwd=self.path)

    def evaluate(self, lines, index):
        # clean the tmp file here
        result = False
        for i in range(index, len(lines)):
            self.checkalerts(lines, i)
            if 'TX' in lines[i]:
                value = int(lines[i].split()[5])
                result = value > 0
                break

        ScapyTest.cleanpcap()
        self.summarylog.write('Is the value greater than 0 : ' + str(result))
        self.assertTrue(result, msg='Value has been 0')


class TestTimeStampCapabilities(BindDevices):
    reqpasses = 2
    logname = 'timestamplog'
    waitinterval = 2

    # test timestamp between NICs
    def runTest(self):
        print("\nTesting MoonGen TimeStamp Capabilities of devices: %s and %s"
              % (self.devicelist[0], self.devicelist[1]))
        p = subprocess.Popen(['./build/MoonGen',
                              './examples/timestamping-tests/test-timestamping-capabilities.lua',
                              '0', '1'], stdout=self.testlog, cwd=self.path)
        while p.poll() is None:
            time.sleep(self.waitinterval)
            sys.stdout.write('.')
            sys.stdout.flush()
        print''
        self.writetoread()
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
                self.summarylog.write('Error in: ' + out + ':\n' + lines[index])

        msg = 'Timestamping conducted %d tests, %d errors came up\n' % (testquant, errorcounter)
        print msg
        self.summarylog.write(msg)
        result = testquant - errorcounter > self.reqpasses
        self.summarylog.write('Verdict: Have the passed tests surpassed ' + str(self.reqpasses) + ': ' + str(result))
        self.assertTrue(result,
                        msg='Selected devices have passed less than %d tests in Test Timestamping Capabilities'
                            % self.reqpasses)
