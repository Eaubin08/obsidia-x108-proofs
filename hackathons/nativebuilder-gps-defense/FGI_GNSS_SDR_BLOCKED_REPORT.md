# FGI GNSS-SDR Blocked Report

Date: 2026-08-03
Status: `GNSS_SDR_BLOCKED_WITH_REAL_FGI_HOSTILE_RF`

## Real Dataset Present

- Dataset: FGI-SpoofRepo / FGI-JSDR.
- URL: `https://etsin.fairdata.fi/dataset/367379a8-7d78-4b08-91f0-8027ce7a621b`
- DOI: `10.23729/7a648509-2ca8-4a7d-8223-0b429182f857`
- License: `CC-BY-4.0`
- Scenario scope: `/FGISpoofRepo/UT_DFMC`
- Package SHA-256: `1df410917bc853b5ab843667acd47ede4e03bf237ce3e399d791a597ce9713ad`
- L1/E1 SHA-256: `e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72`

## Commands Attempted

```powershell
docker --config .local\docker-config info --format '{{.ServerVersion}}'
```

Result:

```text
permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine
```

```powershell
wsl.exe --status
wsl.exe -l -v
```

Result:

```text
Wsl/EnumerateDistros/Service/E_ACCESSDENIED
```

```powershell
where.exe gnss-sdr
choco search gnss-sdr --limit-output
```

Result:

```text
gnss-sdr not found; no Chocolatey package result returned.
```

## Required Human Action

One of these must be made available before `RECORDED_RF_ATTACK` can be attempted:

- Docker Desktop daemon access for this Windows user, including access to `npipe:////./pipe/docker_engine`.
- A WSL2 distro where GNSS-SDR can be installed and run.
- A local GNSS-SDR executable on Windows.
- The official FGI receiver toolchain executable in a usable local runtime.

No RF emission is needed. This is offline file processing only.
