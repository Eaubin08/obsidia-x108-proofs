# GNSS-SDR Blocked Report

Date: 2026-08-02
Status: BLOCKED_GNSS_SDR_RUNTIME

## Objective

Process a real public I/Q GNSS recording with GNSS-SDR:

```text
I/Q file -> GNSS-SDR -> acquisition/tracking -> observables/PVT -> Physical Reality Gate -> DomainState -> P3-05 -> X-108 -> receipt
```

## Official I/Q Source Attempted

- Official GNSS-SDR tutorial: `https://gnss-sdr.org/my-first-fix/`
- Public I/Q file URL: `https://sourceforge.net/projects/gnss-sdr/files/data/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.tar.gz/download`
- File identified by HTTP HEAD: `2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.tar.gz`
- Content type: `application/x-gzip`
- Content length observed by HTTP HEAD: `1150716878` bytes
- SourceForge final mirror observed: `https://unlimited.dl.sourceforge.net/project/gnss-sdr/data/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.tar.gz`

## Commands Executed

```powershell
gnss-sdr --version
docker --version
docker run --rm carlesfernandez/docker-gnsssdr gnss-sdr --version
Invoke-WebRequest -Uri 'https://sourceforge.net/projects/gnss-sdr/files/data/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.tar.gz/download' -Method Head
curl.exe -I -L https://sourceforge.net/projects/gnss-sdr/files/data/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.tar.gz/download
```

## Exact Errors

Local GNSS-SDR:

```text
gnss-sdr : Le terme «gnss-sdr» n'est pas reconnu comme nom d'applet de commande, fonction, fichier de script ou programme exécutable.
```

Docker CLI:

```text
Docker version 29.4.3, build 055a478
WARNING: Error loading config file: open C:\Users\User\.docker\config.json: Access is denied.
```

Docker GNSS-SDR image execution:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

PowerShell HEAD request:

```text
Invoke-WebRequest : La référence d'objet n'est pas définie à une instance d'un objet.
```

`curl.exe -I -L` succeeded and confirmed the real I/Q file exists, but the file was not downloaded because GNSS-SDR execution is blocked and the archive is about 1.07 GiB.

## Result

- No GNSS-SDR version available locally.
- Docker daemon is not running or not reachable.
- No acquisition/tracking/PVT logs were produced.
- No `RECORDED_REAL_RF` claim is allowed.

## Required Action

Start Docker Desktop Linux engine or install GNSS-SDR in an isolated environment, then download and process the official CTTC sample.

