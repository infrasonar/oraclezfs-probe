from libprobe.probe import Probe
from lib.check.zfs import check_zfs
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'zfs': check_zfs
    }

    probe = Probe("orablezfs", version, checks)

    probe.start()
