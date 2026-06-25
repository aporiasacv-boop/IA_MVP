class OrchestrationHealthError(Exception):
    pass


def validate_orchestration_health(issues: dict) -> dict:
    blocking = []
    if issues.get("provider_down"):
        blocking.append("Proveedor LLM caído o con fallback activo")
    if issues.get("timeout"):
        blocking.append("Timeouts de proveedor LLM detectados")
    if issues.get("empty_response"):
        blocking.append("Respuestas vacías del proveedor")
    if issues.get("no_evidence"):
        blocking.append("Respuestas sin evidencia en el paquete")
    if issues.get("negative_cost"):
        blocking.append("Costos negativos detectados")
    if issues.get("unknown_model"):
        blocking.append("Modelo LLM desconocido")

    if blocking:
        raise OrchestrationHealthError("; ".join(blocking))
    return {"status": "healthy", "checks": len(blocking)}
