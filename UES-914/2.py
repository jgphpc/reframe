import os
import reframe as rfm
import reframe.utility.sanity as sn


class TestBase(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_systems = ['dom:mc']
        self.valid_prog_environs = ['*']
        # self.num_tasks = 1
        self.time_limit = '1m'
        self.executable = f"echo 1 mpi={self.mpi_task} step={self.step}"
        # self.executable = 'echo 1 mpi=%s step=%s' % self.step
        self.sanity_patterns = sn.all([sn.assert_found('1', self.stdout)])


steps = [1, 2]
mpi_tasks = [12, 24]
@rfm.parameterized_test(*[[step, mpi_task]
                          for step in steps
                          for mpi_task in mpi_tasks
                          ])
class MPI_ComputeTest(TestBase):
    def __init__(self, step, mpi_task):
        # super().__init__(step)
        # share args witht self for TestBase class
        self.step = step
        self.mpi_task = mpi_task
        super().__init__()
        self.name = f'compute_{mpi_task}mpi_{step}steps'
        # self.name = 'compute_{}mpi_{}steps'.format(mpi_task, step)


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
        # self.testnames = [f'compute_{step}steps' for step in steps]
        self.testnames = [f'compute_{mp}mpi_{step}steps' for step in steps for mp in mpi_tasks]
        # ---
        #ok self.testnames = [[f'compute_{mp}mpi_{step}steps' for step in steps] for mp in mpi_tasks]
        #ok self.testnames = self.testnames[0] + self.testnames[1]
        # ---
        for test in self.testnames:
            self.depends_on(test)

    @rfm.require_deps
    def collect_logs(self):
        for test_index in range(len(self.testnames)):
            stagedir = self.getdep(self.testnames[test_index]).stagedir
            job_out = '*_job.out'
            postrun_cmd = 'echo "%s/%s"' % (stagedir, job_out)
            self.postrun_cmds.append(postrun_cmd)
            #also_ok: postrun_cmd = 'echo "../%s/*_job.out"' % self.testnames[test_index]
