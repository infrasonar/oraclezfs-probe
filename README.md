[![CI](https://github.com/infrasonar/oraclezfs-probe/workflows/CI/badge.svg)](https://github.com/infrasonar/oraclezfs-probe/actions)
[![Release Version](https://img.shields.io/github/release/infrasonar/oraclezfs-probe)](https://github.com/infrasonar/oraclezfs-probe/releases)

# InfraSonar Oracle ZFS Storage Probe

## Environment variable

Variable            | Default                        | Description
------------------- | ------------------------------ | ------------
`AGENTCORE_HOST`    | `127.0.0.1`                    | Hostname or Ip address of the AgentCore.
`AGENTCORE_PORT`    | `8750`                         | AgentCore port to connect to.
`INFRASONAR_CONF`   | `/data/config/infrasonar.yaml` | File with probe and asset configuration like credentials.
`MAX_PACKAGE_SIZE`  | `500`                          | Maximum package size in kilobytes _(1..2000)_.
`MAX_CHECK_TIMEOUT` | `300`                          | Check time-out is 80% of the interval time with `MAX_CHECK_TIMEOUT` in seconds as absolute maximum.
`DRY_RUN`           | _none_                         | Do not run demonized, just return checks and assets specified in the given yaml _(see the [Dry run section](#dry-run) below)_.
`LOG_LEVEL`         | `warning`                      | Log level (`debug`, `info`, `warning`, `error` or `critical`).
`LOG_COLORIZED`     | `0`                            | Log using colors (`0`=disabled, `1`=enabled).
`LOG_FMT`           | `%y%m%d %H:%M:%S`              | Log format prefix.

## Docker build

```
docker build -t oraclezfs-probe . --no-cache
```

## Config

Example configuration:

```yaml
snmp:
  config:
    username: "my-user-name"
    password: "my-secret-password"
```

## Dry run

Available checks:
- `oraclezfs`

Create a yaml file, for example _(test.yaml)_:

```yaml
asset:
  name: "foo.local"
  check: "oraclezfs"
  config:
    address: "192.168.1.2"
    secure: True
    port: 215
    version: 'v2'
```

Run the probe with the `DRY_RUN` environment variable set the the yaml file above.

```
DRY_RUN=test.yaml python main.py
```