# ROUTES_AND_API_SURFACES

## `01_primary_obsidia_lab_trad/gateway/server.ts`
- `app.get("/api/health", (req, res) => {`
- `app.post("/api/features", (req, res) => {`
- `app.post("/api/simulation", async (req, res) => {`
- `app.get("/api/banking/scenarios", (req, res) => {`
- `app.post("/api/banking/process", (req, res) => {`
- `app.post("/api/banking/gemini", async (req, res) => {`
- `app.get("/api/ecommerce/scenarios", (req, res) => {`
- `app.post("/api/ecommerce/evaluate", (req, res) => {`
- `app.post("/api/gates", async (req, res) => {`
- `app.post("/api/python-engine/decision", async (req, res) => {`
- `app.get("/api/python-engine/health", async (req, res) => {`
- `app.get("/api/artifacts", (req, res) => {`
- `app.get("*", (req, res) => {`

## `01_primary_obsidia_lab_trad/fastapi_engine/api_server/main.py`
- `@app.post("/v1/decision")`
- `@app.get("/v1/replay/{trace_id}")`
- `@app.get("/health")`
- `@app.post("/auth/token")`
- `@app.get("/v1/audit/chain")`

## `01_primary_obsidia_lab_trad/canonical_api/app.py`
- `@APP.post("/v1/decision", response_model=DecisionResponse)`
- `@APP.get("/health")`

## `02_backend_local_skeleton/server.ts`
- `app.get("/api/health", (req, res) => {`
- `app.get("/api/explorer", (req, res) => {`
- `app.get("/api/system", (req, res) => {`
- `app.get("/api/file", (req, res) => {`
- `app.get("/api/status", (req, res) => {`
- `app.post("/api/ingest", (req, res) => {`
- `app.get("/api/audit", (req, res) => {`
- `app.get("*", (req, res) => {`
