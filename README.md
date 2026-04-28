# Healthcare AI Triage — Curso de IA aplicada

Workflow de **triage clínico** construido en n8n self-hosted + OpenRouter. Tres clases progresivas: arrancás con un flujo simple, luego sumás prompting avanzado e ingesta, y finalmente pasás a un patrón de **RAG documental**.

> ⚠️ Proyecto educativo. No usar para decisiones clínicas reales.

---

## 🎓 ¿Recién arrancás?

Empezá por **[`conceptos/`](./conceptos/)** — 6 mini-workflows de 2-6 nodos, cada uno enseñando una idea por separado (webhooks, HTTP Request, LLM, few-shot, JSON schema, LlamaCloud, observabilidad + fallback). Cuando los entendés, pasás a `clase-1/`, `clase-2/` y `clase-3/` donde todo se integra.

---

## 📚 Estructura del repo

```
coder-ia/
├── conceptos/  → 6 mini-workflows pedagógicos (arrancá acá)
├── clase-1/    → Workflow base integrado (puerto 5678)
├── clase-2/    → Workflow avanzado integrado (puerto 5679)
├── clase-3/    → RAG documental + workflows parciales (puerto 5680)
└── clase-4/    → Parsing documental + RAG sin vector DB (puerto 5681)
```

- **`conceptos/`** usa el n8n de `clase-1/` — no necesita setup propio.
- **`clase-1/`**, **`clase-2/`**, **`clase-3/`** y **`clase-4/`** son auto-contenidas: cada una con su `docker-compose.yml`, `.env.example` o configuración propia, workflows y `README.md`. Conviven sin chocar.

---

## 🎯 Qué aprendés en cada clase

| Clase | Tema | Qué construís |
|-------|------|---------------|
| **1️⃣** | Fundamentos | Webhook → validación → búsqueda semántica → LLM → clasificación P1–P4 + fallback por reglas |
| **2️⃣** | Prompting avanzado + ingesta + observabilidad | Few-shot, JSON Schema validator, ingesta de PDFs via LlamaCloud, logs estructurados y alertas |
| **3️⃣** | RAG documental | Chunking, embeddings simulados, retrieval top-k, respuesta grounded con fuentes, guardrails y workflows parciales por etapa |
| **4️⃣** | Parsing documental + RAG aplicado | Ingesta documental declarativa, consulta RAG sin vector DB, integración con LlamaCloud y colección Postman propia |

### Diagrama mental

```
┌─────────── CLASE 1 ────────────┐   ┌─────────── CLASE 2 ────────────┐
                                      (todo lo de clase 1, más:)

  Webhook JSON                         + Webhook PDF → LlamaCloud
       ↓                               + Few-shot prompting
  Validar paciente                     + JSON Schema validator
       ↓                               + Log estructurado (latencia, tokens)
  Buscar protocolos                    + Alertas a webhook externo
       ↓
  LLM (Gemini 2.0 Flash)
       ↓
  Clasificar P1/P2/P3/P4
       ↓
  Notificar + responder
```

---

## 🛠️ Requisitos previos

- **Docker Desktop** corriendo
- Una **API key de [OpenRouter](https://openrouter.ai/keys)** (gratis para empezar)
- Una URL de **[webhook.site](https://webhook.site)** para ver notificaciones
- **Solo para clase 2:** API key de **[LlamaCloud](https://cloud.llamaindex.ai)** → API Keys → Generate New Key
- **Solo para clase 3, step 07:** API key de **[LlamaCloud](https://cloud.llamaindex.ai)** → API Keys → Generate New Key

---

## 🚀 Instalación rápida

### 1. Cloná el repo

```bash
git clone https://github.com/jeyzee23/coderia.git
cd coderia
```

### 2. Elegí la clase y arrancala

**Clase 1:**

```bash
cd clase-1
cp .env.example .env
# Editá .env con tus keys
docker compose up -d
```

Abrí → **http://localhost:5678**

**Clase 2:**

```bash
cd clase-2
cp .env.example .env
# Editá .env con tus keys
docker compose up -d
```

Abrí → **http://localhost:5679**

**Clase 3:**

```bash
cd clase-3
cp .env.example .env
# Editá .env con tus keys
docker compose up -d
```

Abrí → **http://localhost:5680**

**Clase 4:**

```bash
cd clase-4
docker compose up -d
```

Abrí → **http://localhost:5681**

### 3. Importá el workflow

1. Entrá a la URL de arriba y creá usuario owner.
2. **Workflows → Import from file →** `workflow.json` de la carpeta.
3. Activá con el toggle arriba a la derecha.

---

## 🧪 Probarlo

### Clase 1 (puerto 5678)

```bash
curl -X POST http://localhost:5678/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "P-001",
    "age": 67,
    "symptoms": "dolor toracico intenso con disnea",
    "vitals": { "bp": "180/110", "hr": 115, "spo2": 91 }
  }'
```

### Clase 2 (puerto 5679) — mismo endpoint, más info en la respuesta

```bash
curl -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "P-001",
    "age": 67,
    "symptoms": "dolor toracico intenso con disnea",
    "vitals": { "bp": "180/110", "hr": 115, "spo2": 91 }
  }'
```

### Clase 3 (puerto 5680) — RAG documental

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

### Postman

Cada clase trae su `postman_collection.json` con casos preparados cuando aplica. Clase 3 trae requests para el workflow padre y para los workflows parciales de RAG. Clase 4 trae una colección propia para parsing, ingesta y consulta RAG sobre documentos.

---

## 📁 Qué hay en cada archivo

```
clase-N/
├── docker-compose.yml       ← configuración del container de n8n
├── .env.example             ← template de variables (NO subir el .env real)
├── workflow.json            ← el workflow para importar a n8n
├── postman_collection.json  ← casos de prueba listos
└── README.md                ← documentación específica de la clase
```

Clase 2 suma `GUIA.md` (guía detallada del profesor) y `entregable-modelo.md` (ejemplo de entrega).

Clase 3 suma además `partials/` con el workflow padre partido por etapas.

Clase 4 suma además:

```
clase-4/
├── docker-compose.yml
├── postman_collection.json
├── partials/
│   ├── 09-ingesta-rag-sin-vector-db.json
│   ├── 10-rag-consulta-sin-vector-db.json
│   └── 11-llamacloud-rag-e2e.json
└── README.md
```

---

## 🧯 Troubleshooting

| Problema | Solución |
|----------|----------|
| "Port 5678/5679/5680 already in use" | Otro proceso ocupa el puerto. `docker ps` y bajá lo que sobra. |
| "workflow execution failed: unauthorized" | Revisá la `OPENROUTER_API_KEY` en `.env`. |
| La IA no responde o timeout | OpenRouter puede tardar en el primer request. Reintentá. |
| "schemaValid: false" en clase 2 | El LLM devolvió JSON malformado — el fallback por reglas responde igual. Es esperable. |
| En clase 2 el PDF da markdown vacío | El PDF dummy está pensado así. Usá un informe real para demo. |

### Comandos útiles

```bash
# Ver estado del container
docker ps

# Ver logs
docker logs -f n8n-dev          # clase 1
docker logs -f n8n-dev-c2       # clase 2
docker logs -f n8n-dev-c3       # clase 3

# Apagar
docker compose down

# Apagar y borrar todo (empezar de cero)
docker compose down -v
```

---

## 🔐 Seguridad

- **Nunca subas el `.env`** — ya está en `.gitignore`.
- Después de probar, **rotá las API keys** si las compartiste en chats o screenshots.
- Este proyecto es educativo: no lo conectes a datos reales de pacientes sin consultar con un DPO.

---

## 📖 Más info

- **Clase 1:** ver [clase-1/README.md](./clase-1/README.md)
- **Clase 2:** ver [clase-2/README.md](./clase-2/README.md) y [clase-2/GUIA.md](./clase-2/GUIA.md)
- **Clase 3:** ver [clase-3/README.md](./clase-3/README.md) y [clase-3/GUIA.md](./clase-3/GUIA.md)
- **Clase 4:** ver [clase-4/README.md](./clase-4/README.md)

---

## 📘 Glosario

- **Embedding → Representación vectorial**
  Vector numérico que representa el significado de un texto. Permite comparar por semántica, no por palabras.

- **Vector Space → Espacio vectorial**
  “Mapa” donde cada embedding es un punto. Cercanía = similitud conceptual.

- **Similarity / Distance → Similitud / Distancia**
  Mide qué tan parecidos son dos vectores. Más cerca = más similar (`cosine`, `euclidean`).

- **Chunking → Fragmentación**
  Dividir documentos en partes más pequeñas coherentes. Mejora la precisión en la búsqueda.

- **Parsing → Parseo / Estructuración**
  Convertir documentos (`PDF`, `DOCX`, etc.) a texto limpio y estructurado. Es la base del pipeline.

- **Retrieval → Recuperación**
  Buscar los fragmentos más relevantes para una consulta. Se basa en similitud vectorial.

- **RAG (Retrieval-Augmented Generation) → Generación aumentada con recuperación**
  Arquitectura que:
  1. Busca información relevante
  2. La pasa al modelo
  3. Genera una respuesta basada en eso

- **Vector Database → Base de datos vectorial**
  Base optimizada para almacenar embeddings y buscar por similitud. Ejemplos: `Chroma`, `Pinecone`.

- **Semantic Search → Búsqueda semántica**
  Búsqueda por significado, no por coincidencia textual.

- **Context → Contexto**
  Información que se le pasa al modelo para responder. En RAG: los chunks recuperados.

- **LLM (Large Language Model) → Modelo de lenguaje grande**
  Modelo que genera texto. No “sabe” por sí mismo: responde con el contexto que recibe.

- **Top-K → Número de resultados**
  Cantidad de fragmentos que se recuperan en la búsqueda. Balance entre precisión y cobertura.

- **Overlap → Solapamiento**
  Superposición entre chunks para no cortar ideas importantes.

- **Pipeline → Flujo de procesamiento**
  Cadena de pasos del sistema:
  `Parsing → Chunking → Embeddings → DB → Retrieval → LLM`

Dudas → preguntá en clase.
