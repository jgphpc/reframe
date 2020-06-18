import os
import reframe as rfm
import reframe.utility.sanity as sn


class TestBase(rfm.RunOnlyRegressionTest):
    def __init__(self, myarg1):
        self.valid_systems = ['dom:mc']
        self.valid_prog_environs = ['*']
        self.num_tasks = 1
        self.time_limit = '1m'
        self.executable = 'echo 1 step=%s' % myarg1
        self.sanity_patterns = sn.all([sn.assert_found('1', self.stdout)])


steps = [1, 2]
@rfm.parameterized_test(*[[step]
                          for step in steps
                          ])
class MPI_ComputeTest(TestBase):
    def __init__(self, step):
        super().__init__(step)


@rfm.simple_test
class MPI_PostprocTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_systems = ['dom:mc']
        self.valid_prog_environs = ['*']
        self.num_tasks_per_node = 1
        self.num_tasks = 1
        self.executable = 'echo 0'
        self.sanity_patterns = sn.assert_found(r'^\d+', self.stdout)
        # construct list of dependencies:
        testnames = [ f'MPI_ComputeTest_{step}' for step in steps]
        for test in testnames:
            self.depends_on(test)


    @rfm.require_deps
    def collect_logs(self, MPI_ComputeTest):
        mydirname = 'MPI_ComputeTest_*'
        self.postrun_cmds = ['ls ../%s/*job.out' % mydirname]
        # self.postrun_cmds = ['echo "%s"' % os.path.join(MPI_ComputeTest().stagedir)]
