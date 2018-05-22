import subprocess


# this file should have all of the functionality of the subprocess module


class SubHandler(object):
    moonpath = ''

    def __init__(self, path):
        super(SubHandler, self).__init__()
        self.moonpath = path

    def popen(self, args, outfile):
        return subprocess.Popen(args, cwd=self.moonpath, stdout=outfile)

    def wait(self, subproc):
        subproc.wait()

    def popenwait(self, args, outfile):
        p = self.popen(args, outfile)
        self.wait(p)
