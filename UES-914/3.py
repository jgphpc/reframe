import os
import sys
import subprocess
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                'common')))  # noqa: E402
import sphexa.sanity as sphs


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
class MPI_Compute_Test(TestBase):
    def __init__(self, step, mpi_task):
        # share args witht self for TestBase class
        self.step = step
        self.mpi_task = mpi_task
        super().__init__()
        # super().__init__(step)
        self.name = f'compute_{mpi_task}mpi_{step}steps'


@rfm.parameterized_test(*[[step, mpi_task]
                          for step in steps
                          for mpi_task in mpi_tasks
                          ])
class MPI_Compute_Singularity_Test(TestBase):
    def __init__(self, step, mpi_task):
        # share args witht self for TestBase class
        self.step = step
        self.mpi_task = mpi_task
        super().__init__()
        # super().__init__(step)
        self.name = f'compute_singularity_{mpi_task}mpi_{step}steps'


@rfm.simple_test
class MPI_CollectLogsTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_systems = ['dom:mc']
        self.valid_prog_environs = ['*']
        self.sourcesdir = None
        # self.modules = ['termgraph/0.3.1-python3']
        self.num_tasks_per_node = 1
        self.num_tasks = 1
        self.executable = 'echo 0'
        self.sanity_patterns = sn.assert_found(r'^\d+', self.stdout)
        # construct list of dependencies:
        self.testnames_native = [f'compute_{mpi_task}mpi_{step}steps' for step in steps for mpi_task in mpi_tasks]
        for test in self.testnames_native:
            self.depends_on(test)
        self.testnames_singularity = [f'compute_singularity_{mpi_task}mpi_{step}steps' for step in steps for mpi_task in mpi_tasks]
        for test in self.testnames_singularity:
            self.depends_on(test)

    @rfm.require_deps
    def collect_logs(self):
        job_out = '*_job.out'
        # bare metal test logs:
        for test_index in range(len(self.testnames_native)):
            stagedir = self.getdep(self.testnames_native[test_index]).stagedir
            #ok postrun_cmd = f'cp {stagedir}/{job_out} .'
            #ok self.postrun_cmds.append(postrun_cmd)
            self.postrun_cmds.append('cp /apps/common/UES/sandbox/jgp/hpctools.git/reframechecks/notool/UES-863/native/sphexa_timers_sqpatch_384mpi_001omp_250n_10steps/rfm_sphexa_timers_sqpatch_384mpi_001omp_250n_10steps_job.out rfm_compute_12mpi_1steps_job.out')
        # singularity test logs:
        for test_index in range(len(self.testnames_singularity)):
            stagedir = self.getdep(self.testnames_singularity[test_index]).stagedir
            self.postrun_cmds.append('cp /apps/common/UES/sandbox/jgp/hpctools.git/reframechecks/notool/UES-863/native/sphexa_timers_sqpatch_384mpi_001omp_250n_10steps/rfm_sphexa_timers_sqpatch_384mpi_001omp_250n_10steps_job.out rfm_compute_singularity_12mpi_1steps_job.out')

# {{{
#     @rfm.require_deps
#     def process_logs(self):
#         job_out = 'job.out'
#         for testnames in self.testnames:
#             rpt = os.path.join(self.stagedir, f'rfm_{testnames}_{job_out}')
#             # self.postrun_cmds.append(f'ls rfm_{testnames}_{job_out}')
#             # regex = r'mpi=(?P<nmpi>\d+)'
#             regex = r'starttime=(?P<nmpi>\d+)'
#             self.res = sn.extractsingle(regex, rpt, 'nmpi', int)
#             # fjg=open('xx.rpt', "a")
#             # fjg.write('xx={}'.format(sn.evaluate(self.res)))
#             # fjg.write(f'xx={self.res}')
#             # fjg.close()
#         self.perf_patterns = {
#             'n': self.res,
#         }
#         self.reference = {
#             '*': {
#                 'n': (0, None, None, ''),
#                 }
#         }
# }}}

    # @rfm.run_before('performance')
    @rfm.run_after('run')
    def extract_data(self):
    # def compare_native_vs_containers_elapsed_time(self):
        fjg=open(os.path.join(self.stagedir, 'timings.rpt'), "w")
        # termgraph header:
        fjg.write('# Elapsed_time (seconds) = f(mpi_tasks)\n')
        fjg.write('@ mpi,native,singularity\n')
        job_out = 'job.out'
        # TODO: reuse self.testnames_native here
        for step in steps:
            for mpi_task in mpi_tasks:
                # native:
                testname = f'compute_{mpi_task}mpi_{step}steps'
                self.rpt = os.path.join(self.stagedir, f'rfm_{testname}_{job_out}')
                res_native = sn.evaluate(sphs.elapsed_time_from_date(self))
                # singularity:
                testname = f'compute_singularity_{mpi_task}mpi_{step}steps'
                self.rpt = os.path.join(self.stagedir, f'rfm_{testname}_{job_out}')
                res_singularity = sn.evaluate(sphs.elapsed_time_from_date(self))
                # termgraph data:
                fjg.write(f'{mpi_task},{res_native},{res_singularity}\n')
        fjg.close()
        # rpt = os.path.join(self.stagedir, 'timings.rpt')
        # tgraph = os.path.join(self.stagedir, 'scripts', 'termgraph_cscs.py')
        # ignored:
        # self.postrun_cmds = [f'echo "{tgraph} --stacked {rpt}"']
        # self.postrun_cmds.append('echo xxxxxxx')

#0    @rfm.run_after('run')
#0    def plot_logs(self):
#0        rpt = os.path.join(self.stagedir, 'timings.rpt')
#0        tgraph = os.path.join(self.stagedir, 'scripts', 'termgraph_cscs.py')
#0        self.postrun_cmds.append('echo xxxx')
#0        # self.postrun_cmds = [f'echo "{tgraph} --stacked {rpt}"']

@rfm.simple_test
class MPI_PostprocTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_systems = ['dom:mc']
        self.valid_prog_environs = ['*']
        self.modules = ['termgraph/0.3.1-python3']
        self.depends_on('MPI_CollectLogsTest')
        self.executable = 'python3.7'
        # rpt = os.path.join(self.stagedir, 'timings.rpt')
        # tgraph = os.path.join(self.stagedir, 'scripts', 'termgraph_cscs.py')
        # self.postrun_cmds = [f'echo {tgraph} {rpt}']
        self.sanity_patterns = sn.assert_not_found(r'ordinal not in range', self.stderr)

    @rfm.require_deps
    def plot_logs(self):
        stagedir = self.getdep('MPI_CollectLogsTest').stagedir
        rpt = os.path.join(stagedir, 'timings.rpt')
        tgraph = os.path.join(self.stagedir, 'scripts', 'termgraph_cscs.py')
        self.executable_opts = [f'{tgraph}', f'{rpt}']
        # self.executable_opts = [f'{tgraph}', '--stacked', f'{rpt}']
        # self.postrun_cmds = [f'echo "{tgraph} --stacked {rpt}"']


## 'MPI_CollectLogsTest' 
#     @rfm.run_before('run')
#     def plot_native_vs_containers_elapsed_time(self):
#         rpt = os.path.join(self.stagedir, 'timings.rpt')
#         tgraph = os.path.join(self.stagedir, 'scripts', 'termgraph_cscs.py')
#         #os.system(f'echo "python3.7 {tgraph} --stacked {rpt}"')
#         #exec(open("test2.py").read())
#         python3_cmd = f'/opt/python/3.7.3.2/bin/python3 {tgraph} --stacked {rpt}'
#         process = subprocess.Popen(python3_cmd.split(), stdout=subprocess.PIPE)
#         output, error = process.communicate()
#         # python3 ./termgraph_cscs.py --stacked $outputf && cat $output_rpt
