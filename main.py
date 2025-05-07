from libprobe.probe import Probe
from lib.check.alerts import check_alerts
from lib.check.cpu import check_cpu
from lib.check.disks import check_disks
from lib.check.hardware import check_hardware
from lib.check.io import check_io
from lib.check.memory import check_memory
from lib.check.network import check_network
from lib.check.problems import check_problems
from lib.check.storage import check_storage
from lib.check.system import check_system

from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'alerts': check_alerts,
        'disks': check_disks,
        'hardware': check_hardware,
        'memory': check_memory,
        'network': check_network,
        'problems': check_problems,
        'storage': check_storage,
        'system': check_system,

        # Analytics checks
        'cpu': check_cpu,
        'io': check_io,
    }

    probe = Probe("oraclezfs", version, checks)
    probe.start()
