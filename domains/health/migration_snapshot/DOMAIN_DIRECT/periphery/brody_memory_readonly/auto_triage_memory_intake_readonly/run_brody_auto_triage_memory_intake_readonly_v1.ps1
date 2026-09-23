# --- AUTO-OPTIMIZATION TRIGGER BEFORE INTAKE ---
Get-Process -Name "chrome", "msedge" -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = "High" }
[System.GC]::Collect()

Write-Host "[X108-SYSTEM] Priorités CPU réalignées. Démarrage de l'Intake V1..." -ForegroundColor Green

# TODO: AUTO_TRIAGE_RUNNER_INCOMPLETE
# Ce runner ne lance pas encore le script Python brody_auto_triage_memory_intake_readonly_v1.py.
# Statut : BLOCKED — ne pas ajouter d'exécution automatique sans validation KX108_ONLY.
