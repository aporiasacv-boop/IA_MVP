# IA_MVP Frontend

Interfaz ejecutiva de Inteligencia Empresarial para Olnatura.

## Stack

- React 19
- TypeScript
- Vite
- TailwindCSS 4
- React Router

## Ejecución local

**1. Backend** (puerto 8001):

```powershell
cd ..
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

**2. Frontend**:

```powershell
cd frontend
npm install
npm run dev
```

Abrir: http://localhost:5173

En desarrollo, Vite hace **proxy** de `/api` hacia el backend (`.env.development` usa URL vacía). En producción usar `VITE_API_BASE_URL` en `.env`.

## Variables de entorno

```env
VITE_API_BASE_URL=http://localhost:8001
```

Copiar desde `.env.example`.

## Prueba de integración API

Con el backend en ejecución:

```powershell
npm run test:api
```

## Build de producción

```powershell
npm run build
npm run preview
```

## Vistas

1. **Asistente IA** — conversación empresarial con respuestas protagonistas
2. **Rendimiento** — métricas de optimización determinística vs generativa

## Notas

- Datos mock integrados (sin conexión al backend por ahora)
- Diseño inspirado en ChatGPT Enterprise, Claude y Microsoft Copilot
- Identidad visual Olnatura con verde corporativo
