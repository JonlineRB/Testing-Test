import subprocess


# this file should have all of the functionality of the subprocess module


class SubHandler(object):
    moonpath = ''

    def __init__(self, path):
        super(SubHandler, self).__init__()
        self.moonpath = path

    def popen(self, args, outfile):
        subprocess.Popen(args, cwd=self.moonpath, stdout=outfile)
