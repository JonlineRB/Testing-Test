Testing-Test

This is the Test Framework of MoonGen.

It features many implemented tests for already existing MoonGen functionality.
If you wish to execute all tests, please run the main python script. It parses the FrameworkConfig.cfg for cases and devices to be tested.
You may edit the FrameworkConfig.cfg file in order to customize your testing process.
If you only wish to execute a few tests, you may bypass the config file with the -t option, followed by these arguments: <tests.TestName> <PCIe ID DUT1> <PCIe ID DUT2 if needed>
