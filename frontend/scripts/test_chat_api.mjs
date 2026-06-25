/**
 * Prueba de integración frontend → FastAPI /api/chat
 * Requiere backend en ejecución: uvicorn app.main:app --port 8001
 */
const API_BASE = process.env.VITE_API_BASE_URL ?? 'http://localhost:8001'

const TEST_QUESTIONS = [
  'Hola',
  '¿Quién eres?',
  '¿Qué KPIs tienes?',
  '¿Quién es nuestro mejor cliente?',
  '¿Qué pasó en junio?',
  '¿Cómo optimizas costos?',
]

async function testQuestion(question) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} para: ${question}`)
  }

  const data = await response.json()
  const preview = data.answer.replace(/\n/g, ' ').slice(0, 120)

  console.log(`[OK] ${question}`)
  console.log(`     intent=${data.intent} mode=${data.response_mode} conf=${data.intent_confidence}`)
  console.log(`     total_ms=${data.timings.total_ms} llm_ms=${data.timings.llm_ms}`)
  console.log(`     respuesta: ${preview}${data.answer.length > 120 ? '...' : ''}`)
  console.log('')
}

async function main() {
  console.log('='.repeat(72))
  console.log('TEST INTEGRACIÓN CHAT API')
  console.log(`Base URL: ${API_BASE}`)
  console.log('='.repeat(72))
  console.log('')

  let passed = 0
  for (const question of TEST_QUESTIONS) {
    try {
      await testQuestion(question)
      passed += 1
    } catch (error) {
      console.error(`[FAIL] ${question}`)
      console.error(`       ${error instanceof Error ? error.message : error}`)
      console.log('')
    }
  }

  console.log('='.repeat(72))
  console.log(`Resultado: ${passed}/${TEST_QUESTIONS.length} OK`)
  if (passed !== TEST_QUESTIONS.length) {
    process.exit(1)
  }
}

main()
