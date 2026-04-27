# Guía completa — Clase 3

## TL;DR

`clase-3/` enseña **RAG documental** con dos niveles:

1. un **workflow padre** que hace el pipeline completo
2. varios **workflows parciales** que muestran el mismo flujo roto en etapas

La decisión pedagógica importante es esta: **todavía no hay vector DB real**. Todo el retrieval está simulado dentro de n8n para que el alumno vea el mecanismo sin sumar infraestructura ni caja negra demasiado temprano.

---

## Objetivo didáctico

Al terminar la clase, el alumno tiene que poder explicar:

1. por qué una LLM sola no alcanza para responder sobre una base documental viva
2. qué rol cumplen chunking, embeddings y retrieval
3. por qué la LLM aparece **después** del retrieval y no antes
4. por qué en healthcare hacen falta guardrails, trazabilidad y fallback

---

## Estructura del proyecto

```text
coder-ia/
├── clase-1/    # workflow base de triage
├── clase-2/    # prompting + PDF + schema + observabilidad
└── clase-3/    # RAG documental
    ├── workflow.json
    ├── postman_collection.json
    ├── README.md
    ├── GUIA.md
    ├── entregable-modelo.md
    ├── partials/
    └── scripts/generate_assets.py
```

Clase 3 corre en **http://localhost:5680** con su propio volumen Docker.

---

## El workflow padre en una frase

> Recibo una pregunta, recupero los fragmentos mas relevantes de una base documental simulada, le pido a la LLM una respuesta grounded con citas, valido que la salida tenga sentido y si algo falla respondo en modo seguro.

---

## El pipeline, etapa por etapa

### 1. Validar consulta

Nodo: `✅ Validar Consulta`

Chequear:

- que exista `question`
- `topK` en rango razonable
- `scope` valido
- `patientContext` opcional

Tambien se genera:

- `startedAtMs`
- `questionHash`

Eso permite observabilidad sin loggear la pregunta completa.

### 2. Base documental simulada

Nodo: `📚 Base documental simulada`

El workflow carga una mini base con:

- prospectos
- guias clinicas
- secciones internas

La base es chica a proposito. No queremos que el alumno confunda el patrón con escala de producción.

### 3. Chunking

Nodo: `✂️ Chunking semántico`

La estrategia usada es:

- partir por secciones
- si una seccion es larga, dividirla en grupos cortos de oraciones
- sin overlap

La idea fuerte de clase es esta:

> un chunk es una unidad de significado que despues puede recuperarse sola

### 4. Embeddings simulados

Nodo: `🧮 Embeddings simulados`

No hay embedding real de proveedor. Lo que hacemos es:

- normalizar texto
- mapear sinonimos simples
- generar un vector hashed bag-of-words

No sirve para producción. Sí sirve para mostrar:

- que texto parecido queda cerca
- que retrieval opera sobre numeros, no sobre strings directos

### 5. Retrieval

Nodo: `🔎 Retrieval Top-K`

Acá se calcula:

- similitud semantica aproximada
- pequeño refuerzo lexical
- ranking de chunks
- `top_k`

La salida relevante es:

- `retrievedChunks[]`
- `retrieval.topScore`
- `retrieval.returned`
- `evidenceSufficient`

Ese `evidenceSufficient` es importante porque después decide si tiene sentido llamar o no a la LLM.

### 6. Generation grounded

Nodo: `🤖 Respuesta grounded (OpenRouter)`

La LLM recibe:

- la pregunta
- solo los chunks recuperados

Y tiene que devolver **solo JSON** con:

- `answer`
- `sources`
- `confidence`
- `requiresHumanReview`

La clase tiene que remarcar esto:

> la LLM no reemplaza retrieval; lo consume

### 7. Validación y fallback

Nodos:

- `🧪 Parsear y validar salida`
- `⚠️ Fallback seguro`

Se valida:

- que haya JSON
- que exista `answer`
- que haya `sources`
- que las fuentes realmente correspondan a chunks recuperados

Si eso falla, el sistema no inventa otra respuesta “bonita”: cae a un modo seguro y deja fuentes parciales para revisión humana.

### 8. Observabilidad

Nodo: `📈 Log estructurado`

Se registra:

- `latencyMs`
- `fallbackUsed`
- `fallbackReason`
- `returnedChunks`
- `topScore`
- `scopeUsed`
- `requiresHumanReview`

Es suficiente para empezar a pensar un dashboard sin meter aún Loki o Datadog.

---

## Workflows parciales

### `01-chunking.json`

Sirve para mostrar:

- documento largo vs chunk
- por qué chunkear bien importa

Contrato:

- input: `documents[]`
- output: `chunks[]`

### `02-embeddings-simulados.json`

Sirve para mostrar:

- texto -> vector
- que el embedding es una representacion, no una respuesta

Contrato:

- input: `chunks[]`
- output: `embeddedChunks[]`

### `03-retrieval-topk.json`

Sirve para mostrar:

- consulta
- ranking
- top-k
- scores

Contrato:

- input: `question + embeddedChunks[]`
- output: `retrievedChunks[] + retrieval`

### `04-generation-with-sources.json`

Sirve para mostrar:

- contexto inyectado
- salida JSON del modelo
- que la LLM opera sobre lo recuperado

Contrato:

- input: `question + retrievedChunks[]`
- output: `draftResponse`

### `05-guardrails-fallback-logs.json`

Sirve para mostrar:

- por qué una salida del modelo no se acepta ciegamente
- cómo se hace grounding
- cuándo disparar fallback

Contrato:

- input: `draftResponse + retrievedChunks[]`
- output: `respuesta final + log`

### `06-rag-completo.json`

Es el workflow padre duplicado dentro de `partials/` para importarlo junto al resto sin salir de la carpeta.

### `07-ingesta-llamacloud-opcional.json`

Es una extensión, no el eje de la clase.

Sirve para mostrar:

- parsing de PDF
- cómo producir `documents[]`
- cómo reemplazar la base simulada por ingesta documental real

---

## Secuencia sugerida para dictarla

### Opción recomendada (2 horas)

1. Mostrar el workflow padre funcionando.
2. Volver a `01` y explicar chunking.
3. Pasar a `02` y `03` para fijar embeddings + retrieval.
4. Recién después abrir `04` y mostrar la LLM.
5. Cerrar con `05`: guardrails, fallback, log.
6. Dejar `07` como extensión o demo final.

---

## Casos para probar en vivo

### Caso 1 — Prospectos gastrointestinales

```json
{
  "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?",
  "scope": "prospectos",
  "topK": 4,
  "patientContext": { "age": 68, "sex": "masculino" }
}
```

Qué tiene que pasar:

- retrieval trae ibuprofeno, metformina y amoxicilina
- la LLM sintetiza
- las fuentes quedan citadas

### Caso 2 — Dolor torácico

```json
{
  "question": "Que documento habla de dolor toracico con disnea y nausea?",
  "scope": "guias",
  "topK": 3
}
```

Qué tiene que pasar:

- retrieval sube la guía de dolor torácico
- aparece `requiresHumanReview: true`

### Caso 3 — Evidencia débil

```json
{
  "question": "Que documento habla de lesiones deportivas en tobillo jugando padel?",
  "topK": 3
}
```

Qué tiene que pasar:

- retrieval flojo
- `fallbackUsed: true`

---

## Qué remarcar conceptualmente

### Lo importante

- RAG no es “meter documentos en un prompt largo”
- retrieval reduce costo, ruido y alucinación
- la fuente recuperada importa tanto como la respuesta
- en healthcare, una respuesta sin trazabilidad vale poco

### Lo que todavía no estamos enseñando

- vector DB real
- embeddings de proveedor
- re-ranking
- evaluación automática seria
- persistencia de una knowledge base viva

Eso viene después. En esta clase la prioridad es **entender el patrón**.

---

## Gotchas esperables

### 1. El alumno cree que el embedding “responde”

Corregir así:

> embedding solo representa. El que responde es el sistema completo, sobre todo retrieval + LLM.

### 2. El alumno quiere mandar todos los documentos al modelo

Corregir así:

> eso rompe costo, latencia y control. El paso retrieval existe para evitar exactamente eso.

### 3. El alumno piensa que si la LLM dio JSON ya está bien

Corregir así:

> JSON válido no implica respuesta grounded ni segura.

---

## Relación con la siguiente iteración

La migración natural después de esta clase es:

1. reemplazar embeddings simulados por embeddings reales
2. reemplazar retrieval in-memory por Qdrant / pgvector / Pinecone
3. sumar ingesta documental real como primer paso del pipeline

La ventaja es que la arquitectura conceptual ya queda instalada.
