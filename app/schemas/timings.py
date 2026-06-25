from pydantic import BaseModel, ConfigDict, Field


class ChatTimings(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "spell_correction_ms": 1.2,
            "synonym_resolution_ms": 0.6,
            "intent_normalization_ms": 0.8,
            "router_ms": 3.0,
            "query_ms": 12.0,
            "context_ms": 5.0,
            "prompt_ms": 1.0,
            "llm_ms": 4210.0,
            "total_ms": 4235.0,
        }
    })

    spell_correction_ms: float = Field(default=0, description="Correccion ortografica deterministica")
    synonym_resolution_ms: float = Field(default=0, description="Resolucion de sinonimos empresariales")
    intent_normalization_ms: float = Field(default=0, description="Normalizacion canonica de la pregunta")
    social_layer_ms: float = Field(default=0, description="Capa social e interacciones conversacionales")
    identity_layer_ms: float = Field(default=0, description="Deteccion de identidad del asistente")
    token_optimization_ms: float = Field(default=0, description="Capa de demostracion de optimizacion de tokens")
    system_explanation_ms: float = Field(default=0, description="Explicacion deterministica del sistema")
    capability_layer_ms: float = Field(default=0, description="Capa de descubrimiento de capacidades ejecutivas")
    entity_extraction_ms: float = Field(default=0, description="Extraccion deterministica de entidades")
    router_ms: float = Field(default=0, description="Clasificacion de intencion")
    deterministic_ms: float = Field(default=0, description="Generacion deterministica de respuesta")
    query_ms: float = Field(default=0, description="Ejecucion de consulta analitica")
    context_ms: float = Field(default=0, description="Construccion de contexto empresarial")
    prompt_ms: float = Field(default=0, description="Construccion del prompt final")
    llm_ms: float = Field(default=0, description="Llamada a Ollama incluyendo fallback")
    total_ms: float = Field(default=0, description="Tiempo total de la solicitud")
