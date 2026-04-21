# Guía completa — Clase 2

## TL;DR

Partiste de **clase-1** (workflow de triage clínico funcional en n8n). Agregamos **clase-2/** que extiende ese workflow con los 3 temas del temario de la semana 1 sesión 2:

| Tema del temario | Qué se implementó |
|---|---|
| Parametrización avanzada | `top_p: 0.9`, **few-shot** con 2 ejemplos, **JSON Schema validator** formal |
| Ingesta de documentos | **Rama PDF** → LlamaCloud → Markdown → extracción → converge con rama JSON |
| Observabilidad | **Log estructurado** (JSON con latencia/tokens/schemaValid) + **alerta** a webhook si fallback/latencia/override |

Todo probado end-to-end. Container corriendo en http://localhost:5679.

---

## Estructura del proyecto

```
coder-ia/
├── clase-1/                    # Workflow base (puerto 5678)
│   ├── docker-compose.yml
│   ├── .env / .env.example
│   ├── workflow.json           # Workflow original
│   ├── postman_collection.json
│   └── README.md
│
└── clase-2/                    # Extensión (puerto 5679)
    ├── docker-compose.yml      # n8n-dev-c2, volumen propio
    ├── .env / .env.example     # +ALERT_WEBHOOK_URL +LLAMA_CLOUD_API_KEY
    ├── workflow.json           # Workflow extendido (26 nodos)
    ├── postman_collection.json # Tests JSON + PDF
    ├── README.md               # Diff vs clase-1, setup, observabilidad
    ├── entregable-modelo.md    # Doc 4-5 páginas — referencia para alumnos
    └── GUIA.md                 # Este documento
```

Conviven sin chocar: **clase-1 usa puerto 5678**, **clase-2 usa 5679**. Cada una tiene su propio volumen Docker.

---

## Cómo levantarlo desde cero

### 1. Pre-requisitos

- Docker Desktop corriendo
- Una key de [OpenRouter](https://openrouter.ai/keys)
- Una key de [LlamaCloud](https://cloud.llamaindex.ai) → API Keys → Generate New Key
- Una URL de [webhook.site](https://webhook.site) para recibir notificaciones y alertas

### 2. Setup

```bash
cd /Users/juancavidela/Desktop/coder-ia/clase-2
cp .env.example .env
# Editar .env con tus 5 valores reales (ya están cargados si es tu máquina)

docker compose up -d
```

Eso crea el container `n8n-dev-c2` en puerto 5679.

### 3. Importar y activar el workflow

**Opción A — via CLI** (la que usamos):
```bash
docker cp workflow.json n8n-dev-c2:/tmp/workflow.json
docker exec n8n-dev-c2 n8n import:workflow --input=/tmp/workflow.json
docker exec n8n-dev-c2 n8n publish:workflow --id=healthcare-triage-c2
docker compose restart
```

**Opción B — via UI** (más didáctico para la clase):
1. Abrir http://localhost:5679
2. Crear usuario owner (la primera vez)
3. Workflows → Import from file → `clase-2/workflow.json`
4. Activar con el toggle arriba a la derecha

### 4. Verificar que está vivo

```bash
curl -s http://localhost:5679/healthz
# → {"status":"ok"}
```

---

## Cómo probarlo (4 escenarios)

### Escenario 1 — P1 crítico (IA + few-shot + schema OK)

```bash
curl -s -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "DEMO-P1",
    "age": 67,
    "symptoms": "dolor toracico intenso opresivo con disnea e irradiacion a brazo izquierdo",
    "vitals": { "bp": "180/110", "hr": 115, "spo2": 91 }
  }' | jq
```

**Qué observar**: `priority: P1_CRITICAL`, `schemaValid: true`, `fallbackUsed: false`, `log.latencyMs` ~2000-5000ms.

### Escenario 2 — P4 leve (flujo normal, baja prioridad)

```bash
curl -s -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "DEMO-P4",
    "age": 32,
    "symptoms": "dolor de garganta leve, congestion nasal, sin fiebre",
    "vitals": { "hr": 72, "spo2": 98 }
  }' | jq
```

**Qué observar**: `priority: P4_LOW`, `slaMinutes: 1440` (24h). El few-shot guía al modelo a replicar el ejemplo P4 del prompt.

### Escenario 3 — Override por vitales críticos (red de seguridad)

```bash
curl -s -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "DEMO-OVR",
    "age": 28,
    "symptoms": "apenas una pequeña molestia al respirar",
    "vitals": { "bp": "185/100", "hr": 118, "spo2": 88 }
  }' | jq
```

**Qué observar**: aunque el síntoma suena leve, `hasCriticalVitals: true` y la prioridad queda al menos P2. Si el modelo infraestima la urgencia, `overrideApplied` se vuelve `true`.

### Escenario 4 — PDF via LlamaCloud

```bash
curl -s -X POST http://localhost:5679/webhook/patient-analysis-pdf \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "DEMO-PDF",
    "pdfUrl": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
  }' | jq
```

**Qué observar**: `log.inputSource: pdf-llamacloud`, el flujo tarda ~13s (incluye los 8s de Wait + parsing). Para demo más vistosa, reemplazá la URL por un informe clínico público real.

### Forzar fallback por schema inválido (avanzado)

Editá temporalmente el nodo `🤖 Análisis IA` y cambiá `max_tokens: 500` a `max_tokens: 30`. La respuesta del LLM se corta a mitad → JSON inválido → schema falla → el flujo rutea al fallback. En la respuesta vas a ver `fallbackUsed: true`, `fallbackReason: "schema-invalid"`.

---

## Cómo entenderlo a fondo

### El flujo en una oración

> Recibo datos del paciente (por JSON o por PDF), busco protocolos relevantes, pido análisis al LLM con ejemplos few-shot, valido el JSON contra un schema, clasifico la prioridad con override por vitales, logueo la métrica y alerto si algo anda mal.

### Los 26 nodos organizados por capa

**Capa 1 — Ingesta (6 nodos)**
- `🩺 Webhook - Datos Paciente` + `📄 Webhook PDF` (2 entradas)
- `☁️ LlamaCloud Upload` → `⏳ Wait 8s` → `📥 Obtener Markdown` → `📝 Extraer Campos Markdown`
- Las dos ramas producen el mismo shape y convergen en `Validar Input`.

**Capa 2 — Validación y anonimización (3 nodos)**
- `✅ Validar Input` — hashea patientId, detecta vitales críticos, setea `startedAtMs` (para medir latencia)
- `❓ ¿Input válido?` + `❌ Respuesta de Error`

**Capa 3 — Análisis con IA (5 nodos)**
- `🔍 Búsqueda Semántica` — top-3 protocolos por similitud
- `🤖 Análisis IA (OpenRouter)` — **el nodo clave**. Tiene `temperature: 0.2`, `top_p: 0.9`, `max_tokens: 500`, y el prompt con 2 ejemplos few-shot
- `❓ ¿IA respondió OK?` — detecta si la llamada falló
- `📝 Parsear Respuesta IA` — extrae JSON tolerando markdown fences

**Capa 4 — Validación de contrato (3 nodos — nuevos vs clase-1)**
- `✅ Validar Output Schema` — chequea que el JSON tenga `analysis`, `urgency` (enum), `recommendedAction`, `differentialDiagnosis` (array)
- `❓ ¿Schema válido?` — branching explícito
- `🧩 Normalizar (OK)` — si pasó, arma el shape para el siguiente paso

**Capa 5 — Fallback (1 nodo)**
- `⚠️ Fallback (Reglas)` — se activa por 3 motivos: IA falló / JSON malformado / schema inválido. Registra el motivo en `fallbackReason`.

**Capa 6 — Clasificación (1 nodo)**
- `📊 Clasificación Riesgo` — aplica el scoring P1-P4 + SLA, con override por vitales.

**Capa 7 — Observabilidad (3 nodos — nuevos vs clase-1)**
- `📊 Log Estructurado` — calcula `latencyMs` (ahora - `startedAtMs`), arma el JSON de log, setea `shouldAlert`
- `❓ ¿Alerta?` — branching
- `🚨 Enviar Alerta` — POST al `ALERT_WEBHOOK_URL`

**Capa 8 — Salida (2 nodos)**
- `📨 Notificación` — POST al `NOTIFICATION_WEBHOOK_URL`
- `📤 Respuesta OK` — responde al cliente HTTP con el triage + el log

### Los 3 conceptos clave del temario (con referencia al código)

**1. Few-shot** → Nodo `🤖 Análisis IA (OpenRouter)`, dentro del campo `jsonBody`. El prompt incluye 2 ejemplos completos (input/output) antes del input real. Compará visualmente con `clase-1/workflow.json` mismo nodo — ahí es zero-shot.

**2. Output schema** → Nodo `✅ Validar Output Schema`. Es JSON Schema **manual en JS**, no una librería. Chequea 4 reglas. Si falla, agrega strings a `errors[]` y setea `schemaValid: false`. El siguiente nodo IF branchea basándose en ese bool.

**3. Observabilidad** → Nodo `📊 Log Estructurado`. Arma un objeto con 13 campos (timestamp, patientHash, priority, urgency, latencyMs, tokens, fallbackUsed, schemaValid, overrideApplied, etc.). En prod eso va a Loki/Datadog; acá sale en la respuesta HTTP.

### Qué cambió vs clase-1 (diff ejecutivo)

| Nodo | Estado |
|---|---|
| Webhook JSON | Idéntico |
| Validar Input | +`startedAtMs` + `inputSource` |
| Búsqueda Semántica | Idéntico |
| Análisis IA | +`top_p` + prompt few-shot |
| Parser AI | Separado en 2: parser puro + schema validator |
| Schema validator | **Nuevo** |
| Fallback Reglas | +`fallbackReason` + `schemaErrors` |
| Clasificación | Idéntico |
| Log Estructurado | **Nuevo** |
| IF Alerta | **Nuevo** |
| Enviar Alerta | **Nuevo** |
| Rama PDF completa | **Nueva** (5 nodos) |
| Notificación | +`schemaValid` + `latencyMs` en payload |

---

## Tips para dictar en vivo

### Secuencia sugerida (2 horas)

1. **(10 min) Repaso de clase-1** — correr un caso P1, mostrar la arquitectura.
2. **(20 min) Parametrización** — abrí el nodo `🤖 Análisis IA` en clase-2, mostrá `top_p: 0.9` y el few-shot. Compará con clase-1. Correr P1 y P4 y mostrar cómo el modelo imita los ejemplos.
3. **(15 min) Output Schema** — nodo `✅ Validar Output Schema`. Mostrar el código del validator. Forzar un caso donde falla bajando `max_tokens` a 30 en vivo y viendo el fallback activarse.
4. **(25 min) LlamaCloud** — explicar PDF → Markdown. Mostrar cada nodo de la rama (Upload, Wait, GET, Extract). Correr el caso PDF. Abrir la respuesta y comparar el markdown extraído con un PDF real.
5. **(20 min) Observabilidad** — mostrar el `log` en la respuesta HTTP, explicar cada campo. Mostrar webhook.site recibiendo la alerta cuando `fallbackUsed=true`. Hablar de métricas derivables (p95 latencia, tasa fallback, etc.).
6. **(15 min) Privacidad y regulación** — nota en el canvas + sección del entregable. Discutir transferencia internacional de datos con LlamaCloud.
7. **(15 min) Laboratorio** — NotebookLM + AI Studio. Mostrar cómo jugar con temperatura/top_p sin código.

### Casos "wow" para la clase

- **Bajar `max_tokens` en vivo a 30** → schema falla → flujo cae a fallback → alerta llega a webhook.site en tiempo real.
- **Correr P1 dos veces seguidas** → la respuesta es casi idéntica (temperature 0.2 en acción).
- **Cambiar `temperature` a 1.5** en el nodo → respuestas mucho más variadas entre runs (didáctico para mostrar el parámetro).
- **Cambiar el prompt a zero-shot** (borrar los ejemplos) → ver cómo aumenta la tasa de schema inválido.

### Gotchas conocidos (para no pisarte)

- **`console.log` no llega a `docker logs`** por los task runners de n8n 1.x. Mostrá el log directamente en la respuesta HTTP.
- **Primera request después de activar tarda más** (cold start del task runner). Hacé un warmup al principio de la clase.
- **LlamaCloud con PDFs grandes tarda > 8s**. El retry del `📥 Obtener Markdown` cubre hasta 15s más, pero si ves 400 repetidamente, subí el Wait a 15s.
- **El PDF dummy.pdf da markdown casi vacío** ("Dummy PDF file"). Para demo vistosa, tené preparada una URL de PDF clínico real.

---

## Qué es el few-shot (refresher)

**Few-shot** es una técnica de prompting donde le das al modelo **unos pocos ejemplos** de entrada/salida *dentro del mismo prompt*, antes de pedirle que procese el caso real. El modelo aprende el patrón imitando los ejemplos — sin re-entrenarlo.

- **Zero-shot**: 0 ejemplos. "Clasificá este texto como positivo o negativo: {texto}"
- **One-shot**: 1 ejemplo.
- **Few-shot**: 2-10 ejemplos. Lo que suele usarse en la práctica.

### Por qué funciona mejor que "explicar con palabras"

1. **Formato exacto**: el modelo copia el shape del JSON de los ejemplos, no "interpreta" tu descripción. Cae menos en devolver markdown fences o comentarios extra.
2. **Criterio clínico**: ante un caso ambiguo, el modelo se ancla al ejemplo más cercano. Si le mostraste que "SpO2 91 + dolor torácico = crítica", va a replicar ese criterio para casos parecidos.
3. **Escalas y tonos**: aprende implícitamente la longitud esperada del campo `analysis`, el estilo de `recommendedAction`, cuántos diferenciales devolver, etc.

### El trade-off

Cada ejemplo ocupa tokens del contexto → paga más por request y deja menos espacio para el input real. Regla empírica:

- **2-4 ejemplos** suele ser el sweet spot.
- Elegí ejemplos **que cubran los extremos** (un P1 y un P4) — el modelo interpola el medio.
- Si el modelo necesita > 10 ejemplos para entender, probablemente necesitás **fine-tuning**, no más few-shot.

---

## Comandos de referencia

```bash
# Arrancar
cd /Users/juancavidela/Desktop/coder-ia/clase-2
docker compose up -d

# Ver estado
docker ps --filter name=n8n-dev-c2

# Smoke tests rápidos
curl -s -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"T","age":67,"symptoms":"dolor toracico","vitals":{"spo2":91}}' | jq

# Ver logs generales del contenedor (no los TRIAGE_LOG, esos van en la respuesta HTTP)
docker logs -f n8n-dev-c2

# Re-importar workflow si lo modificás
docker cp workflow.json n8n-dev-c2:/tmp/workflow.json
docker exec n8n-dev-c2 n8n import:workflow --input=/tmp/workflow.json
docker exec n8n-dev-c2 n8n publish:workflow --id=healthcare-triage-c2
docker compose restart

# Apagar
docker compose down

# Apagar + borrar volumen (empieza de cero la próxima vez)
docker compose down -v
```

---

## Referencia rápida de archivos para la clase

| Si querés mostrar... | Abrí... |
|---|---|
| El workflow completo en el canvas | http://localhost:5679 |
| El código del few-shot prompt | `clase-2/workflow.json` → buscar `"🤖 Análisis IA"` |
| El código del schema validator | `clase-2/workflow.json` → buscar `"✅ Validar Output Schema"` |
| El formato del log estructurado | `clase-2/README.md` sección "Logs estructurados" |
| Documento modelo para alumnos | `clase-2/entregable-modelo.md` |
| Diff conceptual vs clase-1 | `clase-2/README.md` tabla "Qué cambia vs clase 1" |
| Lista de casos de prueba | `clase-2/postman_collection.json` — importar a Postman |

---

**Nota final**: después de la clase, **rotá la key de LlamaCloud** (`llx-...`) desde https://cloud.llamaindex.ai → API Keys. La escribiste en este chat, así que considerala semi-comprometida.
