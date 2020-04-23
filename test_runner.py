# from scripts.test_util import run_command
from test_cli import TestModule

import argparse
import random
import socket
import string
import subprocess
import sys


class TestRunner(object):
    _CODALAB_SERVICE_EXECUTABLE = 'codalab_service.py'
    _TEST_INSTANCE_NEEDED_TESTS = ['all', 'default', 'copy']

    @staticmethod
    def _docker_exec(command):
        return 'docker exec -it codalab_rest-server_1 /bin/bash -c "{}"'.format(command)

    @staticmethod
    def _create_temp_instance(name):
        print('Creating another CodaLab instance for testing...')

        def get_free_ports(num_ports):
            socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(num_ports)]
            for s in socks:
                # When binding a socket to port 0, the kernel will assign it a free port
                s.bind(('', 0))
            ports = [str(s.getsockname()[1]) for s in socks]
            for s in socks:
                s.listen(5)
            return ports

        def next_free_port(port=1024, max_port=65535):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while port <= max_port:
                try:
                    sock.bind(('', port))
                    result = sock.connect_ex(('', port))
                    if result == 0:
                        print('Tony Found a port: ' + str(port))
                        sock.listen(5)
                        print('Tony returning port: ' + str(port))
                        return port
                    else:
                        print('Tony Non-zero result for port: ' + str(port))
                        sock.close()
                        port += 1
                except OSError:
                    port += 1
            raise IOError('no free ports')

        rest_port, http_port, mysql_port = get_free_ports(3)
        # rest_port = 2900  # default is 2900
        # rest_port = next_free_port()
        # http_port = portpicker.pick_unused_port('0.0.0.0')

        mysql_port = 3306  # Hardcoded for now

        # TODO: delete -tony
        print(
            '1. Tony rest_port: {}, http_port: {}, mysql_port: {}'.format(
                rest_port, http_port, mysql_port
            )
        )
        instance = 'http://rest-server:%s' % rest_port
        try:
            subprocess.check_call(
                ' '.join(
                    [
                        'python3',
                        TestRunner._CODALAB_SERVICE_EXECUTABLE,
                        'start',
                        '--instance-name %s' % name,
                        '--rest-port %s' % rest_port,
                        '--http-port %s' % http_port,
                        '--mysql-port %s' % mysql_port,
                        '--version %s' % version,
                        '--services default',
                        # '--services rest-server',
                    ]
                ),
                shell=True,
            )
        except subprocess.CalledProcessError as ex:
            print('Temp instance exception: %s' % ex.output)
            raise

        return instance

    def __init__(self, instance, tests):
        self.instance = instance
        self.tests = tests

        # Check if a second, temporary instance of CodaLab is needed for testing
        self.temp_instance_required = any(
            test in tests for test in TestRunner._TEST_INSTANCE_NEEDED_TESTS
        )
        if self.temp_instance_required:
            self.temp_instance_name = 'temp-instance%s' % ''.join(
                random.choice(string.digits) for _ in range(8)
            )
            self.temp_instance = TestRunner._create_temp_instance(self.temp_instance_name)

    def run(self):
        try:
            test_command = 'python3 test_cli.py --instance {} --second-instance {} {} '.format(
                self.instance, self.temp_instance, ' '.join(self.tests)
            )
            if self.temp_instance_required:
                test_command += '--second-instance %s ' % self.temp_instance

            test_command += ' '.join(self.tests)
            # TODO: remove -tony
            print('Tony: test command - ' + test_command)
            subprocess.check_call(TestRunner._docker_exec(test_command), shell=True)
        except subprocess.CalledProcessError as ex:
            print('Exception while executing tests: %s' % ex.output)
            raise

        self._cleanup()

    def _cleanup(self):
        if not self.temp_instance_required:
            return

        print('Shutting down the temp instance {}...'.format(self.temp_instance_name))
        subprocess.check_call(
            ' '.join(
                [
                    'python3',
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
        default='latest',
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
    version = args.version
    test_runner = TestRunner(args.instance, args.tests)
    if not test_runner.run():
        sys.exit(1)
