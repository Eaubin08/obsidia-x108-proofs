# OBSIDIA TERMINAL V0 — wrapper non souverain.
# Usage : .\scripts\obsidia.ps1 doctor
#         .\scripts\obsidia.ps1 "statut du kernel"
# Aucune mutation possible : le CLI Python ne contient aucun subprocess ni flag d'application.
$ErrorActionPreference = "Stop"
$cli = Join-Path $PSScriptRoot "obsidia_cli.py"
python $cli @args
