import sys
import argparse
from utils.test_qemu import TestRunner, TestStatus, load_testcases
from utils.log import Logger

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--arch", choices=["x86_64", "riscv64", "aarch64"], default="x86_64", help="target architecture")
parser.add_argument("-f", "--fast", action="store_true", help="do not test known failed and timeout testcases")
parser.add_argument("-t", "--test", help="run only one test")
parser.add_argument("-b", "--board", choices=["qemu"], default="qemu", help="board")
args = parser.parse_args()

TEST_DIR = "testcases/linux_libc_test"
TEST_NAME = "%s_%s" % (args.arch, args.board)
TEST_FILE = "%s/%s.txt" % (TEST_DIR, TEST_NAME)
LOG_OUTPUT = "linux_libc_test_%s.log" % TEST_NAME

TIMEOUT = 10
FAILED_PATTERN = ["failed","ERROR","Error","panicked","Hangup","Unknown signal"]

class LinuxTestRunner(TestRunner):
    BASE_CMD = "make -C ../zCore MODE=release LINUX=1 TEST=1 ARCH=%s" % args.arch

    def build_cmdline(self) -> str:
        return self.BASE_CMD

    def run_cmdline(self) -> str:
        return self.BASE_CMD + " justrun"

    def check_output(self, output: str) -> TestStatus:
        for pattern in FAILED_PATTERN:
            if pattern in output:
                return TestStatus.FAILED
        return TestStatus.OK

if __name__=='__main__':
    runner = LinuxTestRunner()
    runner.build()
    runner.run_qemu()

    if args.test:
        res = runner.run_one(args.test, args.fast, TIMEOUT)
        ok = res == TestStatus.OK
    else:
        runner.set_logger(Logger(LOG_OUTPUT))
        testcases = load_testcases(TEST_FILE)
        ok = runner.run_all(testcases, args.fast, TIMEOUT)

    runner.stop_qemu()
    if not ok:
        sys.exit(-1)
    else:
        sys.exit(0)
