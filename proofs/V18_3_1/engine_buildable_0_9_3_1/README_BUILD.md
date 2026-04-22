# Build / Run (local)

## 1) Quick run (kernel)

```bash
cd <this_folder>
python entrypoint.py
```

## 2) Run API (if you have FastAPI/Uvicorn)

```bash
python -m uvicorn api.api_server.main:app --reload
```

## 3) Run fusion tests F01→F04

```bash
python -m pytest -q tests_fusion/test_fusion_F01_F04.py
```

## Notes
- This pack is **flattened** (no nested zips). It is the **buildable** form of the Beta 0.9.3.* kernel.
- Audit V3 report + manifests are in `docs/audit_v3/`.
