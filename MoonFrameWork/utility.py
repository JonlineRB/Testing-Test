import subprocess


# utility class for the MoonGen Testing framework

def parsedevices(dpdkdevlist):
    print('Framework: Parsing DPDK bound devices')
    # call a subprocess for dpdk-devbind, store the relevant results in a file
    # create a file
    initialbinds = open('initialBindState', 'w')
    # start this process
    subprocess.Popen(
        ['./dpdk-devbind.py', '-s'], stdout=initialbinds, cwd='/home/borowski/MoonGen/libmoon/deps/dpdk/usertools'
    )
    # parse and store the results
    initialbinds.close()
    initialbinds = open('initialBindState', 'r')
    parsedlines = initialbinds.readlines()
    initialbinds.close()
    for x in parsedlines:
        if 'Network devices using DPDK-compatible driver' in x:
            dpdkindex = parsedlines.index(x) + 2
            # dpdkDevList = list()
            # get all devices in this category on a list
            while parsedlines[dpdkindex] != '\n':
                dpdkdevlist.append(parsedlines[dpdkindex])
                dpdkindex += 1
            break
    return dpdkdevlist


def unbinddevices(devicelist):
    for x in devicelist:
        current = x.split()[0]
        p = subprocess.Popen(
            ['./dpdk-devbind.py', '-u', current], cwd='/home/borowski/MoonGen/libmoon/deps/dpdk/usertools'
        )
        p.wait()
