import os
import subprocess


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


def binddevices(devicelist):
    if not devicelist:
        return
    for x in devicelist:
        p = subprocess.Popen(
            ['./dpdk-devbind.py', '--bind=igb_uio', x.split()[0]], cwd='/home/borowski/MoonGen/libmoon/deps/dpdk/usertools'
        )
        p.wait()
        print('bound device: ' + x.split()[0])
