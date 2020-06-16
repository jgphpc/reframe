import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ExampleRunLoggingTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = ('RunOnlyRegressionTest')
        self.valid_systems = ['dom:login']
        self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu']
        self.sourcesdir = None
        self.executable = 'echo 9'
        self.sanity_patterns = sn.all([sn.assert_found('9', self.stdout)])
        regex = r'(?P<nn>\d)'
        self.elapsed = sn.extractsingle(regex, self.stdout, 'nn', int)
        self.perf_patterns = {'Elapsed': self.elapsed}
        self.reference = {'*': {'Elapsed': (0, None, None, 's')}}
