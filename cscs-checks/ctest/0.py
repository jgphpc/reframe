import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class Exit_Code_Test(rfm.RegressionTest):
    test = parameter(['returnT', 'returnF', 'return'])
    valid_systems = ['dom:login']
    valid_prog_environs = ['builtin']
    build_system = 'CMake'
    executable = 'ctest'
    # executable_opts = ['-R', f'{test}']
    # postrun_cmds = ['echo rc=$?']

    @run_before('compile')
    def set_cmake(self):
        self.build_system.cxx = 'g++'
        self.build_system.make_opts = ['all']
        self.executable_opts = ['-R', f'{self.test}']

    @sanity_function
    def assert_passed(self):
        return sn.assert_found(r'passed', self.stdout)

#     @sanity_function
#     def assert_passed(self):
#         regex = r'rc=(\d+)'
#         rc = sn.extractsingle(regex, self.stdout, 1)
#         failure_msg = f'ctest failed with rc={rc}'
#         return sn.assert_eq(rc, '0', failure_msg)