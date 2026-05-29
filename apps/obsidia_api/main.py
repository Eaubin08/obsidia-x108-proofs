"""
Obsidia API — FastAPI application. V5B full closure.
All responses: readonly=True, decision_authority=KX108_ONLY.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Obsidia X-108 API", version="V5B")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST"], allow_headers=["*"])

# Import all route modules
from apps.obsidia_api.routes.status import router as status_router
from apps.obsidia_api.routes.brody import router as brody_router
from apps.obsidia_api.routes.translation import router as translation_router
from apps.obsidia_api.routes.os_trad_ir_reverse import router as os_trad_ir_reverse_router
from apps.obsidia_api.routes.context import router as context_router
from apps.obsidia_api.routes.memory import router as memory_router
from apps.obsidia_api.routes.gencoin import router as gencoin_router
from apps.obsidia_api.routes.graphiti import router as graphiti_router
from apps.obsidia_api.routes.x108 import router as x108_router
from apps.obsidia_api.routes.os3 import router as os3_router
from apps.obsidia_api.routes.worldcalls import router as worldcalls_router
from apps.obsidia_api.routes.blockchain import router as blockchain_router
from apps.obsidia_api.routes.audit import router as audit_router
from apps.obsidia_api.routes.periphery_ops import router as periphery_ops_router
from apps.obsidia_api.routes.brody_monitoring import router as brody_monitoring_router
from apps.obsidia_api.routes.runtime_freeze import router as runtime_freeze_router
from apps.obsidia_api.routes.bus import router as bus_router

for r in [status_router, brody_router, translation_router, os_trad_ir_reverse_router, context_router,
           memory_router, gencoin_router, graphiti_router, x108_router,
           os3_router, worldcalls_router, blockchain_router, audit_router,
           periphery_ops_router, brody_monitoring_router, runtime_freeze_router, bus_router]:
    app.include_router(r)


@app.get("/")
async def root():
    return {"service": "obsidia-api", "version": "V5B", "mode": "readonly_dryrun", "decision_authority": "KX108_ONLY"}
