/**
 * Catálogo centralizado — Localización Español v1
 * Toda etiqueta visible para usuarios de negocio debe provenir de aquí.
 */

export const HANDLED_BY_LABELS: Record<string, string> = {
  business_pipeline: 'Canal Empresarial',
  conversation_memory: 'Memoria Conversacional',
  slot_clarification: 'Aclaración de Consulta',
  guided_fallback: 'Asistencia Guiada',
  capability_discovery: 'Descubrimiento de Capacidades',
  legacy_chat: 'Conversación General',
  executive_reasoning: 'Razonamiento Ejecutivo',
  product_identity: 'Identidad del Asistente',
  business_knowledge: 'Conocimiento Institucional',
}

export const QUERY_TYPE_LABELS: Record<string, string> = {
  COUNT_CLIENTES: 'Conteo de clientes',
  COUNT_PROVEEDORES: 'Conteo de proveedores',
  TOP_CLIENTES: 'Principales clientes',
  TOP_PROVEEDORES: 'Principales proveedores',
  MAX_PROVEEDOR_MES: 'Proveedor con mayor movimiento',
  MAX_TRANSACCION_CLIENTE: 'Transacción máxima por cliente',
  LOOKUP_CLIENTE_BY_CUENTA: 'Cliente por cuenta',
  DATA_COVERAGE: 'Cobertura temporal de datos',
  DATASET_INFO: 'Información del conjunto de datos',
  SYSTEM_CAPABILITIES: 'Capacidades del sistema',
  capability_discovery: 'Descubrimiento de capacidades',
  UNSUPPORTED: 'No soportada',
}

export const DOMAIN_LABELS: Record<string, string> = {
  VENTAS: 'Ventas',
  COMPRAS: 'Compras',
  INVENTARIO: 'Inventario',
  FACTURACION: 'Facturación',
  FINANZAS: 'Finanzas',
  LOGISTICA: 'Logística',
  PRODUCCION: 'Producción',
}

export const RESPONSE_MODE_LABELS: Record<string, string> = {
  DETERMINISTIC: 'Determinístico',
  GENERATIVE: 'Generativo con IA',
}

export const METRIC_TOOLTIPS: Record<string, string> = {
  coverageScore:
    'Porcentaje de consultas resueltas mediante procesos empresariales estructurados.',
  coverageGapScore:
    'Proporción de consultas que terminaron en asistencia guiada o conversación general.',
  successRate: 'Porcentaje de consultas respondidas exitosamente.',
  avgResponseTime: 'Tiempo promedio de respuesta del sistema en milisegundos.',
  aiAvoidanceRate:
    'Porcentaje de consultas resueltas sin recurrir a IA conversacional.',
  legacyDependencyRate:
    'Porcentaje de consultas que requirieron el canal conversacional general.',
  equivalentGptCost: 'Costo estimado equivalente si se hubiera usado GPT.',
  equivalentClaudeCost: 'Costo estimado equivalente si se hubiera usado Claude.',
  equivalentOllamaCost: 'Costo estimado equivalente del uso de Ollama local.',
  totalRequests: 'Número total de consultas registradas en el período.',
  businessPipelinePct: 'Porcentaje de consultas atendidas por el canal empresarial.',
  memoryPct: 'Porcentaje de consultas resueltas con memoria conversacional.',
  capabilityDiscoveryPct: 'Porcentaje de consultas de descubrimiento de capacidades.',
  guidedFallbackPct: 'Porcentaje de consultas con asistencia guiada.',
  legacyPct: 'Porcentaje de consultas en conversación general.',
}

export const es = {
  nav: {
    assistant: 'Asistente IA',
    performance: 'Rendimiento',
    analytics: 'Analítica Empresarial',
    audit: 'Auditoría Operacional',
    entities: 'Entidades Empresariales',
    canonical: 'Identidad Canónica',
    profiles: 'Perfiles de Comportamiento',
    ontology: 'Ontología Empresarial',
    knowledge: 'Servicio de Conocimiento',
    knowledgeObjects: 'Objetos de Conocimiento (EKO)',
    reasoning: 'Razonamiento Empresarial',
    semanticIntent: 'Intención Semántica',
    evidence: 'Paquete de Evidencia',
    aiCosts: 'FinOps',
    finops: 'FinOps',
    simulator: 'Simulador',
    decisionCenter: 'Centro de Decisiones',
    platformActive: 'Plataforma activa',
  },
  common: {
    refresh: 'Actualizar',
    loading: 'Cargando…',
    count: 'Cantidad',
    question: 'Pregunta',
    channel: 'Canal Utilizado',
    queryType: 'Tipo de Consulta',
    percent: '%',
    scaleZeroHundred: 'Escala 0–100',
    assistedAndGeneral: 'Asistencia guiada + conversación general',
    noData: 'Sin datos registrados aún.',
    exportJson: 'Exportar JSON',
    exportCsv: 'Exportar CSV',
    errorAnalytics: 'No fue posible obtener la analítica del sistema.',
    errorAudit: 'No fue posible obtener la auditoría operacional del backend.',
    errorEntities: 'No fue posible obtener el catálogo de entidades del backend.',
  },
  businessEntities: {
    eyebrow: 'Datos maestros',
    title: 'Entidades empresariales',
    subtitle:
      'Catálogo maestro estructural descubierto en el diario general. Solo lectura — sin clasificación de negocio aún.',
    errorLoad: 'No fue posible obtener el catálogo de entidades del backend.',
    stats: {
      title: 'Resumen del catálogo',
      subtitle: 'Entidades registradas por dimensión de origen en D365.',
      total: 'Total de entidades',
      loaded: 'Última carga procesada',
      duplicated: 'Códigos en múltiples fuentes',
      lastRefresh: 'Última actualización',
    },
    filters: {
      searchPlaceholder: 'Buscar por código o nombre…',
      allSources: 'Todas las fuentes',
      account: 'Cuenta contable',
      vendor: 'Dimensión proveedor',
      customer: 'Dimensión cliente',
      allStatuses: 'Todos los estados',
    },
    table: {
      title: 'Explorador de entidades',
      subtitle: 'Ordena y filtra el universo descubierto antes de la ontología de negocio.',
      code: 'Código',
      name: 'Nombre',
      movements: 'Movimientos',
      amount: 'Monto total',
      source: 'Columna origen',
      status: 'Estado',
      showing: 'Mostrando',
      of: 'de',
      prev: 'Anterior',
      next: 'Siguiente',
    },
  },
  canonicalEntities: {
    eyebrow: 'Resolución de entidades',
    title: 'Identidad canónica',
    subtitle:
      'Organizaciones únicas y sugerencias de unión entre alias del diario. Sin merge automático — solo evidencia.',
    errorLoad: 'No fue posible obtener las entidades canónicas del backend.',
    stats: {
      title: 'Resumen de identidad',
      total: 'Canónicas',
      matches: 'Grupos con alias',
      pending: 'Sugerencias pendientes',
      suggestions: 'Sugerencias generadas',
      unresolved: 'Sin resolver (%)',
    },
    filters: {
      searchPlaceholder: 'Buscar organización canónica…',
    },
    canonical: {
      title: 'Entidades canónicas',
    },
    suggestions: {
      title: 'Sugerencias pendientes',
      subtitle: 'Pares con evidencia determinística. Requieren revisión humana antes de unir.',
      source: 'Origen',
      candidate: 'Candidata',
      rule: 'Regla',
      score: 'Score',
    },
    table: {
      name: 'Organización',
      rfc: 'RFC',
      aliases: 'Alias detectados',
    },
  },
  entityProfiles: {
    eyebrow: 'Perfilado de datos',
    title: 'Perfiles de comportamiento',
    subtitle:
      'Métricas transaccionales descubiertas en el diario general por entidad canónica. Clasificación por comportamiento, no por nombre.',
    errorLoad: 'No fue posible obtener los perfiles empresariales del backend.',
    stats: {
      title: 'Resumen ejecutivo',
      total: 'Perfiles generados',
      completeness: 'Completitud promedio',
      movements: 'Movimientos perfilados',
      withoutMovements: 'Sin movimientos',
      generationTime: 'Tiempo de generación',
      lastRefresh: 'Última actualización',
    },
    filters: {
      searchPlaceholder: 'Buscar organización…',
    },
    list: {
      title: 'Explorador de perfiles',
      subtitle: 'Ordenado por volumen transaccional en el diario.',
    },
    table: {
      name: 'Organización',
      movements: 'Movimientos',
      amount: 'Monto total',
      completeness: 'Completitud',
    },
    detail: {
      title: 'Detalle de comportamiento',
      empty: 'Selecciona un perfil para ver su actividad.',
      activity: 'Actividad',
      range: 'Periodo',
      debitCredit: 'Ratio débito/crédito',
      currencies: 'Divisas',
      monthly: 'Distribución mensual',
      accounts: 'Cuentas relacionadas',
      counterparties: 'Principales contrapartes',
    },
  },
  businessOntology: {
    eyebrow: 'Capa semántica',
    title: 'Ontología empresarial',
    subtitle:
      'Clasificación semántica por comportamiento transaccional. Sugerencias determinísticas — sin aprobación automática.',
    errorLoad: 'No fue posible obtener la ontología empresarial del backend.',
    stats: {
      title: 'Resumen semántico',
      entities: 'Entidades con sugerencias',
      pending: 'Pendientes',
      approved: 'Aprobadas',
      rules: 'Reglas activas',
      confidence: 'Confianza promedio',
      withoutSuggestions: 'Sin sugerencias',
    },
    filters: {
      searchPlaceholder: 'Buscar entidad…',
    },
    list: {
      title: 'Explorador semántico',
    },
    table: {
      entity: 'Entidad',
      movements: 'Movimientos',
      suggestions: 'Sugerencias',
      category: 'Concepto',
      classification: 'Clasificación',
      rule: 'Regla',
      score: 'Confianza',
      status: 'Estado',
    },
    detail: {
      title: 'Vista semántica',
      empty: 'Selecciona una entidad para ver su clasificación sugerida.',
      movements: 'Movimientos perfilados',
      dimensions: 'Dimensiones',
      suggestions: 'Clasificaciones sugeridas',
    },
  },
  enterpriseKnowledgeService: {
    eyebrow: 'Servicio transversal',
    title: 'Servicio de Conocimiento',
    subtitle:
      'Punto único de acceso al conocimiento empresarial: proveedores activos, documentos, categorías y estado del cache centralizado.',
    searchPlaceholder: 'Buscar en el servicio de conocimiento…',
    searchResults: 'Resultados de búsqueda',
    noResults: 'No se encontraron coincidencias.',
    categoriesTitle: 'Categorías disponibles',
    documentsLabel: 'documentos',
    providersTitle: 'Proveedores de conocimiento',
    providerActive: 'Activo',
    providerPlanned: 'Planificado',
    stats: {
      documents: 'Documentos cargados',
      faq: 'Entradas de FAQ',
      cacheStatus: 'Estado del cache',
      cacheOk: 'Válido',
      cacheDegraded: 'Degradado',
      reloadTime: 'Tiempo de carga',
      cacheHitRate: 'Tasa de aciertos en cache',
    },
  },
  businessKnowledge: {
    eyebrow: 'Conocimiento institucional',
    title: 'Base de conocimiento empresarial',
    subtitle:
      'Conceptos, preguntas frecuentes, reglas, escenarios, glosario y ejemplos cargados desde el paquete de conocimiento.',
    searchPlaceholder: 'Buscar en el conocimiento institucional…',
    searchResults: 'Resultados de búsqueda',
    noResults: 'No se encontraron coincidencias.',
    categoriesTitle: 'Categorías disponibles',
    documentsLabel: 'documentos',
    stats: {
      documents: 'Documentos cargados',
      faq: 'Entradas de FAQ',
      hits: 'Consultas resueltas',
    },
  },
  enterpriseKnowledge: {
    eyebrow: 'Capa de conocimiento',
    title: 'Conocimiento empresarial',
    subtitle:
      'Objeto de conocimiento estructurado (EKO v1). Conocimiento verificable sin SQL ni narrativa generada por IA.',
    errorLoad: 'No fue posible obtener el conocimiento empresarial del backend.',
    stats: {
      title: 'Resumen de conocimiento',
      objects: 'Objetos EKO',
      completeness: 'Completitud promedio',
      confidence: 'Confianza promedio',
      incomplete: 'Objetos incompletos',
    },
    filters: {
      searchPlaceholder: 'Buscar entidad…',
    },
    list: {
      title: 'Explorador de conocimiento',
    },
    table: {
      entity: 'Entidad',
      completeness: 'Completitud',
      confidence: 'Confianza',
      key: 'Clave',
      value: 'Valor',
      source: 'Origen',
    },
    sections: {
      identity: 'Identidad',
      ontology: 'Ontología (roles, naturaleza, comportamiento)',
      facts: 'Hechos verificables',
      signals: 'Señales',
      alerts: 'Alertas',
      relationships: 'Relaciones',
      evidence: 'Evidencia',
    },
    detail: {
      title: 'Vista de conocimiento',
      empty: 'Selecciona una entidad para explorar su objeto de conocimiento.',
      completeness: 'Completitud',
      confidence: 'Confianza',
    },
  },
  enterpriseReasoning: {
    eyebrow: 'Capa de razonamiento',
    title: 'Razonamiento empresarial',
    subtitle:
      'Conclusiones determinísticas y explicables (ERO v1) derivadas del EKO. Sin IA generativa ni narrativa.',
    errorLoad: 'No fue posible obtener el razonamiento empresarial del backend.',
    stats: {
      title: 'Resumen de razonamiento',
      objects: 'Objetos ERO',
      rules: 'Reglas ejecutadas',
      confidence: 'Confianza promedio',
      findings: 'Hallazgos promedio',
      recommendations: 'Recomendaciones promedio',
    },
    filters: {
      searchPlaceholder: 'Buscar entidad…',
    },
    list: {
      title: 'Explorador de razonamiento',
    },
    table: {
      entity: 'Entidad',
      findings: 'Hallazgos',
      confidence: 'Confianza',
      key: 'Clave',
      rule: 'Regla',
      severity: 'Severidad',
    },
    sections: {
      findings: 'Hallazgos',
      signals: 'Señales',
      alerts: 'Alertas',
      risks: 'Riesgos',
      opportunities: 'Oportunidades',
      recommendations: 'Recomendaciones',
      evidence: 'Evidencia',
    },
    detail: {
      title: 'Vista de razonamiento',
      empty: 'Selecciona una entidad para explorar sus conclusiones.',
      confidence: 'Confianza',
      rules: 'Reglas evaluadas',
    },
  },
  semanticIntent: {
    eyebrow: 'Capa semántica',
    title: 'Intención semántica',
    subtitle:
      'Planificador de ejecución empresarial determinístico. Interpreta la pregunta y decide qué conocimiento (EKO/ERO) se requiere — sin LLM ni SQL.',
    errorLoad: 'No fue posible contactar el planificador semántico.',
    stats: {
      title: 'Resumen del planificador',
      parses: 'Parseos semánticos',
      plans: 'Planes generados',
      confidence: 'Confianza promedio',
      successRate: 'Tasa de éxito',
      unknownVerbs: 'Verbos desconocidos',
    },
    form: {
      label: 'Pregunta empresarial',
      analyze: 'Analizar y planificar',
    },
    detail: {
      title: 'Resultado semántico',
      empty: 'Ingresa una pregunta para analizar.',
      verb: 'Verbo',
      category: 'Categoría',
      confidence: 'Confianza',
      strategy: 'Estrategia',
      objects: 'Objetos detectados',
      context: 'Contexto',
      knowledge: 'Conocimiento requerido (EKO)',
      reasoning: 'Razonamiento requerido (ERO)',
      evidence: 'Evidencia requerida',
      incomplete: 'Plan incompleto.',
      incompatible: 'Estrategia incompatible detectada.',
    },
  },
  evidencePackage: {
    eyebrow: 'Recuperación de evidencia',
    title: 'Paquete de evidencia empresarial',
    subtitle:
      'Contrato EEP v1 para consumo LLM. Ensambla EKO + ERO según el plan SBEP — sin SQL, sin texto generado.',
    errorLoad: 'No fue posible construir el paquete de evidencia.',
    stats: {
      title: 'Resumen de paquetes',
      packages: 'Paquetes generados',
      size: 'Tamaño promedio (bytes)',
      items: 'Items de evidencia',
      confidence: 'Confianza promedio',
      missing: 'Sin evidencia',
    },
    form: {
      label: 'Pregunta empresarial',
      build: 'Construir paquete',
      example: 'Cargar ejemplo',
    },
    detail: {
      title: 'Paquete de evidencia empresarial',
      empty: 'Construye un paquete para explorar su contenido.',
      strategy: 'Estrategia',
      confidence: 'Confianza',
      knowledge: 'Conocimiento seleccionado',
      reasoning: 'Razonamiento seleccionado',
      facts: 'Hechos',
      recommendations: 'Recomendaciones',
      evidence: 'Índice de evidencia',
      limitations: 'Limitaciones',
      tableKey: 'Clave',
      tableSource: 'Fuente',
      tableConfidence: 'Conf.',
    },
  },
  simulator: {
    eyebrow: 'Motor de decisión',
    title: 'Simulador',
    subtitle:
      'Simula escenarios de operación con el comportamiento histórico registrado en FinOps y Operational Metrics.',
    baseline: 'Fuente de línea base',
    run: 'Ejecutar simulación',
    predefined: 'Escenarios predefinidos',
    parameters: 'Parámetros del escenario',
    users: 'Usuarios',
    queriesPerUser: 'Consultas por usuario/día',
    pipelinePct: '% Business Pipeline',
    knowledgePct: '% Knowledge Service',
    memoryPct: '% Conversation Memory',
    executivePct: '% Executive Reasoning',
    legacyPct: '% Legacy Chat',
    provider: 'Proveedor LLM',
    concurrency: 'Concurrencia',
    peakHours: 'Horas pico',
    workingDays: 'Días laborales',
    executiveSummary: 'Resumen ejecutivo',
    monthlyCost: 'Costo mensual',
    yearlyCost: 'Costo anual proyectado',
    avoidedCost: 'Costo evitado',
    roi: 'ROI',
    infrastructure: 'Infraestructura estimada',
    latencyP95: 'Latencia P95',
    providerComparison: 'Comparación de proveedores',
    recommendations: 'Recomendaciones automáticas',
  },
  decisionCenter: {
    eyebrow: 'Motor de decisión ejecutiva',
    title: 'Centro de Decisiones',
    subtitle:
      'Recomendaciones ejecutivas fundamentadas en evidencia operativa, FinOps, simulaciones y conocimiento enterprise.',
    generate: 'Generar recomendación',
    decisionType: 'Tipo de decisión',
    scenario: 'Escenario de referencia',
    executiveSummary: 'Resumen ejecutivo',
    mainRecommendation: 'Recomendación principal',
    alternatives: 'Recomendaciones alternativas',
    economicImpact: 'Impacto económico mensual',
    expectedSavings: 'Ahorro esperado',
    risks: 'Riesgos',
    opportunities: 'Oportunidades',
    evidence: 'Evidencia utilizada',
    confidence: 'Nivel de confianza',
    limitations: 'Limitaciones',
    source: 'Fuente',
    metric: 'Métrica',
    scenarios: [
      { id: 'demo', label: 'Demostración' },
      { id: 'piloto', label: 'Piloto' },
      { id: 'produccion', label: 'Producción' },
      { id: 'enterprise', label: 'Empresarial' },
    ],
  },
  finops: {
    eyebrow: 'Métricas operativas',
    title: 'FinOps',
    subtitle:
      'Costos reales por consulta, ahorro por canal, comparativa de proveedores y proyección de capacidad.',
    executiveSummary: 'Resumen ejecutivo',
    costToday: 'Costo hoy',
    costMonth: 'Costo del mes',
    costYearProjected: 'Costo anual proyectado',
    llmAvoidance: 'LLM evitadas',
    costBreakdown: 'Desglose de costos',
    costPerUser: 'Costo por usuario',
    costPerSession: 'Costo por sesión',
    knowledgeRuntime: 'Knowledge Runtime',
    businessPipeline: 'Business Pipeline',
    executiveReasoning: 'Executive Reasoning',
    providerComparison: 'Comparativa OpenAI vs Claude vs Ollama',
    savingsTitle: 'Ahorro operativo',
    avoidedCost: 'Costo evitado',
    accumulatedSavings: 'Ahorro acumulado',
    forecastTitle: 'Forecast de capacidad',
    users: 'usuarios',
    queries: 'consultas/mes',
    table: {
      provider: 'Proveedor',
      usage: 'Uso',
      cost: 'Costo',
      tokens: 'Tokens',
      latency: 'Tiempo',
      share: 'Participación',
    },
  },
  aiCosts: {
    eyebrow: 'Orquestación de IA',
    title: 'Costos IA',
    subtitle:
      'Costos, tokens y latencia del Executive Response Engine por proveedor LLM.',
    errorLoad: 'No fue posible cargar los costos de IA.',
    overview: 'Resumen operativo',
    providerComparison: 'Comparativa entre proveedores',
    costPerUser: 'Costo por usuario',
    noProviderData: 'Sin datos de proveedores todavía.',
    provider: 'Proveedor',
    requests: 'Consultas',
    tokens: 'Tokens',
    cost: 'Costo',
    latency: 'Latencia',
    totalRequests: 'Consultas LLM',
    dailyCost: 'Costo diario',
    monthlyCost: 'Costo mensual',
    costPerQuery: 'Costo por consulta',
    avgCostPerQuestion: 'Costo promedio por pregunta',
    totalTokens: 'Tokens totales',
    avgLatency: 'Latencia promedio',
    hallucinationGuard: 'Guardias anti-alucinación',
  },
  analytics: {
    eyebrow: 'Analítica Empresarial',
    title: 'Adopción, cobertura y ahorro',
    subtitle: 'Métricas de negocio derivadas de la observabilidad real del enrutador híbrido.',
    coverage: {
      title: 'Cobertura de canales',
      subtitle: 'Distribución real de canales de atención del asistente.',
      totalRequests: 'Total de consultas',
      businessPipeline: 'Canal empresarial',
      memory: 'Memoria conversacional',
      capabilityDiscovery: 'Descubrimiento de capacidades',
      guidedFallback: 'Asistencia guiada',
      legacy: 'Conversación general',
    },
    performance: {
      title: 'Rendimiento',
      subtitle: 'Latencias agregadas del pipeline híbrido.',
      p50: 'Percentil 50',
      p95: 'Percentil 95',
      p99: 'Percentil 99',
      avgTotalTime: 'Tiempo promedio de respuesta',
    },
    financial: {
      title: 'Impacto financiero',
      subtitle: 'Ahorro por determinismo y costos equivalentes configurables.',
      aiAvoidanceRate: 'Consultas resueltas sin IA',
      legacyDependencyRate: 'Dependencia de IA conversacional',
      gptCost: 'Costo equivalente GPT',
      claudeCost: 'Costo equivalente Claude',
      ollamaCost: 'Costo equivalente Ollama',
      deterministicRequests: 'Consultas determinísticas',
    },
    topQueries: {
      title: 'Consultas más frecuentes',
      subtitle: 'Consultas reales con canal y tasa de éxito.',
      successRate: 'Tasa de éxito',
    },
  },
  audit: {
    eyebrow: 'Auditoría Operacional',
    title: 'Realidad operacional del asistente',
    subtitle:
      'Telemetría del enrutador híbrido transformada en decisiones de producto.',
    overview: {
      title: 'Resumen general',
      subtitle: 'Volumen, distribución y puntajes de cobertura operativa.',
      totalRequests: 'Total de consultas',
      successes: 'Éxitos',
      failures: 'Fallos',
      businessPipeline: 'Canal empresarial',
      memory: 'Memoria conversacional',
      clarification: 'Aclaración de consulta',
      capability: 'Descubrimiento de capacidades',
      guidedFallback: 'Asistencia guiada',
      legacy: 'Conversación general',
      coverageScore: 'Cobertura operativa',
      coverageGapScore: 'Brecha de cobertura',
    },
    coverageGaps: {
      title: 'Brechas de cobertura',
      subtitle:
        'Preguntas que terminaron en conversación general o asistencia guiada.',
    },
    topFailures: {
      title: 'Consultas no resueltas más frecuentes',
      subtitle: 'Preguntas con respuesta fallida agrupadas por frecuencia.',
    },
    topRoutes: {
      title: 'Canales más utilizados',
      subtitle: 'Canales de atención más frecuentes del enrutador híbrido.',
    },
    adoption: {
      title: 'Adopción',
      subtitle: 'Uso de capacidades conversacionales existentes.',
      suggestedQuestions: 'Preguntas sugeridas',
      conversationMemory: 'Memoria conversacional',
      slotClarification: 'Aclaración de consulta',
      capabilityDiscovery: 'Descubrimiento de capacidades',
    },
    exportFilename: 'brechas_cobertura',
  },
  performance: {
    backendEyebrow: 'Métricas reales del backend',
    backendTitle: 'Observabilidad del enrutador híbrido',
    backendSubtitle: 'Datos persistidos del servidor de métricas.',
    totalRequests: 'Total de consultas',
    businessPipelineRequests: 'Consultas por canal empresarial',
    legacyChatRequests: 'Consultas por conversación general',
    guidedFallbackRequests: 'Consultas por asistencia guiada',
    capabilityDiscoveryRequests: 'Consultas por descubrimiento de capacidades',
    suggestedQuestionsGenerated: 'Preguntas sugeridas generadas',
    avgSuggestionsPerResponse: 'Promedio de sugerencias por respuesta',
    pipelinePct: 'Porcentaje canal empresarial',
    legacyPct: 'Porcentaje conversación general',
    latencyTitle: 'Latencia de respuesta',
    topQueries: 'Consultas más frecuentes',
    topDomains: 'Dominios más consultados',
    heroTitle: 'Por qué esta arquitectura es más rápida y eficiente',
    heroSubtitle:
      'Menos latencia, menos unidades de procesamiento y menos dependencia del modelo generativo en consultas empresariales rutinarias.',
    smartSavingsTitle: 'Ahorro inteligente',
    smartSavingsSubtitle: 'Comparativa entre arquitectura tradicional y arquitectura Olnatura.',
    traditionalArchitecture: 'Arquitectura tradicional',
    olnaturaArchitecture: 'Arquitectura Olnatura',
    savings: 'Ahorro',
    estimatedTraditionalTime: 'Tiempo estimado tradicional',
    actualOlnaturaTime: 'Tiempo real Olnatura',
    questionLabel: 'Pregunta',
    moreExamples: 'Más ejemplos',
    costOptimizationTitle: 'Optimización en consultas empresariales frecuentes',
    traditional: 'Tradicional',
    processingUnits: 'unidades de procesamiento',
    efficiencyIndicators: 'Indicadores de eficiencia',
    totalQueries: 'Consultas totales',
    deterministicQueries: 'Consultas determinísticas',
    generativeQueries: 'Consultas generativas',
    estimatedSavings: 'Ahorro estimado',
    averageTime: 'Tiempo promedio',
    responseToUser: 'Respuesta al usuario',
    tokensSaved: 'Unidades de procesamiento ahorradas',
    estimatedCostAvoided: 'Costo evitado estimado',
    llmCallsAvoided: 'Llamadas evitadas al modelo de lenguaje',
    localMetricsEyebrow: 'Métricas locales frontend',
    platformPerformanceTitle: 'Rendimiento de la plataforma',
    localMetricsSubtitle: 'Métricas locales frontend · sesión + benchmark contra /api/chat',
    measuring: 'Midiendo…',
    architecturalEyebrow: 'Explicación arquitectónica',
    architecturalTitle: 'Cómo funciona la eficiencia de la plataforma',
    whyFaster: '¿Por qué es más rápido?',
    whyFasterBody:
      'Las consultas empresariales frecuentes se resuelven con tablas resumen pre-calculadas y KPIs materializados. No es necesario recorrer millones de registros ni esperar la generación del modelo en cada interacción.',
    whyLessTokens: '¿Por qué consume menos unidades de procesamiento?',
    whyLessTokensBody:
      'El motor determinístico responde con plantillas verificadas cuando la intención es conocida. El modelo local solo interviene en preguntas interpretativas, abiertas o ejecutivas que requieren síntesis narrativa.',
    whyNotAllLlm: '¿Por qué no se envía todo al modelo de lenguaje?',
    whyNotAllLlmBody:
      'Enviar cada pregunta al modelo implica latencia, variabilidad y costo. La arquitectura clasifica primero, extrae entidades y decide si los datos ya existen en la capa ejecutiva antes de activar IA generativa.',
    whyIntermediateLayers: '¿Por qué existen capas intermedias?',
    whyIntermediateLayersBody:
      'Capa de lenguaje natural, extracción de entidades, enrutador de intención y capa de resumen ejecutivo traducen lenguaje natural en consultas estructuradas. Es la misma lógica que usan asistentes empresariales: entender antes de generar.',
    metricNarratives: {
      totalQueries: 'Volumen de interacción empresarial',
      deterministicQueries: 'Resueltas sin invocar IA generativa',
      generativeQueries: 'Interpretación y síntesis ejecutiva',
      averageTime: 'Respuesta percibida por el usuario',
      tokensSaved: 'Consumo evitado frente a arquitectura tradicional',
      estimatedCostAvoided: 'Impacto económico proyectado',
      llmCallsAvoided: 'Consultas resueltas con datos verificados',
    },
  },
  executiveSummary: {
    title: 'Resumen de la respuesta',
    channel: 'Canal utilizado',
    channelTooltip: 'Ruta por la que el sistema resolvió su consulta.',
    confidence: 'Nivel de confianza',
    confidenceTooltip: 'Grado de certeza asociado a la evidencia y al método de respuesta.',
    evidence: 'Evidencia utilizada',
    evidenceTooltip: 'Fuentes, tipo de consulta o paquete de evidencia que sustentan la respuesta.',
    limitations: 'Limitaciones',
    limitationsTooltip: 'Restricciones o vacíos que deben considerarse al tomar decisiones.',
    responseTime: 'Tiempo de respuesta',
    responseTimeTooltip: 'Duración total percibida para entregar la respuesta.',
  },
  chat: {
    pipeline: 'Canal',
    queryType: 'Tipo de consulta',
    confidence: 'Confianza',
    mode: 'Modo',
    intent: 'Intención detectada',
    totalTime: 'Tiempo total',
    nlp: 'Procesamiento de lenguaje',
    entityExtraction: 'Extracción de entidades',
    router: 'Enrutador',
    deterministicEngine: 'Motor determinístico',
    llm: 'Modelo de lenguaje',
    tokens: 'Unidades de procesamiento estimadas',
    sources: 'Fuentes utilizadas',
    advancedInfo: 'Información avanzada',
    technicalInfo: 'Información técnica',
    sessionId: 'Identificador de sesión',
    pendingClarification: 'Aclaración pendiente',
    clarificationResolved: 'Aclaración resuelta',
  },
  export: {
    question: 'Pregunta',
    count: 'Cantidad',
    channel: 'Canal Utilizado',
    queryType: 'Tipo de consulta',
    coverageGapScore: 'Brecha de cobertura',
    exportedAt: 'Fecha de exportación',
    items: 'Registros',
  },
} as const

/** Traduce handled_by del API a etiqueta de negocio. */
export function translateHandledBy(value: string | null | undefined): string {
  if (!value) return '—'
  return HANDLED_BY_LABELS[value] ?? value
}

/** Traduce query_type del API. */
export function translateQueryType(value: string | null | undefined): string {
  if (!value) return '—'
  return QUERY_TYPE_LABELS[value] ?? value.replaceAll('_', ' ').toLowerCase()
}

/** Traduce dominio empresarial (métricas de fallback). */
export function translateDomain(value: string | null | undefined): string {
  if (!value) return '—'
  return DOMAIN_LABELS[value] ?? value
}

/** Traduce modo de respuesta legacy. */
export function translateResponseMode(value: string | null | undefined): string {
  if (!value) return '—'
  return RESPONSE_MODE_LABELS[value] ?? value
}

export function getMetricTooltip(key: keyof typeof METRIC_TOOLTIPS): string {
  return METRIC_TOOLTIPS[key]
}

/** Formatea unidades de procesamiento para comparativas de rendimiento. */
export function formatProcessingUnits(units: number): string {
  if (units === 0) return `0 ${es.performance.processingUnits}`
  if (units >= 1000) {
    return `~${(units / 1000).toFixed(1)}k ${es.performance.processingUnits}`
  }
  return `~${units} ${es.performance.processingUnits}`
}

const CSV_HEADER_MAP: Record<string, string> = {
  question: es.export.question,
  count: es.export.count,
  route: es.export.channel,
}

/** Localiza encabezados y valores de exportación CSV de brechas de cobertura. */
export function localizeCoverageGapsCsv(csv: string): string {
  const trimmed = csv.trim()
  if (!trimmed) return csv

  const lines = trimmed.split('\n')
  const headers = lines[0].split(',').map((h) => CSV_HEADER_MAP[h.trim()] ?? h.trim())
  const body = lines.slice(1).map((line) => {
    const parts = line.split(',')
    if (parts.length >= 3) {
      parts[2] = translateHandledBy(parts[2]?.trim())
    }
    return parts.join(',')
  })

  return [headers.join(','), ...body].join('\n')
}

/** Localiza claves de exportación JSON de brechas de cobertura. */
export function localizeCoverageGapsJson(jsonText: string): string {
  const data = JSON.parse(jsonText) as {
    items?: Array<{ question: string; count: number; route: string }>
    coverage_gap_score?: number
    exported_at?: string
  }

  const localized: Record<string, unknown> = {}
  if (data.items) {
    localized[es.export.items] = data.items.map((item) => ({
      [es.export.question]: item.question,
      [es.export.count]: item.count,
      [es.export.channel]: translateHandledBy(item.route),
    }))
  }
  if (data.coverage_gap_score !== undefined) {
    localized[es.export.coverageGapScore] = data.coverage_gap_score
  }
  if (data.exported_at) {
    localized[es.export.exportedAt] = data.exported_at
  }

  return JSON.stringify(localized, null, 2)
}

/** Patrones de inglés prohibidos en UI de negocio (validación automática). */
export const FORBIDDEN_ENGLISH_UI_PATTERNS: RegExp[] = [
  /\bOverview\b/i,
  /\bCoverage Gaps\b/i,
  /\bTop Failures\b/i,
  /\bTop Routes\b/i,
  /\bTop Queries\b/i,
  /\bTop Domains\b/i,
  /\bAdoption\b/i,
  /\bBusiness Analytics\b/i,
  /\bOperational Audit\b/i,
  /\bBusiness Pipeline\b/i,
  /\bLegacy Chat\b/i,
  /\bGuided Fallback\b/i,
  /\bCapability Discovery\b/i,
  /\bCoverage Score\b/i,
  /\bSuccess Rate\b/i,
  /\bExport JSON\b/i,
  /\bExport CSV\b/i,
  /\bhandled_by\b/i,
  /\bquery_type\b/i,
  /\bmetadata\b/i,
  /\bconfidence\b/i,
  /\bbusiness_pipeline\b/i,
  /\blegacy_chat\b/i,
]

export function containsForbiddenEnglish(text: string): string | null {
  for (const pattern of FORBIDDEN_ENGLISH_UI_PATTERNS) {
    const match = text.match(pattern)
    if (match) return match[0]
  }
  return null
}

/** Recopila cadenas de UI del catálogo para auditoría. */
export function collectLocalizedUiStrings(): string[] {
  const strings: string[] = []

  function walk(value: unknown): void {
    if (typeof value === 'string') strings.push(value)
    else if (Array.isArray(value)) value.forEach(walk)
    else if (value && typeof value === 'object') Object.values(value).forEach(walk)
  }

  walk(es)
  strings.push(...Object.values(HANDLED_BY_LABELS))
  strings.push(...Object.values(QUERY_TYPE_LABELS))
  strings.push(...Object.values(METRIC_TOOLTIPS))
  return strings
}

export function auditLocalizedCatalog(additionalStrings: string[] = []): string[] {
  const violations: string[] = []
  for (const text of [...collectLocalizedUiStrings(), ...additionalStrings]) {
    const forbidden = containsForbiddenEnglish(text)
    if (forbidden) violations.push(`${forbidden} en: ${text.slice(0, 60)}`)
  }
  return violations
}
