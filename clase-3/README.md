# Healthcare RAG Assistant — Clase 3

Clase 3 introduce el patrón **RAG (Retrieval-Augmented Generation)** con un enfoque pedagógico: un **workflow padre completo** y varios **workflows parciales** que muestran el mismo pipeline roto por etapas.

> ⚠️ Proyecto educativo. No usar para decisiones clínicas reales.

## Qué construye esta clase

- Un workflow padre de RAG documental en healthcare.
- 6 workflows parciales para ver el pipeline paso a paso.
- Búsqueda semántica **simulada** dentro de n8n para que el alumno entienda el mecanismo antes de conectar una base vectorial real.
- Respuesta grounded con fuentes, guardrails, fallback seguro y log estructurado.

## Idea central

En vez de mandar toda una base documental a la LLM:

1. partimos documentos en `chunks`
2. representamos cada chunk con un embedding simulado
3. recuperamos los `top-k` mas relevantes
4. solo esos fragmentos entran al prompt
5. la LLM sintetiza y cita fuentes

## Arquitectura del workflow padre

```text
Webhook consulta
  -> Validar input
  -> Base documental simulada
  -> Chunking semantico
  -> Embeddings simulados
  -> Retrieval top-k
  -> IF evidencia suficiente
       -> OpenRouter grounded
       -> Parse + validar salida
       -> Guardrails / fallback
  -> Log estructurado
  -> Respuesta final
```

## Setup

Clase 3 corre en **puerto 5680**, asi que convive con clase 1 (`5678`) y clase 2 (`5679`).

```bash
cd clase-3
cp .env.example .env
# completar OPENROUTER_API_KEY
# LLAMA_CLOUD_API_KEY solo si vas a usar el step 07

docker compose up -d
```

n8n queda en **http://localhost:5680**.

## Importar workflows

### Workflow padre

1. Abrir `http://localhost:5680`
2. Crear usuario owner
3. `Workflows -> Import from file -> workflow.json`
4. Activar el workflow

### Workflows parciales

Podés importar cualquiera desde `clase-3/partials/`.

Orden sugerido:

1. `01-chunking.json`
2. `02-embeddings-simulados.json`
3. `03-retrieval-topk.json`
4. `04-generation-with-sources.json`
5. `05-guardrails-fallback-logs.json`
6. `06-rag-completo.json`
7. `07-ingesta-llamacloud-opcional.json`

## Qué necesita cada workflow

| Workflow | Requiere API externa |
|---|---|
| `01` chunking | No |
| `02` embeddings simulados | No |
| `03` retrieval | No |
| `04` generation | Sí, OpenRouter |
| `05` guardrails + logs | No |
| `06` workflow padre | Sí, OpenRouter |
| `07` LlamaCloud opcional | Sí, LlamaCloud |

## Cómo se conectan entre si

La idea es que todos compartan un contrato de datos simple:

| Paso | Input | Output |
|---|---|---|
| `01` | `documents[]` | `chunks[]` |
| `02` | `chunks[]` | `embeddedChunks[]` |
| `03` | `question + embeddedChunks[]` | `retrievedChunks[] + retrieval` |
| `04` | `question + retrievedChunks[]` | `draftResponse` |
| `05` | `draftResponse + retrievedChunks[]` | respuesta final segura + `log` |
| `06` | todo junto | respuesta final |
| `07` | `pdfUrl` | `documents[]` |

Los parciales funcionan solos porque, si no reciben input previo, cargan un dataset demo por defecto.

## Probar el workflow padre

```bash
curl -X POST http://localhost:5680/webhook/rag-clinical-query \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?",
    "topK": 4,
    "scope": "prospectos",
    "patientContext": { "age": 68, "sex": "masculino" }
  }'
```

## Probar parciales

### Step 01 — chunking

```bash
curl -X POST http://localhost:5680/webhook/rag-step-01-chunking \
  -H 'Content-Type: application/json' \
  -d '{}'
```

### Step 03 — retrieval

```bash
curl -X POST http://localhost:5680/webhook/rag-step-03-retrieval \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?",
    "scope": "prospectos"
  }'
```

### Step 05 — guardrails

```bash
curl -X POST http://localhost:5680/webhook/rag-step-05-guardrails \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?"
  }'
```

### Step 07 — LlamaCloud opcional

```bash
curl -X POST http://localhost:5680/webhook/rag-step-07-llamacloud-ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "pdfUrl": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
  }'
```

## Postman

Importar `postman_collection.json`.

Trae:

- 2 requests para el workflow padre
- 5 requests de parciales
- 1 request opcional para LlamaCloud

Si querés verlos animados en el canvas, cambiá `/webhook/` por `/webhook-test/` y corré primero **Execute workflow** en n8n.

## Estructura

```text
clase-3/
├── docker-compose.yml
├── .env.example
├── workflow.json
├── postman_collection.json
├── README.md
├── GUIA.md
├── entregable-modelo.md
├── partials/
│   ├── 01-chunking.json
│   ├── 02-embeddings-simulados.json
│   ├── 03-retrieval-topk.json
│   ├── 04-generation-with-sources.json
│   ├── 05-guardrails-fallback-logs.json
│   ├── 06-rag-completo.json
│   └── 07-ingesta-llamacloud-opcional.json
└── scripts/
    └── generate_assets.py
```

## Notas de seguridad

- El sistema devuelve **busqueda documental con trazabilidad**, no diagnostico.
- `requiresHumanReview` queda pensado como freno natural para un flujo de healthcare.
- El dataset es simulado y chico a proposito: el objetivo es entender el patrón, no la cobertura clínica real.
- Si usás el step 07, el documento sale de tu infraestructura y viaja a LlamaCloud.
