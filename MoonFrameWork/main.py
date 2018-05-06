from subprocess import call

print ("Testing MoonGen Simple")


# go to MoonGen repo and execute a simple flow

def callsimple1():
    # moonGenPath = "~/MoonGen/"
    # simpleFlow = "moongen-simple start load-latency:0:1:rate=10Mp/s,time=3m"
    call("./../../../MoonGen/moongen-simple start load-latency:0:1:rate=10Mp/s,time=3m",shell=True)

def callsimplelocal():
    call("moongen-simple start load-latency:0:1:rate=10Mp/s,time=3m",shell=True)

def echotest():
    call("echo TEST",shell=True)


callsimplelocal()
