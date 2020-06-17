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

@rfm.parameterized_test(*[[steps]
                          for steps in [1]
                          ])
class MPI_ComputeTest(TestBase):
    def __init__(self, steps):
        super().__init__(steps)
        self.name = 'compute_{}steps'.format(steps)

@rfm.simple_test
class MPI_PostprocTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_systems = ['dom:mc']
        self.valid_prog_environs = ['*']
        self.num_tasks_per_node = 1
        self.num_tasks = 1
        self.executable = 'echo 0'
        # self.depends_on('ComputeTest_1')
        self.depends_on('compute_1steps')
        self.sanity_patterns = sn.assert_found(r'^\d+', self.stdout)

    @rfm.require_deps
    def collect_logs(self, MPI_ComputeTest):
        mydirname = 'MPI_ComputeTest_*'
        # self.postrun_cmds = ['echo "%s"' % os.path.join(MPI_ComputeTest().stagedir)]
        self.postrun_cmds = ['echo "%s"' % os.path.join(compute_1steps().stagedir)]
