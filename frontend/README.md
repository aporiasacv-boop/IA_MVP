# IA_MVP Frontend — Olnatura Intelligence

Interfaz ejecutiva de Inteligencia Empresarial para Olnatura.

## Stack

- React 19 · TypeScript · Vite · TailwindCSS 4 · React Router

## Ejecución local

**Backend** (puerto 8001):

```powershell
cd ..
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

**Frontend**:

```powershell
npm install
npm run dev
```

Abrir: http://localhost:5173

En desarrollo, Vite hace **proxy** de `/api` hacia el backend.

## Variables de entorno

```env
VITE_API_BASE_URL=http://localhost:8001
```

## Pantallas activas (16)

| Ruta | Pantalla |
|------|----------|
| `/` | Asistente IA |
| `/rendimiento` | Rendimiento |
| `/analytics` | Analítica Empresarial |
| `/audit` | Auditoría Operacional |
| `/entidades` | Entidades Empresariales |
| `/canonicas` | Identidad Canónica |
| `/perfiles` | Perfiles de Comportamiento |
| `/ontologia` | Ontología Empresarial |
| `/conocimiento` | Servicio de Conocimiento |
| `/objetos-conocimiento` | Objetos EKO |
| `/razonamiento` | Razonamiento Empresarial |
| `/intencion-semantica` | Intención Semántica |
| `/evidencia` | Paquete de Evidencia |
| `/simulador` | Simulador |
| `/centro-decisiones` | Centro de Decisiones |
| `/finops` | FinOps |

Alias de compatibilidad: `/costos-ia` → FinOps.

## Localización

Toda etiqueta visible proviene de `src/i18n/spanish.ts`.

## Tests

```powershell
npm run test:api   # integración con backend
npm run test       # vitest unitarios
```

## Build

```powershell
npm run build
npm run preview
```
