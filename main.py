from libprobe.probe import Probe
from lib.check.alerts import CheckAlerts
from lib.check.cpu import CheckCpu
from lib.check.disks import CheckDisks
from lib.check.hardware import CheckHardware
from lib.check.io import CheckIo
from lib.check.memory import CheckMemory
from lib.check.network import CheckNetwork
from lib.check.problems import CheckProblems
from lib.check.storage import CheckStorage
from lib.check.system import CheckSystem

from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckAlerts,
        CheckDisks,
        CheckHardware,
        CheckMemory,
        CheckNetwork,
        CheckProblems,
        CheckStorage,
        CheckSystem,

        # Analytics checks
        CheckCpu,
        CheckIo,
    )

    probe = Probe("oraclezfs", version, checks)
    probe.start()
