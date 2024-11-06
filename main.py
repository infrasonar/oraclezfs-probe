from libprobe.probe import Probe
from lib.check.alerts import check_alerts
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'alerts': check_alerts
    }

    probe = Probe("oraclezfs", version, checks)
    probe.start()
