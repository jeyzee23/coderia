# Healthcare AI Triage — n8n + OpenRouter

Actividad práctica de automatización con IA. Workflow de **triage clínico preliminar** corriendo en n8n self-hosted que combina búsqueda semántica, análisis por LLM y una política de fallback determinista.

> ⚠️ Proyecto educativo. No usar para decisiones clínicas reales.

## Arquitectura

```
Webhook → Validar & anonimizar → Búsqueda semántica (embeddings simulados)
  → OpenRouter (Gemini 2.0 Flash) ──┐
                                    ├→ Clasificación (P1–P4 + SLA) → Notificación → Respuesta
  → Fallback reglas (si falla IA) ──┘
```

Decisiones clave:

- **Hashing de `patientId`** antes de propagar — no se logea PII identificable.
- **Retry 3× + timeout 10s + `continueOnFail`** en la llamada al LLM.
- **Parser robusto** que tolera markdown fences o texto extra alrededor del JSON.
- **Override por vitales críticos**: SpO2 < 92, HR < 50 o > 110, TA sistólica > 170, temp ≥ 39 → fuerza prioridad mínima P2 aunque la IA diga menos.
- **Clasificación final**: P1 (5 min) / P2 (30 min) / P3 (2 h) / P4 (24 h).

## Stack

- **n8n** self-hosted vía Docker Compose
- **OpenRouter** → `google/gemini-2.0-flash-001`
- **Postman** para pruebas

## Requisitos

- Docker Desktop
- Una API key de [OpenRouter](https://openrouter.ai/keys)
- (Opcional) URL de [webhook.site](https://webhook.site) para ver las notificaciones

## Setup

```bash
git clone git@github.com:jeyzee23/coderia.git
cd coderia

cp .env.example .env
# Editar .env con tus valores reales:
#   - N8N_ENCRYPTION_KEY: generar con `openssl rand -hex 32`
#   - OPENROUTER_API_KEY: tu key de OpenRouter
#   - NOTIFICATION_WEBHOOK_URL: tu URL de webhook.site

docker compose up -d
```

n8n queda en http://localhost:5678.

### Importar el workflow

1. Abrir http://localhost:5678, crear el usuario owner.
2. **Workflows → Import from file →** `workflow.json` (o `index.json`, son equivalentes; `index.json` es la versión que usa `$env.NOTIFICATION_WEBHOOK_URL` directo desde docker-compose).
3. En el nodo **🤖 Análisis IA (OpenRouter)**: crear credential **Header Auth** con
   - Name: `Authorization`
   - Value: `Bearer sk-or-v1-...` (tu key)
4. Activar el workflow (toggle arriba a la derecha).

## Probar

### Con curl

```bash
curl -X POST http://localhost:5678/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "P-2024-001",
    "age": 67,
    "symptoms": "dolor toracico intenso con disnea",
    "vitals": { "bp": "180/110", "hr": 115, "spo2": 91 }
  }'
```

### Con Postman

Importar `postman_collection.json`. Trae dos carpetas:

- **Producción (`/webhook`)** — requiere workflow Active. Corre en background, resultado visible en la tab **Executions** del editor.
- **Test (`/webhook-test`)** — apretar **"Execute workflow"** en el editor *antes de cada request*. Anima el canvas nodo por nodo.

Incluye casos para P1/P2/P3/P4, override por vitales, y error 400.

## Estructura

```
.
├── docker-compose.yml       # n8n self-hosted con envs desde .env
├── .env.example             # template de variables
├── workflow.json            # versión con webhook.site hardcodeado
├── index.json               # versión que lee NOTIFICATION_WEBHOOK_URL de env
├── postman_collection.json  # tests Postman (producción + test)
└── README.md
```

## Notas sobre privacidad

Para producción real habría que sumar:

- Filtro de PII antes de mandar al LLM (o usar Azure OpenAI / Vertex AI con BAA).
- Encriptación de campos sensibles en tránsito dentro del flujo.
- Consentimiento informado del paciente.
- Comité de ética / DPO validando el uso clínico.
- Versionado y explicabilidad de las decisiones.

Normativas aplicables (AR): Ley 26.529 (Derechos del Paciente), Ley 25.326 (Protección Datos Personales), Resolución 189/2018 MSAL.
