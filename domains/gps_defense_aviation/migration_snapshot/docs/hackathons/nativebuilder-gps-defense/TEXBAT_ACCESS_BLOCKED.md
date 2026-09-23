# TEXBAT Access Blocked Report

Date: 2026-08-02
Status: BLOCKED_TEXBAT_RUNTIME

## Objective

Run a blind benchmark over an official TEXBAT scenario:

```text
TEXBAT .bin -> GNSS-SDR -> acquisition/tracking -> observables -> blind detection -> P3-05 -> X-108 -> receipt
```

## Official Source

- TEXBAT page: `https://radionavlab.ae.utexas.edu/texbat/`
- Public index observed: `https://rnl-data.ae.utexas.edu/datastore/texbat/`
- Example scenario attempted: `https://rnl-data.ae.utexas.edu/datastore/texbat/ds1.bin`
- Metadata attempted: `https://rnl-data.ae.utexas.edu/datastore/texbat/ds1.xml`, `https://rnl-data.ae.utexas.edu/datastore/texbat/ds1.md5`

## License / Conditions From Official Page

The University of Texas copyright notice allows use, copy, and modification for research purposes without license fees, requests users not to redistribute the data, and disclaims warranties.

## Commands Executed

```powershell
curl.exe -I https://rnl-data.ae.utexas.edu/datastore/texbat/ds1.bin
Invoke-WebRequest -Uri 'https://rnl-data.ae.utexas.edu/datastore/texbat/ds1.xml' -OutFile 'hackathons\nativebuilder-gps-defense\data\texbat\metadata\ds1.xml'
Invoke-WebRequest -Uri 'https://rnl-data.ae.utexas.edu/datastore/texbat/ds1.md5' -OutFile 'hackathons\nativebuilder-gps-defense\data\texbat\metadata\ds1.md5'
```

## Exact Errors

Both TEXBAT access attempts timed out in this session:

```text
command timed out after 64066 milliseconds
command timed out after 60053 milliseconds
```

## Additional Runtime Blocker

Even if the TEXBAT `.bin` download succeeded, GNSS-SDR execution is currently blocked because local `gnss-sdr` is absent and Docker Desktop Linux engine is not running.

## Result

- No TEXBAT binary was downloaded.
- No blind RF attack benchmark was executed.
- No `RECORDED_RF_ATTACK` claim is allowed.

## Required Action

Retry TEXBAT download with longer network window and enough disk space, then run GNSS-SDR after Docker Desktop or a local GNSS-SDR installation is available.

