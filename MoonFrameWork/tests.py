import unittest
import subprocess
import utility
import time
import sys
import os.path
from datetime import datetime
from DisplayValue import DisplayValue


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
        self.logname += '_' + str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + '.txt'
        self.testlog = open(self.logname, 'w')
        self.summarylog = open(self.logname + '_summary.txt', 'w')
        self.summarylog.write('=== SUMMARY ===\n\n')

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
        print'Waiting for termination'
        # time.sleep(20)  # trying a delay before the poll
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
            print'Process not terminated!--'

    def runTest(self):
        print("Testing MoonGen Case: %s, this will take %d seconds" % (self.casename, int(self.duration)))
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

    valueindex = {'txmax': 0,
                  'rxmax': 1,
                  'txavg': 2,
                  'rxavg': 3,
                  'txmin': 4,
                  'rxmin': 5}

    def adjustvalues(self, vallist, txvalue, rxvalue, firstrun):
        if txvalue > vallist[self.valueindex['txmax']]:
            vallist[self.valueindex['txmax']] = txvalue
            if firstrun is True:
                vallist[self.valueindex['txmin']] = vallist[self.valueindex['txmax']]
        if txvalue < vallist[self.valueindex['txmin']]:
            vallist[self.valueindex['txmin']] = txvalue
        if rxvalue > vallist[self.valueindex['rxmax']]:
            vallist[self.valueindex['rxmax']] = rxvalue
            if firstrun is True:
                vallist[self.valueindex['rxmin']] = vallist[self.valueindex['rxmax']]
        if rxvalue < vallist[self.valueindex['rxmin']]:
            vallist[self.valueindex['rxmin']] = rxvalue

        vallist[self.valueindex['txavg']] += txvalue
        vallist[self.valueindex['rxavg']] += rxvalue

        return vallist

    def initvalues(self):
        # list stores interesting values, to be printed
        # 0     1       2      3      4      5
        txmax, rxmax, txavg, rxavg, txmin, rxmin = (0.0,) * 6
        reslist = [txmax, rxmax, txavg, rxavg, txmin, rxmin]
        return reslist

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

    def extractvalues(self, lines, index):
        return list()

    def evaluate(self, lines, index):
        result = True
        # tx / rx values
        vallist = self.initvalues()
        avgcounter = 0
        firstvalueskip = True
        firstminmax = True
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
                # TODO get the tx value
                line1 = lines[i].split()
                for j in range(0, len(line1)):
                    if 'TX' in line1[j]:
                        txvalue = float(line1[j + 1])
                        # TODO here get the rx value
                        if '[Device: id=1]' not in lines[i + 1]:
                            continue
                        line2 = lines[i + 1].split()
                        for k in range(0, len(line2)):
                            if 'RX' in line2[k]:
                                rxvalue = float(line2[k + 1])
                                if self.checkvaluesarezero(txvalue, rxvalue) is True:
                                    result = False
                                # adjust values
                                vallist = self.adjustvalues(vallist, txvalue, rxvalue, firstminmax)
                                if firstminmax is True:
                                    firstminmax = False
                                avgcounter += 1
                                # TODO here check result condition
                                result = result and (rxvalue > txvalue * self.resulttolorance)
                                break
                        break
        # TODO here adjust avarages
        vallist[self.valueindex['txavg']] /= float(avgcounter)  # tx avg
        vallist[self.valueindex['rxavg']] /= float(avgcounter)  # rx avg
        self.summarylog.write('TX / RX Values of this test case')
        # TODO here write reseults to log
        self.summarylog.write(
            'TX values are:\n MAX = ' + str(vallist[self.valueindex['txmax']]) + '\n MIN = ' + str(
                vallist[self.valueindex['txmin']]) + '\n AVG = ' + str(vallist[self.valueindex['txavg']]) + '\n')
        self.summarylog.write(
            'RX values are:\n MAX = ' + str(vallist[self.valueindex['rxmax']]) + '\n MIN = ' + str(
                vallist[self.valueindex['rxmin']]) + '\n AVG = ' + str(vallist[self.valueindex['rxavg']]) + '\n')
        self.summarylog.write(
            'Conclusion: has RX value always been at least ' + str(self.resulttolorance * 100) + ' % of TX? : ' + str(
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
        firstminmax = True
        vallist = [0.0, 0.0, 0.0, 0.0]  # value list with: max, avg, min, counter
        for i in range(index, len(lines)):
            if not result:
                break
            self.checkalerts(lines, i)
            if 'TX' in lines[i]:
                if ignorefirst:
                    ignorefirst = False
                    continue
                value = float(lines[i].split()[3])
                vallist = self.adjustvalues(vallist, value, firstminmax)
                result = result and not self.checkvaluesarezero(value)
                firstminmax = False

        self.summarylog.write(
            '\nTX Values: \nMAX: ' + str(vallist[0]) + '\nAVG: ' + str(vallist[1] / vallist[3]) + '\nMIN: ' + str(
                vallist[2]) + '\n')
        self.summarylog.write('\nVerdict: have all values been greater than zero at all times: ' + str(result))
        self.assertTrue(result, msg='This means a value has been zero')


class TwoWayTerminatingTest(TerminatingTest):

    def initvalues(self):
        # list stores interesting values, to be printed

        tx1max, tx2max, rx1max, rx2max, tx1avg, tx2avg, rx1avg, rx2avg, tx1min, tx2min, rx1min, rx2min = (0.0,) * 12
        device1 = [tx1max, rx1max, tx1avg, rx1avg, tx1min, rx1min]
        device2 = [tx2max, rx2max, tx2avg, rx2avg, tx2min, rx2min]
        reslist = [device1, device2]
        return reslist

    def extractvalues(self, lines, index):
        reslist = list()
        if '[Device: id=0]' in lines[index]:
            # reslist.append(self.parsevalue(lines[index].split(), 'RX'))
            reslist.append(float(lines[index].split()[3]))
        if '[Device: id=1]' in lines[index + 1]:
            reslist.append(float(lines[index].split()[3]))
            # reslist.append(self.parsevalue(lines[index].split(), 'RX'))
        if '[Device: id=0]' in lines[index + 2]:
            reslist.append(float(lines[index].split()[3]))
            # reslist.append(self.parsevalue(lines[index].split(), 'TX'))
        if '[Device: id=1]' in lines[index + 3]:
            reslist.append(float(lines[index].split()[3]))
            # reslist.append(self.parsevalue(lines[index].split(), 'TX'))

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
        avgcounter = 0
        firstvalueskip = True
        firstminmax = True
        for i in range(index, len(lines)):
            if not result:
                break
            if self.checkalerts(lines, i) is False:
                break
            elif '[Device: id=0]' in lines[i]:
                if firstvalueskip is True:
                    i += 3
                    firstvalueskip = False
                    continue
                else:
                    tmpval = self.extractvalues(lines, i)
                    if tmpval is not None:
                        self.checkvaluesarezero(tmpval)
                        # call adjust values here
                        vallist = self.adjustvalues(vallist, tmpval[2], tmpval[3], tmpval[0], tmpval[1], firstminmax)
                        firstminmax = False
                        avgcounter += 1
                        result = result and (tmpval[0] > self.resulttolorance * tmpval[3] and
                                             tmpval[1] > self.resulttolorance * tmpval[2])

        vallist[0][self.valueindex['txavg']] /= float(avgcounter)  # tx1 avg
        vallist[0][self.valueindex['rxavg']] /= float(avgcounter)  # rx1 avg
        vallist[1][self.valueindex['txavg']] /= float(avgcounter)  # tx2 avg
        vallist[1][self.valueindex['rxavg']] /= float(avgcounter)  # rx2 avg

        self.summarylog.write(
            'TX values of device 1 are:\n MAX = ' + str(vallist[0][self.valueindex['txmax']]) + '\n MIN = ' + str(
                vallist[0][self.valueindex['txmin']]) + '\n AVG = ' + str(vallist[0][self.valueindex['txavg']]) + '\n')
        self.summarylog.write(
            'RX values of device 1 are:\n MAX = ' + str(vallist[0][self.valueindex['rxmax']]) + '\n MIN = ' + str(
                vallist[0][self.valueindex['rxmin']]) + '\n AVG = ' + str(vallist[0][self.valueindex['rxavg']]) + '\n')
        self.summarylog.write(
            'TX values of device 2 are:\n MAX = ' + str(vallist[1][self.valueindex['txmax']]) + '\n MIN = ' + str(
                vallist[1][self.valueindex['txmin']]) + '\n AVG = ' + str(vallist[1][self.valueindex['txavg']]) + '\n')
        self.summarylog.write(
            'RX values of device 2 are:\n MAX = ' + str(vallist[1][self.valueindex['rxmax']]) + '\n MIN = ' + str(
                vallist[1][self.valueindex['rxmin']]) + '\n AVG = ' + str(vallist[1][self.valueindex['rxavg']]) + '\n')
        self.summarylog.write(
            'Conclusion: has RX value always been at least ' + str(
                self.resulttolorance * 100) + ' % of TX on both ways? : ' + str(
                result) + '\n')
        self.assertTrue(result,
                        msg='This means that the RX values were not over'
                            '90 percent of TX values at all times on both ways')

    def adjustvalues(self, vallist, tx1value, tx2value, rx1value, rx2value, firstrun):
        if tx1value > vallist[0][self.valueindex['txmax']]:
            vallist[0][self.valueindex['txmax']] = tx1value
            if firstrun is True:
                vallist[0][self.valueindex['txmin']] = vallist[0][self.valueindex['txmax']]
        if tx1value < vallist[0][self.valueindex['txmin']]:
            vallist[0][self.valueindex['txmin']] = tx1value
        if rx1value > vallist[0][self.valueindex['rxmax']]:
            vallist[0][self.valueindex['rxmax']] = rx1value
            if firstrun is True:
                vallist[0][self.valueindex['rxmin']] = vallist[0][self.valueindex['rxmax']]
        if rx1value < vallist[0][self.valueindex['rxmin']]:
            vallist[0][self.valueindex['rxmin']] = rx1value

        if tx2value > vallist[1][self.valueindex['txmax']]:
            vallist[1][self.valueindex['txmax']] = tx2value
            if firstrun is True:
                vallist[1][self.valueindex['txmin']] = vallist[1][self.valueindex['txmax']]
        if tx2value < vallist[1][self.valueindex['txmin']]:
            vallist[1][self.valueindex['txmin']] = tx2value
        if rx2value > vallist[1][self.valueindex['rxmax']]:
            vallist[1][self.valueindex['rxmax']] = rx2value
            if firstrun is True:
                vallist[1][self.valueindex['rxmin']] = vallist[1][self.valueindex['rxmax']]
        if rx2value < vallist[1][self.valueindex['rxmin']]:
            vallist[1][self.valueindex['rxmin']] = rx1value

        vallist[0][self.valueindex['txavg']] += tx1value
        vallist[0][self.valueindex['rxavg']] += rx1value
        vallist[1][self.valueindex['txavg']] += tx2value
        vallist[1][self.valueindex['rxavg']] += rx2value

        return vallist


class OneTXTwoRXQueues(TerminatingTest):

    def checkvaluesarezero(self, value1, value2, value3):
        if value1 == 0 and value2 == 0 and value3 == 0:
            self.assertTrue(False, msg='Values are 0')

    def adjustvalues(self, vallist, currvalues, firstrun):

        for i in range(0, 3):
            if currvalues[i] > vallist[i][0]:
                vallist[i][0] = currvalues[i]
                if firstrun:
                    vallist[i][2] = currvalues[i]
            if currvalues[i] < vallist[i][2]:
                vallist[i][2] = currvalues[i]
            vallist[i][1] += currvalues[i]
        vallist[3] += 1
        return vallist

    def evaluate(self, lines, index):
        result = True
        ignorefirst = True
        firstmimax = True
        vallist = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 0.0]
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
                        vallist = self.adjustvalues(vallist, curvalues, firstmimax)
                        firstmimax = False
                except IndexError:
                    continue

        titles = ['TX Values', 'RX 1 Values', 'RX 2 Values']
        for i in range(0, 3):
            self.summarylog.write(
                '\n' + titles[i] + '\nMAX: ' + str(vallist[i][0]) + '\nAVG: ' + str(vallist[i][1] / vallist[3])
                + '\nMIN: ' + str(vallist[i][2]) + '\n'
            )
        self.summarylog.write('Verdict: Has the sum of RX values been at least ' + str(
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
    # testlog = open(logname, 'w')
    casename = 'udp simple'

    def executetest(self):
        return subprocess.Popen([
            './moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
            stdout=self.testlog, cwd=self.path)


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
            './build/MoonGen', './examples/device-statistics.lua', '0', '1'],
            stdout=self.testlog, cwd=self.path)


class TestL2LoadLatency(TwoWayTerminatingTest):
    logname = 'l2loadlatencylog'
    casename = 'L2 Load Latency'

    def executetest(self):
        return subprocess.Popen([
            './build/MoonGen', './examples/l2-load-latency.lua', '0', '1'],
            stdout=self.testlog, cwd=self.path)

    # this class needs to read the log differently, it prints the values pairwise


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
            reslist = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            return reslist
        else:
            return [0.0, 0.0, 0.0]

    valueindex = {'tx1max': 0,
                  'tx1avg': 1,
                  'tx1min': 2,
                  'tx2max': 3,
                  'tx2avg': 4,
                  'tx2min': 5}

    def adjustvalues(self, vallist, tx1value, tx2value, firstrun):
        if tx1value > vallist[self.valueindex['tx1max']]:
            vallist[self.valueindex['tx1max']] = tx1value
            if firstrun:
                vallist[self.valueindex['tx1min']] = tx1value
        if tx1value < vallist[self.valueindex['tx1min']]:
            vallist[self.valueindex['tx1min']] = tx1value
        vallist[self.valueindex['tx1avg']] += tx1value

        if len(self.devicelist) == 2:
            if tx2value > vallist[self.valueindex['tx2max']]:
                vallist[self.valueindex['tx2max']] = tx2value
                if firstrun:
                    vallist[self.valueindex['tx2min']] = tx2value
            if tx2value < vallist[self.valueindex['tx2min']]:
                vallist[self.valueindex['tx2min']] = tx2value
            vallist[self.valueindex['tx2avg']] += tx2value

        return vallist

    def executetest(self):
        args = ['./build/MoonGen', './examples/l3-tcp-syn-flood.lua', '0']
        if len(self.devicelist) == 2:
            args.append('1')
        return subprocess.Popen(args, stdout=self.testlog, cwd=self.path)

    # def checkdevicesfound(self, lines):
    #     for i in range(0, len(lines)):
    #         self.checkalerts(lines, i)
    #         if 'Found 0 usable devices:' in lines[i]:
    #             msg = 'Found 0 usable devices. Possible reasons: no devices, hugepages'
    #             self.summarylog.write(msg + '\n')
    #             self.assertTrue(False, msg=msg)
    #         elif 'Device 0' in lines[i] and 'is up' in lines[i]:
    #             if len(self.devicelist) == 1:
    #                 return i
    #             else:
    #                 for j in range(i, len(lines)):
    #                     if 'Device 1' in lines[j] and 'is up' in lines[j]:
    #                         return j
    #     self.summarylog.write('Devices were not up\n')
    #     self.assertTrue(False, msg='Devices are not up')

    def evaluate(self, lines, index):
        result = True
        vallist = self.initvalues()
        avgcounter = 0
        firstvalueskip = True
        firstminmax = True
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
                    vallist = self.adjustvalues(vallist, tx1value, None, firstminmax)
                    firstminmax = False
                    avgcounter += 1
                else:
                    try:
                        tx2value = float(lines[i + 1].split()[3])
                        self.checkvaluesarezero(tx1value, tx2value)
                        vallist = self.adjustvalues(vallist, tx1value, tx2value, firstminmax)
                        firstminmax = False
                        avgcounter += 1
                    except IndexError:
                        continue

        vallist[self.valueindex['tx1avg']] /= avgcounter
        self.summarylog.write('DEVICE 1 TX values:\nMAX: ' + str(vallist[self.valueindex['tx1max']]) + '\nMIN: ' + str(
            vallist[self.valueindex['tx1min']]) + '\nAVG: ' + str(vallist[self.valueindex['tx1avg']]) + '\n')
        if len(self.devicelist) == 2:
            vallist[self.valueindex['tx2avg']] /= avgcounter
            self.summarylog.write(
                'DEVICE 2 TX values:\nMAX' + str(vallist[self.valueindex['tx2max']]) + '\nMIN: ' + str(
                    vallist[self.valueindex['tx2min']]) + '\nAVG: ' + str(vallist[self.valueindex['tx2avg']]) + '\n')

        self.assertTrue(result, msg='Something went wrong')


class TestQualityOfService(TerminatingTest):
    logname = 'qualityofservicelog'
    casename = 'Quality of Service'

    def executetest(self):
        return subprocess.Popen(['./build/MoonGen', './examples/quality-of-service-test.lua', '0', '1'],
                                stdout=self.testlog, cwd=self.path)

    def adjustvalues(self, vallist, value, firstrun):
        if value > vallist[0]:
            vallist[0] = value
            if firstrun:
                vallist[2] = value
        if value < vallist[2]:
            vallist[2] = value

        vallist[1] += value
        vallist[3] += 1

        return vallist

    def getavg(self, vallist):
        if vallist[1] == 0.0:
            return str(0.0)
        return str(vallist[1] / vallist[3])

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
        firstminmax = [True, True, True, True]

        firstportline = lines[index + 1].split()
        firstport = firstportline[len(firstportline) - 1]

        firstport = self.extractport(firstport)
        self.summarylog.write("value of firstport is: " + firstport + '\n')
        secondportline = lines[index + 2].split()
        secondport = secondportline[len(secondportline) - 1]
        secondport = self.extractport(secondport)

        firstporttxvalues = [0.0, 0.0, 0.0, 0]
        firstportrxvalues = [0.0, 0.0, 0.0, 0]
        secondporttxvalues = [0.0, 0.0, 0.0, 0]
        secondportrxvalues = [0.0, 0.0, 0.0, 0]

        for i in range(index, len(lines)):

            self.checkalerts(lines, i)
            if '[Port' in lines[i]:
                value = float(lines[i].split()[3])
                if str(firstport) in lines[i]:
                    if 'TX' in lines[i]:
                        firstporttxvalues = self.adjustvalues(firstporttxvalues, value, firstminmax[0])
                        firstminmax[0] = False
                    elif 'RX' in lines[i]:
                        firstportrxvalues = self.adjustvalues(firstportrxvalues, value, firstminmax[1])
                        firstminmax[1] = False
                elif secondport in lines[i]:
                    if 'TX' in lines[i]:
                        secondporttxvalues = self.adjustvalues(secondporttxvalues, value, firstminmax[2])
                        firstminmax[2] = False
                    elif 'RX' in lines[i]:
                        secondportrxvalues = self.adjustvalues(secondportrxvalues, value, firstminmax[3])
                        firstminmax[3] = False

        self.summarylog.write(
            'FIRST PORT: ' + firstport + '\nTX Values:\nMAX: ' + str(firstporttxvalues[0]) + '\nAVG: ' + self.getavg(
                firstporttxvalues)
            + '\nMIN: ' + str(firstporttxvalues[2]) +
            '\nRX Values:\nMAX: ' + str(firstportrxvalues[0]) + '\nAVG: ' + self.getavg(
                firstportrxvalues) + '\nMIN: ' + str(firstportrxvalues[2]) +
            '\nSECOND PORT: ' + secondport + '\nTX Values:\nMAX: ' + str(secondporttxvalues[0]) + '\nAVG: ' +
            self.getavg(secondportrxvalues) + '\nMIN: ' + str(secondporttxvalues[2]) +
            '\nRX Values:\nMAX: ' + str(secondportrxvalues[0]) + '\nAVG: ' + self.getavg(
                secondportrxvalues) + '\nMIN: ' +
            str(secondportrxvalues[2])
        )
        result = result and firstportrxvalues[0] != 0 and firstportrxvalues[
            0] != 0 and secondporttxvalues != 0 and secondportrxvalues != 0
        self.assertTrue(result, 'Some values were 0z')  # tmp


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
        values = DisplayValue('Nano Seconds')
        for i in range(index, len(lines)):
            self.checkalerts(lines, i)
            if lines[i][0] == '-':
                if ignorefirst:
                    ignorefirst = False
                    continue
                value = self.getvalue(lines[i])
                values.aggregate(value)

            self.summarylog.write('Clock difference values are: ' + values.tostring())
            self.assertTrue(True)


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
                self.summarylog.write('Error in: ' + out + ':\n' + lines[index])

        msg = 'Timestamping conducted %d tests, %d errors came up\n' % (testquant, errorcounter)
        print msg
        self.summarylog.write(msg)
        result = testquant - errorcounter > self.reqpasses
        self.summarylog.write('Verdict: Have the passed tests surpassed ' + str(self.reqpasses) + ': ' + str(result))
        self.assertTrue(result,
                        msg='Selected devices have passed less than %d tests in Test Timestamping Capabilities'
                            % self.reqpasses)
