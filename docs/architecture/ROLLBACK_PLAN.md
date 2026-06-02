# Rollback Plan — F74 / F76a / F76b
**Date** : 2026-05-30 | Jamais de `git reset --hard`

---

## Ordre de rollback

Toujours de la couche la plus récente vers la plus ancienne :
**F76b → F76a → F74**

---

## Rollback F76b

### Fichiers modifiés par F76b

| Fichier | Backup |
|---|---|
| `apps/obsidia_api/main.py` | `*.bak_20260530_070535_CLAUDE_BEFORE_F76B` |
| `apps/obsidia_api/routes/brody.py` | `*.bak_20260530_070535_CLAUDE_BEFORE_F76B` |
| `.env.example` | `*.bak_20260530_070535_CLAUDE_BEFORE_F76B` |

### Commandes rollback F76b (Windows)

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"

# Restaurer les fichiers modifiés
Copy-Item "apps\obsidia_api\main.py.bak_20260530_070535_CLAUDE_BEFORE_F76B" "apps\obsidia_api\main.py" -Force
Copy-Item "apps\obsidia_api\routes\brody.py.bak_20260530_070535_CLAUDE_BEFORE_F76B" "apps\obsidia_api\routes\brody.py" -Force
Copy-Item ".env.example.bak_20260530_070535_CLAUDE_BEFORE_F76B" ".env.example" -Force

# Supprimer les fichiers créés par F76b
Remove-Item "apps\obsidia_api\auth.py" -ErrorAction SilentlyContinue
Remove-Item "docker-compose.yml" -ErrorAction SilentlyContinue
Remove-Item "docs\architecture\ROLLBACK_PLAN.md" -ErrorAction SilentlyContinue
Remove-Item "tests\api\test_f76b_auth_rate_limit_prod_hardening.py" -ErrorAction SilentlyContinue
```

### Commandes rollback F76b (Linux/macOS)

```bash
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"

cp apps/obsidia_api/main.py.bak_20260530_070535_CLAUDE_BEFORE_F76B apps/obsidia_api/main.py
cp apps/obsidia_api/routes/brody.py.bak_20260530_070535_CLAUDE_BEFORE_F76B apps/obsidia_api/routes/brody.py
cp .env.example.bak_20260530_070535_CLAUDE_BEFORE_F76B .env.example
rm -f apps/obsidia_api/auth.py docker-compose.yml
```

---

## Rollback F76a

### Fichiers modifiés par F76a

| Fichier | Backup |
|---|---|
| `apps/obsidia_api/main.py` | `*.bak_20260530_064339_CLAUDE_BEFORE_PATCH` |
| `apps/obsidia_api/routes/status.py` | `*.bak_20260530_064448_CLAUDE_BEFORE_PATCH` |

```powershell
Copy-Item "apps\obsidia_api\main.py.bak_20260530_064339_CLAUDE_BEFORE_PATCH" "apps\obsidia_api\main.py" -Force
Copy-Item "apps\obsidia_api\routes\status.py.bak_20260530_064448_CLAUDE_BEFORE_PATCH" "apps\obsidia_api\routes\status.py" -Force
Remove-Item "Dockerfile" -ErrorAction SilentlyContinue
```

---

## Rollback F74

### Fichiers modifiés par F74

| Fichier | Backup |
|---|---|
| `requirements.txt` | `*.bak_20260530_063501_CLAUDE_BEFORE_PATCH` |

```powershell
Copy-Item "requirements.txt.bak_20260530_063501_CLAUDE_BEFORE_PATCH" "requirements.txt" -Force
Remove-Item ".python-version" -ErrorAction SilentlyContinue
Remove-Item ".env.example" -ErrorAction SilentlyContinue
Remove-Item "requirements-dev.txt" -ErrorAction SilentlyContinue
Remove-Item "QUICKSTART.md" -ErrorAction SilentlyContinue
Remove-Item "QUICKSTART_FRESH_CLONE.md" -ErrorAction SilentlyContinue
Remove-Item "scripts\run_api.ps1" -ErrorAction SilentlyContinue
Remove-Item "scripts\run_api.sh" -ErrorAction SilentlyContinue
```

---

## Vérification post-rollback (à tout niveau)

```bash
python -m pytest tests/sigma tests/api/test_f63_sigma_monitoring_endpoints_readonly.py \
  tests/api/test_f65_sigma_bus_readonly_bridge.py -q --tb=short
```

Résultat attendu : `PASS` — zéro failure.

---

_Rollback Plan | 2026-05-30 | Jamais de git reset --hard | KX108_ONLY_
