# Healthcare AI Triage — Clase 2

Extensión del workflow de [clase-1](../clase-1/) con parametrización avanzada, ingesta vía **LlamaCloud**, validación formal de **output schema** y **observabilidad** (logs estructurados + alertas).

> ⚠️ Proyecto educativo. No usar para decisiones clínicas reales.

## Qué cambia vs clase 1

| Dimensión | Clase 1 | Clase 2 |
|---|---|---|
| Parametrización LLM | `temperature: 0.2` | `temperature: 0.2` + `top_p: 0.9` + **few-shot (2 ejemplos)** |
| Output schema | Solo instrucciones en prompt + parser tolerante | **Validator formal** (JSON Schema manual) + rama explícita al fallback si no cumple |
| Ingesta | Webhook JSON | Webhook JSON **+ webhook PDF** (LlamaCloud → markdown → extracción) |
| Fallback | IA falla → reglas | IA falla **o schema falla** → reglas (con `fallbackReason` en el log) |
| Observabilidad | Ejecuciones de n8n | **Log JSON estructurado** con latencia, tokens, schemaValid + **alerta** a webhook externo |

## Arquitectura

```
[Webhook JSON] ──────────────────────────────┐
                                              ├→ Validar Input → IF válido
[Webhook PDF]                                 │       ├→ (sí) → Búsqueda Semántica
     ↓                                        │       └→ (no) → Respuesta Error
  LlamaCloud Upload                           │
     ↓                                        │
  Wait 8s                                     │
     ↓                                        │
  GET Markdown                                │
     ↓                                        │
  Extraer Campos ─────────────────────────────┘

Búsqueda Semántica → OpenRouter (few-shot + top_p)
   → IF IA OK
        ├→ Parse → Validar Schema → IF Schema OK
        │             ├→ (sí) → Normalizar → Clasificación Riesgo
        │             └→ (no) → Fallback Reglas ──┐
        └→ Fallback Reglas ───────────────────────┤
                                                  ↓
                                          Clasificación Riesgo
                                                  ↓
                                          Log Estructurado
                                                  ↓
                                          IF ¿Alerta?
                                            ├→ (sí) → Enviar Alerta ─┐
                                            └→ (no) ─────────────────┤
                                                                     ↓
                                                              Notificación
                                                                     ↓
                                                              Respuesta OK
```

## Setup

Clase 2 corre en **puerto 5679** con volumen propio, así que convive con clase-1 (que usa 5678) sin chocar.

```bash
cd clase-2
cp .env.example .env
# Editar .env con:
#   - N8N_ENCRYPTION_KEY: generar con `openssl rand -hex 32`
#   - OPENROUTER_API_KEY: https://openrouter.ai/keys
#   - NOTIFICATION_WEBHOOK_URL: https://webhook.site
#   - ALERT_WEBHOOK_URL: puede ser el mismo que el anterior
#   - LLAMA_CLOUD_API_KEY: https://cloud.llamaindex.ai → API Keys

docker compose up -d
```

n8n queda en **http://localhost:5679**.

### Importar el workflow

1. Abrir http://localhost:5679, crear usuario owner.
2. **Workflows → Import from file →** `workflow.json`.
3. Activar el workflow (toggle arriba a la derecha).

No hace falta crear credentials en la UI — el workflow consume `$env.OPENROUTER_API_KEY` y `$env.LLAMA_CLOUD_API_KEY` directo desde docker-compose.

## Probar

### Con curl (JSON)

```bash
curl -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "P-2024-001",
    "age": 67,
    "symptoms": "dolor toracico intenso con disnea",
    "vitals": { "bp": "180/110", "hr": 115, "spo2": 91 }
  }'
```

### Con curl (PDF)

```bash
curl -X POST http://localhost:5679/webhook/patient-analysis-pdf \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "P-2024-PDF-001",
    "pdfUrl": "https://URL_PUBLICA_DE_TU_INFORME.pdf"
  }'
```

Para smoke test podés usar `https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf` — va a parsear pero el markdown sale casi vacío y el flujo cae al fallback (útil para ver cómo responde el sistema a datos pobres).

### Con Postman

Importar `postman_collection.json`. Trae tres carpetas:

- **JSON producción** (`/webhook`) — requiere workflow Active.
- **JSON test** (`/webhook-test`) — apretar "Execute workflow" antes de cada request, anima el canvas.
- **PDF LlamaCloud** — smoke test + placeholder para URL real.

Incluye tests automáticos para P1/P4, override por vitales, error 400, y validación del log/schemaValid.

## Verificar logging y alertas

### Logs estructurados

El log JSON aparece **en la respuesta HTTP del webhook** bajo el campo `log`, así que se puede inspeccionar directamente:

```bash
curl -s -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"X","age":67,"symptoms":"dolor toracico","vitals":{"spo2":91}}' \
  | jq .log
```

En producción este mismo JSON se enviaría a Loki/Datadog/CloudWatch con un HTTP request adicional (el `console.log` del Code node no llega a `docker logs` porque n8n 1.x corre los Code nodes en un task runner separado).

Cada ejecución produce:

```json
{
  "event": "triage_completed",
  "ts": "2026-04-21T19:05:12.345Z",
  "patientHash": "hash_xxx",
  "priority": "P1_CRITICAL",
  "urgency": "critica",
  "slaMinutes": 5,
  "latencyMs": 1243,
  "tokensUsed": 312,
  "fallbackUsed": false,
  "fallbackReason": null,
  "schemaValid": true,
  "schemaErrors": [],
  "overrideApplied": false,
  "inputSource": "webhook-json",
  "source": "openrouter-gemini-2.0-flash"
}
```

### Alertas

Llegan al `ALERT_WEBHOOK_URL` (visible en webhook.site) cuando:

- `fallbackUsed = true` (IA o schema fallaron)
- `latencyMs > 8000` (procesamiento lento)
- `triage.overrideApplied = true` (vitales forzaron escalar)

El payload de alerta incluye el array `reasons` con los disparadores que se activaron.

## Estructura

```
.
├── docker-compose.yml       # n8n en puerto 5679, volumen propio
├── .env.example             # template con 5 variables
├── workflow.json            # workflow completo con todas las extensiones
├── postman_collection.json  # tests JSON + PDF
└── README.md
```

## Notas sobre privacidad (adicionales a clase 1)

Al habilitar la rama PDF, el archivo sale de nuestra infra y viaja a LlamaCloud (LlamaIndex Inc.). Implicancias:

- **Transferencia internacional de datos**: los servidores de LlamaCloud están en US por default. Para producción clínica en AR/UE habría que evaluar un **BAA** con el proveedor o usar **LlamaParse self-hosted**.
- **Retención**: LlamaCloud retiene los documentos parseados un tiempo configurable. En datos reales conviene borrarlos por API apenas terminás el parseo.
- **PII en markdown**: el campo `_pdfMarkdownPreview` expone los primeros 400 chars del documento — en producción filtrá antes de loguear.

Normativas aplicables (AR): Ley 26.529 (Derechos del Paciente), Ley 25.326 (Protección Datos Personales), Resolución 189/2018 MSAL.

## Actividades para alumnos

1. Correr el workflow con al menos 3 casos clínicos distintos (uno por prioridad P1–P4).
2. Forzar un caso de **schema inválido** bajando `max_tokens` a 50 (la IA corta el JSON a mitad y el validator lo rechaza) — verificar que la alerta llega.
3. Subir un PDF clínico real a un storage público, disparar la rama PDF y comparar el triage con el JSON equivalente.
4. Documentar las métricas del `TRIAGE_LOG` durante 10 ejecuciones: latencia promedio, p95, tasa de fallback, tokens consumidos.
5. Proponer un dashboard mínimo (Grafana / Metabase / NotebookLM) que consuma esos logs.

## Laboratorio complementario: NotebookLM / Google AI Studio

El temario de la unidad 4 sugiere explorar herramientas de experimentación:

- **Google AI Studio** ([aistudio.google.com](https://aistudio.google.com/)) — pegar el prompt del nodo OpenRouter y probar cómo cambia la salida con `temperature 0.0` / `0.5` / `1.0` manteniendo `top_p=0.9`. Observar en qué punto la IA empieza a salirse del formato JSON.
- **NotebookLM** ([notebooklm.google.com](https://notebooklm.google.com/)) — cargar los 6 protocolos clínicos del nodo "Búsqueda Semántica" como sources y preguntarle al notebook qué documento recomienda para cada caso de prueba. Comparar contra la búsqueda semántica simulada del workflow.

Estos laboratorios no requieren código y sirven para **intuición clínica** antes de ajustar el pipeline.
