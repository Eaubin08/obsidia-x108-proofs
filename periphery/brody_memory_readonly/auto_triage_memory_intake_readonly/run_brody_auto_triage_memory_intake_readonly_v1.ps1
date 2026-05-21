# --- AUTO-OPTIMIZATION TRIGGER BEFORE INTAKE ---
Get-Process -Name "chrome", "msedge" -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = "High" }
[System.GC]::Collect()

Write-Host "[X108-SYSTEM] Priorités CPU réalignées. Démarrage de l'Intake V1..." -ForegroundColor Green

# (Le code d'appel du script d'auto-triage s'insérera ici au prochain bloc)
