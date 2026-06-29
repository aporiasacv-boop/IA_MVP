from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import (
    analytics,
    business_knowledge,
    enterprise_knowledge_service,
    business_analytics,
    business_ontology,
    business_entities,
    canonical_entities,
    entity_profiles,
    knowledge,
    reasoning,
    semantic_intent,
    evidence,
    executive_response,
    executive_advisor,
    finops,
    simulation,
    decision,
    knowledge_pack,
    chat,
    health,
    hybrid_chat,
    insights,
    metadata,
    metrics,
    operational_audit,
    query,
    semantic,
    upload,
    version,
)
from app.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(version.router)
app.include_router(upload.router, prefix="/upload")
app.include_router(analytics.router)
app.include_router(insights.router)
app.include_router(metadata.router)
app.include_router(chat.router)
app.include_router(hybrid_chat.router)
app.include_router(semantic.router)
app.include_router(query.router)
app.include_router(metrics.router)
app.include_router(business_analytics.router)
app.include_router(operational_audit.router)
app.include_router(business_entities.router)
app.include_router(canonical_entities.router)
app.include_router(entity_profiles.router)
app.include_router(business_ontology.router)
app.include_router(knowledge.router)
app.include_router(reasoning.router)
app.include_router(semantic_intent.router)
app.include_router(evidence.router)
app.include_router(executive_response.router)
app.include_router(executive_response.cost_router)
app.include_router(executive_advisor.router)
app.include_router(finops.router)
app.include_router(simulation.router)
app.include_router(decision.router)
app.include_router(knowledge_pack.router)
app.include_router(business_knowledge.router)
app.include_router(enterprise_knowledge_service.router)
