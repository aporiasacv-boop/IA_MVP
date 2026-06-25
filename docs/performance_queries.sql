-- Dashboard SQL para observabilidad v1
-- Tabla: performance_metrics

-- Top preguntas
SELECT
    question,
    COUNT(*) AS count
FROM performance_metrics
GROUP BY question
ORDER BY count DESC, question ASC
LIMIT 20;

-- Tiempo promedio total y por etapa
SELECT
    COUNT(*) AS total_requests,
    ROUND(AVG(total_time_ms)::numeric, 2) AS avg_total_time_ms,
    ROUND(AVG(intent_time_ms)::numeric, 2) AS avg_intent_time_ms,
    ROUND(AVG(planner_time_ms)::numeric, 2) AS avg_planner_time_ms,
    ROUND(AVG(executor_time_ms)::numeric, 2) AS avg_executor_time_ms,
    ROUND(AVG(database_time_ms)::numeric, 2) AS avg_database_time_ms,
    ROUND(AVG(response_time_ms)::numeric, 2) AS avg_response_time_ms,
    ROUND(AVG(legacy_chat_time_ms)::numeric, 2) AS avg_legacy_chat_time_ms,
    ROUND(AVG(ollama_time_ms)::numeric, 2) AS avg_ollama_time_ms
FROM performance_metrics;

-- Pipeline vs Legacy
SELECT
    handled_by,
    COUNT(*) AS requests,
    ROUND(AVG(total_time_ms)::numeric, 2) AS avg_total_time_ms,
    ROUND(AVG(database_time_ms)::numeric, 2) AS avg_database_time_ms
FROM performance_metrics
GROUP BY handled_by
ORDER BY requests DESC;

-- Consultas mas lentas
SELECT
    request_id,
    question,
    handled_by,
    query_type,
    total_time_ms,
    database_time_ms,
    ollama_time_ms,
    success,
    created_at
FROM performance_metrics
ORDER BY total_time_ms DESC
LIMIT 50;

-- Percentiles de latencia total
SELECT
    ROUND(
        percentile_cont(0.50) WITHIN GROUP (ORDER BY total_time_ms)::numeric,
        2
    ) AS p50_total_time_ms,
    ROUND(
        percentile_cont(0.95) WITHIN GROUP (ORDER BY total_time_ms)::numeric,
        2
    ) AS p95_total_time_ms,
    ROUND(
        percentile_cont(0.99) WITHIN GROUP (ORDER BY total_time_ms)::numeric,
        2
    ) AS p99_total_time_ms
FROM performance_metrics;
