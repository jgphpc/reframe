import os
import reframe as rfm
import reframe.utility.sanity as sn


class TestBase(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_systems = ['dom:mc']
        self.valid_prog_environs = ['*']
        self.num_tasks = 1
        self.time_limit = '1m'
        self.executable = f"echo 1 mpi={self.mpi_task} step={self.step}"
        self.sanity_patterns = sn.all([sn.assert_found('1', self.stdout)])


steps = [1]
mpi_tasks = [12]
@rfm.parameterized_test(*[[step, mpi_task]
                          for step in steps
                          for mpi_task in mpi_tasks
                          ])
class MPI_ComputeTest(TestBase):
    def __init__(self, step, mpi_task):
        # share args witht self for TestBase class
        self.step = step
        self.mpi_task = mpi_task
        super().__init__()
        # super().__init__(step)
        self.name = f'compute_{mpi_task}mpi_{step}steps'


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
        self.testnames = [f'compute_{mp}mpi_{step}steps' for step in steps for mp in mpi_tasks]
        for test in self.testnames:
            self.depends_on(test)

    @rfm.require_deps
    def collect_logs(self):
        for test_index in range(len(self.testnames)):
            stagedir = self.getdep(self.testnames[test_index]).stagedir
            job_out = '*_job.out'
            postrun_cmd = f'cp {stagedir}/{job_out} .'
            # postrun_cmd = 'cp %s/%s .' % (stagedir, job_out)
            self.postrun_cmds.append(postrun_cmd)

    @rfm.require_deps
    def process_logs(self):
        job_out = 'job.out'
        for testnames in self.testnames:
            rpt = os.path.join(self.stagedir, f'rfm_{testnames}_{job_out}')
            # self.postrun_cmds.append(f'ls rfm_{testnames}_{job_out}')
            regex = r'mpi=(?P<nmpi>\d+)'
            self.res = sn.extractsingle(regex, rpt, 'nmpi', int)
        self.perf_patterns = {
            'n': self.res,
        }
        self.reference = {
            '*': {
                'n': (0, None, None, ''),
                }
        }
