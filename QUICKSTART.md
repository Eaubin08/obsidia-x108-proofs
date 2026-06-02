# Obsidia X-108 — Quick Start

See **[QUICKSTART_FRESH_CLONE.md](QUICKSTART_FRESH_CLONE.md)** for the complete fresh clone guide.

## TL;DR

```bash
git clone https://github.com/Eaubin08/obsidia-x108-proofs.git
cd obsidia-x108-proofs
python3.12 -m venv .venv && source .venv/bin/activate   # Linux
# py -3.12 -m venv .venv && .\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python -m pytest tests/sigma -q
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
```
