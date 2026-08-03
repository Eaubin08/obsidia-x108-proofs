# FGI GNSS-SDR Blocked Report

Date: 2026-08-03
Status: `SUPERSEDED_BY_GNSS_SDR_EXECUTION_NO_PVT`

## Real Dataset Present

- Dataset: FGI-SpoofRepo / FGI-JSDR.
- URL: `https://etsin.fairdata.fi/dataset/367379a8-7d78-4b08-91f0-8027ce7a621b`
- DOI: `10.23729/7a648509-2ca8-4a7d-8223-0b429182f857`
- License: `CC-BY-4.0`
- Scenario scope: `/FGISpoofRepo/UT_DFMC`
- Package SHA-256: `1df410917bc853b5ab843667acd47ede4e03bf237ce3e399d791a597ce9713ad`
- L1/E1 SHA-256: `e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72`

## Receiver Runtime Update

This blocker is no longer the current boundary when commands run with the unsandboxed Windows user. Docker Desktop and the local `carlesfernandez/docker-gnsssdr:latest` image were reused successfully for the FGI hostile RF lot.

Recovered runtime:

- Docker version: `29.4.3`.
- Context: `desktop-linux`.
- Image: `carlesfernandez/docker-gnsssdr:latest`.
- GNSS-SDR version: `0.0.21.git-next-2a7214a4f`.

The current blocker is technical receiver output quality, not Docker availability:

- GNSS-SDR acquisition/tracking/observables: produced.
- NAV messages: not produced.
- PVT positions: not produced.
- Live X-108: called successfully.
- Receipt: produced.

The historical sandbox limitation still exists for the `codexsandboxoffline` user. Docker daemon access works when the command is executed as the normal Windows user.

## Next Required Technical Action

One of these must be done before `RECORDED_RF_ATTACK` can honestly pass:

- Run the official FGI-GSRx receiver with MATLAB/Octave on the FGI UT_DFMC L1/E1 file.
- Produce a GNSS-SDR configuration that yields NAV/PVT from the official `real 8-bit I`, `26 MHz`, `1569.03 MHz` L1/E1 recording without inventing physical parameters.
- Execute a matched nominal/hostile pair and compute metrics after label reveal.

No RF emission is needed. This remains offline file processing only.
