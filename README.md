Testing-Test

This is the Test Framework of MoonGen.

It features many implemented tests for already existing MoonGen functionality.
If you wish to execute all tests, please run the main python script. It parses the FrameworkConfig.cfg for cases and devices to be tested.
You may edit the FrameworkConfig.cfg file in order to customize your testing process.
If you only wish to execute a few tests, you may bypass the config file with the -t option, followed by these arguments: <tests.TestName> <PCIe ID DUT1> <PCIe ID DUT2 if needed>

Test .lua scripts with tests.TestFiles - It will look for all scripts within the specified directory in the configuration file and execute them. Success will depend on their return code.

In the Meta section of the configuration file, specify the directory containing the files-to-be-tested like this:

testdir: test/tests/

Here is an example for the complete Meta section:

[Meta]
path: /home/borowski/MoonGen/
testdir: test/tests/
device1: 0000:02:00.0
device2: 0000:02:00.1

Devices declared in this section will be used as default devices. Unless specified otherwise, these devices are associated with tests mentioned in other sections of the config file.


In order to expand the framework's functionallity, new classes may be introduced into the tests.py script. Please take the class hierarchy into account, it might save a lot of effort regarding common functionality among tests.