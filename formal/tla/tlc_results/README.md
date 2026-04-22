# TLC Model-Checking Results

Ce dossier contiendra les logs de vérification TLC générés automatiquement
par le workflow GitHub Actions (.github/workflows/verify.yml).

## Relancer manuellement
```bash
cd formal/tla
tlc X108.tla -config X108.cfg > tlc_results/X108_results.log
tlc DistributedX108.tla -config DistributedX108.cfg > tlc_results/DistributedX108_results.log
```

Les résultats sont aussi archivés comme artifacts GitHub Actions après chaque push.
