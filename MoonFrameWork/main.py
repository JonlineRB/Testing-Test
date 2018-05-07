# import unittest
import subprocess

print ("Testing MoonGen Simple Case: udp-simple")

# outFile = open('result', 'w')

# p = subprocess.Popen(['/home/borowski/Moongen/moongen-simple', 'start',
#                       'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'], stdout=outFile)


# p = subprocess.Popen(
#     ['./../../../MoonGen/moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'],
#     stdout=outFile)

try:
    p = subprocess.check_output(['./../../../MoonGen/moongen-simple', 'start', 'udp-simple:0:1:rate=1000mbit/s,ratePattern=poisson'])
    print("=== No Errors===")
except subprocess.CalledProcessError as e:
    print(e)

# result = subprocess.Popen.wait(p)

if result == 0:
    print('==TestFramework: test terminated, everything works.')
else:
    print('==TestFramework: exit code %s: Something went wrong!' % result)
    # parse file

# outFile.close()
