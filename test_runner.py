# from scripts.test_util import run_command
from codalab_service import clean_version, get_default_version
from test_cli import TestModule

import argparse
import random
import string
import subprocess
import sys


class TestRunner(object):
    _CODALAB_SERVICE_EXECUTABLE = './codalab_service.py'

    @staticmethod
    def _create_temp_instance(name):
        print('Creating another CodaLab instance for testing...')

        def get_free_ports(num_ports):
            import socket

            socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(num_ports)]
            for s in socks:
                s.bind(("", 0))
            ports = [str(s.getsockname()[1]) for s in socks]
            for s in socks:
                s.close()
            return ports

        rest_port, http_port, mysql_port = get_free_ports(3)
        # TODO: delete -tony
        print(
            '1. Tony rest_port: {}, http_port: {}, mysql_port: {}'.format(
                rest_port, http_port, mysql_port
            )
        )
        # mysql_port = 3306  # Hardcoded for now
        instance = 'http://localhost:%s' % rest_port
        try:
            subprocess.check_output(
                ' '.join(
                    [
                        TestRunner._CODALAB_SERVICE_EXECUTABLE,
                        'start',
                        '--instance-name %s' % name,
                        '--rest-port %s' % rest_port,
                        '--http-port %s' % http_port,
                        '--mysql-port %s' % mysql_port,
                        '--version %s' % version,
                    ]
                ),
                shell=True,
            )
        except subprocess.CalledProcessError as ex:
            print('Temp instance exception: %s' % ex.output)
            raise

        # Wait for the temp instance to be up
        TestRunner.wait_for_service(instance, 'echo temp instance {} is up...'.format(instance))
        return instance

    @staticmethod
    def wait_for_service(instance, cmd):
        return '/opt/wait-for-it.sh {} -- {}'.format(instance, cmd)

    def __init__(self, instance, tests):
        self.instance = instance
        self.temp_instance_name = 'temp-instance%s' % ''.join(
            random.choice(string.digits) for _ in range(8)
        )
        self.temp_instance = TestRunner._create_temp_instance(self.temp_instance_name)
        self.tests = tests

    def run(self):
        print('Running tests on version {}...'.format(version))
        # TODO: remove -tony
        # print(
        #     'python3 test_cli.py --instance {} --second-instance {} {}'.format(
        #         self.instance, self.temp_instance, ' '.join(self.tests)
        #     )
        # )
        # subprocess.check_call(
        #     TestRunner.wait_for_service(
        #         self.instance,
        #         'python3 test_cli.py --instance {} --second-instance {} {}'.format(
        #             self.instance, self.temp_instance, ' '.join(self.tests)
        #         ),
        #     ),
        #     shell=True,
        # )
        print(
            '3. Tony '
            + ' '.join(
                [
                    TestRunner._CODALAB_SERVICE_EXECUTABLE,
                    'test',
                    '--version %s' % version,
                    '--second-instance %s' % self.temp_instance,
                    ' '.join(self.tests),
                ]
            )
        )

        try:
            # subprocess.check_output(
            #     ' '.join(
            #         [
            #             TestRunner._CODALAB_SERVICE_EXECUTABLE,
            #             'test',
            #             '--version %s' % version,
            #             '--second-instance %s' % self.temp_instance,
            #             ' '.join(self.tests),
            #         ]
            #     ),
            #     shell=True,
            # )
            subprocess.check_output(
                'python3 test_cli.py --instance {} --second-instance {} {}'.format(
                    self.instance, self.temp_instance, ' '.join(self.tests)
                ),
                shell=True,
            )
        except subprocess.CalledProcessError as ex:
            print('Exception while executing tests: %s' % ex.output)
            raise

        # TODO: Tony here
        sys.exit(0)
        # subprocess.check_call(
        #     'python3 test_cli.py --instance {} --second-instance {} {}'.format(
        #         self.instance, self.temp_instance, ' '.join(self.tests)
        #     ),
        #     shell=True,
        # )
        self._cleanup()

    def _cleanup(self):
        print('Shutting down the temp instance {}...'.format(self.temp_instance_name))
        subprocess.check_output(
            ' '.join(
                [
                    TestRunner._CODALAB_SERVICE_EXECUTABLE,
                    'stop',
                    '--instance-name %s' % self.temp_instance_name,
                ]
            ),
            shell=True,
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Runs the specified tests against the specified CodaLab instance (defaults to localhost)'
    )
    parser.add_argument(
        '--cl-executable',
        type=str,
        help='Path to CodaLab CLI executable, defaults to "cl"',
        default='cl',
    )
    parser.add_argument(
        '--version',
        type=str,
        help='CodaLab version to use for multi-instance tests, defaults to "latest"',
        default=get_default_version(),
    )
    parser.add_argument(
        '--instance',
        type=str,
        help='CodaLab instance to run tests against, defaults to "http://rest-server:2900"',
        default='http://rest-server:2900',
    )
    parser.add_argument(
        'tests',
        metavar='TEST',
        nargs='+',
        type=str,
        choices=list(TestModule.modules.keys()) + ['all', 'default'],
        help='Tests to run from: {%(choices)s}',
    )

    args = parser.parse_args()
    cl = args.cl_executable
    version = clean_version(args.version)
    test_runner = TestRunner(args.instance, args.tests)
    if not test_runner.run():
        sys.exit(1)
