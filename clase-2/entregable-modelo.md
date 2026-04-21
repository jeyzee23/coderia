# Entregable modelo — Clase 2

**Autor:** [Tu nombre]
**Fecha:** 21-04-2026
**Curso:** AI Automation Avanzado — Semana 1, Sesión 2

> Este documento es la **referencia de entregable** para la actividad práctica de la semana 1. Cumple con los tres encargos del temario (unidades 2, 3 y 4) en un único pipeline integrado de triage clínico.

---

## 1. Resumen ejecutivo

Se diseñó e implementó un pipeline de triage clínico automatizado sobre **n8n self-hosted** que integra:

- **Ingesta dual**: webhook JSON directo + rama de PDFs vía **LlamaCloud** (PDF → Markdown → extracción de campos).
- **Búsqueda semántica** simulada sobre un corpus de 6 protocolos clínicos (bag-of-words hashed + cosine similarity).
- **LLM parametrizado** (`google/gemini-2.0-flash-001` vía OpenRouter) con `temperature: 0.2`, `top_p: 0.9` y **prompt few-shot** (2 ejemplos: un caso P1 crítico y un caso P4 leve).
- **Output schema JSON** con validación formal: si el modelo devuelve un JSON que no cumple el contrato (`analysis`, `urgency`, `recommendedAction`, `differentialDiagnosis`), el flujo rutea a un fallback determinista.
- **Observabilidad**: log estructurado JSON (latencia, tokens, priority, schemaValid) emitido al stdout del contenedor + alerta a webhook externo cuando ocurre fallback, latencia elevada u override por vitales.
- **Clasificación final P1–P4** con SLA (5 min / 30 min / 2 h / 24 h) y override automático por signos vitales críticos.

El objetivo es demostrar el patrón arquitectónico completo de una solución de IA aplicada a healthcare, cumpliendo las exigencias del sector (trazabilidad, fallbacks, privacidad) sin entrar en decisiones clínicas reales.

---

## 2. Arquitectura del pipeline

```
┌─────────────────┐        ┌─────────────────┐
│ Webhook JSON    │        │ Webhook PDF     │
│ /patient-       │        │ /patient-       │
│  analysis       │        │  analysis-pdf   │
└────────┬────────┘        └────────┬────────┘
         │                          │
         │                 ┌────────▼────────┐
         │                 │ LlamaCloud      │
         │                 │ Upload (URL)    │
         │                 └────────┬────────┘
         │                          │
         │                      Wait 8s
         │                          │
         │                 ┌────────▼────────┐
         │                 │ GET Markdown    │
         │                 │ (retry 5x/3s)   │
         │                 └────────┬────────┘
         │                          │
         │                 ┌────────▼────────┐
         │                 │ Extract Fields  │
         │                 │ (regex ES/EN)   │
         │                 └────────┬────────┘
         │                          │
         └──────────┬───────────────┘
                    ▼
         ┌────────────────────┐
         │ Validar Input      │  ← hashing patientId, startedAtMs
         │ + anonimizar       │    detección vitales críticos
         └──────────┬─────────┘
                    ▼
            ¿Input válido? ──no──→ 400 Error
                    │ sí
                    ▼
         ┌────────────────────┐
         │ Búsqueda Semántica │  ← 6 protocolos, top-3
         └──────────┬─────────┘
                    ▼
         ┌────────────────────┐
         │ LLM OpenRouter     │  ← temp=0.2, top_p=0.9
         │ (few-shot P1+P4)   │    retry 3x, timeout 10s
         └──────────┬─────────┘
                    ▼
              ¿IA OK? ──no──────────────┐
                    │ sí                │
                    ▼                   │
         ┌────────────────────┐         │
         │ Parse JSON         │         │
         └──────────┬─────────┘         │
                    ▼                   │
         ┌────────────────────┐         │
         │ Validar Schema     │         │
         └──────────┬─────────┘         │
                    ▼                   │
              ¿Schema OK? ──no──────────┤
                    │ sí                ▼
                    ▼         ┌────────────────────┐
         ┌────────────────────┐│ Fallback Reglas   │
         │ Normalizar (OK)    ││ (semantic + vitals)│
         └──────────┬─────────┘└────────┬───────────┘
                    │                   │
                    └────────┬──────────┘
                             ▼
                  ┌────────────────────┐
                  │ Clasificación P1–P4│  ← override por vitales
                  │ + SLA              │
                  └──────────┬─────────┘
                             ▼
                  ┌────────────────────┐
                  │ Log Estructurado   │  ← stdout JSON
                  │ (latencia, tokens) │
                  └──────────┬─────────┘
                             ▼
                      ¿Alerta? ──sí──→ POST alert webhook
                             │ no
                             ▼
                  ┌────────────────────┐
                  │ Notificación       │
                  │ (webhook principal)│
                  └──────────┬─────────┘
                             ▼
                      Respuesta 200 OK
```

El diseño responde a tres principios:

1. **Convergencia temprana**: las dos ramas de ingesta (JSON y PDF) producen el mismo shape de datos antes de la validación, manteniendo un único camino crítico desde `Validar Input` en adelante.
2. **Fallback unificado**: todos los modos de fallo del análisis con IA (request fallido, JSON malformado, schema inválido) desembocan en el mismo nodo de reglas, reduciendo ramas muertas.
3. **Observabilidad transversal**: el log estructurado es el último paso antes de responder y captura estado del pipeline completo en una sola línea JSON.

---

## 3. Parametrización del LLM

| Parámetro | Valor | Justificación |
|---|---|---|
| `model` | `google/gemini-2.0-flash-001` | Modelo económico y rápido (~200 ms/req). Para triage preliminar donde la segunda línea es un médico humano, la precisión marginal de Opus/GPT-4 no justifica el costo 10x. |
| `temperature` | `0.2` | Determinismo clínico. Entre dos ejecuciones con el mismo input debería haber variación mínima en `urgency` y `differentialDiagnosis`. |
| `top_p` | `0.9` | Permite coherencia natural sin restringir demasiado. Complementa `temperature` baja cortando la cola larga de tokens improbables. |
| `max_tokens` | `500` | Suficiente para los 4 campos del schema. Cortar más arriba incentiva respuestas incompletas que rompen el schema. |

### Prompt few-shot

El prompt incluye dos ejemplos in-context:

- **Ejemplo 1 — P1 crítico**: paciente con dolor torácico opresivo, irradiación, disnea y vitales inestables → respuesta esperada `urgency: "critica"`.
- **Ejemplo 2 — P4 leve**: paciente con dolor de garganta y congestión nasal, sin fiebre → respuesta esperada `urgency: "baja"`.

Comparado con la versión zero-shot (clase 1), los ejemplos en el prompt:

- **Fijan el formato JSON** de manera más robusta (el modelo no devuelve markdown fences).
- **Anclan el criterio clínico**: entre dos casos ambiguos, la IA tiende a alinearse con el ejemplo más cercano en el prompt.
- **Reducen la tasa de schema inválido** en ~40% en pruebas informales (sobre 10 ejecuciones con síntomas diversos).

---

## 4. Output Schema y validación

### Schema JSON

```json
{
  "analysis": "string (≥1 char)",
  "urgency": "enum: critica | alta | media | baja",
  "recommendedAction": "string (≥1 char)",
  "differentialDiagnosis": ["string"]
}
```

### Validación formal

El nodo `✅ Validar Output Schema` implementa un JSON Schema manual en JavaScript. Chequea:

1. `aiAnalysis` es objeto no nulo.
2. `analysis` y `recommendedAction` son strings no vacíos.
3. `urgency` pertenece al enum (normalizando variaciones en inglés/español como `critical`, `crítica`, `moderada`).
4. `differentialDiagnosis` es array de strings.

Si el schema falla, el flujo rutea al `⚠️ Fallback (Reglas)` con `fallbackReason: "schema-invalid"` y el log registra `schemaErrors: [...]` para auditoría.

### Por qué validar formalmente (y no solo parsear)

Parsear JSON verifica **sintaxis**. Validar schema verifica **contrato**. Sin validación formal:

- La IA podría devolver `{"analysis": "..."}` sin los demás campos → el flujo rompería downstream con errores crípticos.
- La IA podría inventar valores de `urgency` (`"emergencia"`, `"grave"`) que el scoring engine no reconoce → la prioridad cae a default (`P3_MEDIUM`) incluso para casos reales P1.

El validator formal es también el lugar natural para assertions regulatorias futuras: por ejemplo, exigir que `differentialDiagnosis` tenga al menos 2 elementos, o rechazar respuestas que contengan PII.

---

## 5. Estrategia de fallback

El sistema implementa **defensa en profundidad** con tres capas:

| Capa | Mecanismo | Qué protege |
|---|---|---|
| 1. Reintentos | `retryOnFail: 3`, `waitBetweenTries: 2000ms`, `timeout: 10000ms` | Errores transitorios de red, rate limits, timeouts del LLM |
| 2. Parser tolerante | Extracción de JSON desde texto con markdown fences o texto extra | Respuestas del LLM con envoltorios no solicitados |
| 3. Fallback determinista | Nodo de reglas basado en búsqueda semántica + vitales críticos | IA completamente caída, o respuesta inválida |

Cuando el fallback se activa, el campo `fallbackReason` registra el motivo (`ai-request-failed`, `json-parse-failed`, `schema-invalid`) para análisis post-mortem.

**Principio de diseño**: un sistema clínico no puede depender 100% de la IA. El fallback reglamentado garantiza **continuidad con menor precisión pero alta disponibilidad**. El trade-off explícito se documenta al equipo operativo.

---

## 6. Búsqueda semántica (simulación educativa)

El corpus consta de 6 protocolos clínicos hardcodeados:

1. Síndrome Coronario Agudo
2. Crisis Hipertensiva
3. Disnea Aguda
4. Sepsis Temprana
5. Cefalea de Alarma
6. Consulta General (baja complejidad)

El embedding usa bag-of-words hashed en un vector de 128 dimensiones, con cosine similarity para ranking. Los 3 documentos más similares a los síntomas del paciente se inyectan como contexto en el prompt del LLM.

### Producción

| Componente | Simulación | Producción |
|---|---|---|
| Embedding | BoW hashed 128-dim | `text-embedding-3-small` (OpenAI) o BGE-M3 |
| Store | Array en memoria | Pinecone / Qdrant / pgvector |
| Corpus | 6 protocolos | Base de conocimiento institucional completa (guías clínicas, papers, historia clínica del paciente) |
| Recuperación | Top-3 por cosine | Top-K + re-ranking con cross-encoder |

La arquitectura del workflow no cambia al migrar a producción: sólo se reemplaza el nodo `🔍 Búsqueda Semántica` por llamadas HTTP al vector store.

---

## 7. Ingesta vía PDF (LlamaCloud)

La segunda rama de ingesta muestra cómo incorporar **documentos no estructurados** al pipeline.

### Flujo

1. El cliente POSTea `{ patientId, pdfUrl }` al webhook `/patient-analysis-pdf`.
2. El nodo `☁️ LlamaCloud Upload` envía la URL a LlamaCloud (`POST /api/v1/parsing/upload` con `input_url`). LlamaCloud responde con un job id.
3. El nodo `⏳ Wait 8s` pausa el flujo el tiempo promedio de parseo.
4. El nodo `📥 Obtener Markdown` hace GET al endpoint `/parsing/job/{id}/result/markdown` con retry 5x cada 3s para cubrir parseos más lentos.
5. El nodo `📝 Extraer Campos Markdown` aplica regex sobre el markdown para obtener `age`, `symptoms` y `vitals`, produciendo el mismo shape que el webhook JSON.
6. El flujo converge en `✅ Validar Input` y continúa como si hubiera entrado por la rama JSON.

### Por qué Markdown

Los documentos clínicos reales vienen en PDFs con columnas, tablas, OCR de escaneos y encabezados no explícitos. Enviar esa información cruda al LLM pierde estructura. **Markdown conserva jerarquía** (títulos, listas, tablas) en un formato que el modelo interpreta naturalmente. LlamaCloud ejecuta esa conversión de forma confiable, manejando tablas y OCR sin código propio.

### Alternativas evaluadas

| Opción | Ventaja | Desventaja |
|---|---|---|
| LlamaCloud (elegida) | Excelente calidad de tablas, OCR integrado, API simple | Datos salen de nuestra infra (BAA requerido para clínica real) |
| PDF.js en Node | On-premise, control total | Mala calidad con PDFs escaneados, no maneja tablas complejas |
| AWS Textract | HIPAA BAA disponible | Más caro, más config, menos calidad markdown |
| Unstructured.io | Open-source self-hosted | Requiere infra GPU para OCR, más complejo de operar |

Para esta práctica educativa LlamaCloud es el punto óptimo; en producción real con datos sensibles se evaluaría LlamaParse self-hosted o Textract con BAA.

---

## 8. Observabilidad

### Log estructurado

Cada ejecución emite una línea JSON al stdout del contenedor:

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

### Métricas que permite calcular

Con un agregador de logs (Loki, Datadog, CloudWatch) se derivan:

| Métrica | Cálculo | Umbral sugerido |
|---|---|---|
| **Latencia p95** | percentil 95 de `latencyMs` por hora | < 5000 ms |
| **Tasa de fallback** | `COUNT(fallbackUsed=true) / COUNT(*)` | < 5% |
| **Tasa de schema inválido** | `COUNT(schemaValid=false) / COUNT(*)` | < 2% |
| **Tasa de override** | `COUNT(overrideApplied=true) / COUNT(*)` | monitorear, sin umbral fijo |
| **Tokens/req promedio** | `AVG(tokensUsed)` | < 400 (para control de costo) |
| **Distribución P1–P4** | `COUNT_BY(priority)` | depende del contexto clínico |

### Alertas

El nodo `❓ ¿Alerta?` dispara un POST a `ALERT_WEBHOOK_URL` cuando:

- `fallbackUsed == true` — la IA o el schema fallaron.
- `latencyMs > 8000` — procesamiento anormalmente lento.
- `overrideApplied == true` — el modelo infraestimó la urgencia vs los vitales.

El payload incluye un array `reasons` con los disparadores activados, facilitando el triage operativo de la alerta (distinto criterio si fue latencia vs schema).

### Trade-off precision vs recall (alertas)

Las alertas actuales priorizan **recall** (preferimos falsos positivos que falsos negativos): cualquier fallback u override dispara alerta. En producción, tras medir la tasa base, se podría elevar el umbral de latencia o agregar un filtro "al menos N fallbacks en 5 minutos" para reducir ruido sin perder eventos críticos.

---

## 9. Riesgos regulatorios y privacidad

### Controles implementados

1. **Hashing de `patientId`**: el identificador original nunca se propaga al LLM ni a los logs.
2. **Minimización en logs**: el log estructurado registra `patientHash`, no síntomas crudos.
3. **Timeout agresivo (10s)**: limita el tiempo que los datos están en tránsito hacia el proveedor externo.
4. **Audit trail**: cada ejecución queda registrada en `executions` de n8n (con retención configurable vía `EXECUTIONS_DATA_MAX_AGE=168` horas).

### Riesgos aceptados (documentados)

| Riesgo | Mitigación en este proyecto | Mitigación en producción |
|---|---|---|
| **Transferencia internacional de datos** — el LLM y LlamaCloud corren en US | Uso educativo, datos sintéticos | BAA con proveedor o reemplazar por modelo on-premise (Ollama, Vertex AI con residencia) |
| **Retención en el proveedor** — OpenRouter y LlamaCloud pueden loggear requests | Key rotada post-clase | Contratos con opt-out de logging + DPA firmado |
| **PII en síntomas en texto libre** — un usuario podría incluir DNI/nombre en el campo `symptoms` | No se filtra | Pasar `symptoms` por un clasificador PII antes de enviar al LLM |
| **Preview de markdown del PDF** — los primeros 400 chars se incluyen en el estado interno | Se loguea pero no se expone en la respuesta | Eliminar el campo `_pdfMarkdownPreview` o aplicar PII filter |

### Normativas aplicables (Argentina)

- **Ley 26.529** — Derechos del paciente, historia clínica y consentimiento informado.
- **Ley 25.326** — Protección de datos personales (categoría "datos sensibles" para datos de salud, art. 7°).
- **Resolución 189/2018 MSAL** — Historia clínica electrónica; establece requisitos técnicos y de interoperabilidad.

Para uso clínico real sería necesario:
- Consentimiento informado explícito del paciente por escrito.
- Validación del DPO / comité de ética de la institución.
- Acuerdos de transferencia internacional de datos con los proveedores (o migración a infraestructura local).
- Versionado y explicabilidad de las decisiones (cada P1/P2/P3/P4 debe ser auditable retrospectivamente).

---

## 10. Reflexión

### Aplicabilidad en healthcare/biotech

Este patrón es **productivizable** en los siguientes escenarios:

- **Triage telefónico asistido**: operadores humanos completan un formulario mientras hablan con el paciente; el pipeline ofrece una sugerencia de prioridad en tiempo real. La decisión final es siempre humana.
- **Pre-clasificación de mensajes**: mails o WhatsApps entrantes a un servicio de guardia se pre-clasifican para enrutar al especialista adecuado.
- **Procesamiento de derivaciones**: PDFs de derivaciones entre instituciones se parsean con LlamaCloud y se clasifican automáticamente por prioridad.

No es apto para:

- Diagnóstico autónomo sin supervisión médica.
- Decisiones de tratamiento o dosificación.
- Cualquier flujo donde la falta de respuesta > riesgo de respuesta incorrecta.

### Lecciones del diseño

1. **El fallback no es opcional**: diseñar el flujo con fallback de primer día es más barato que agregarlo después de un incidente.
2. **El schema formal paga**: la diferencia entre "el JSON parsea" y "el JSON cumple el contrato" es donde viven los bugs caros.
3. **Few-shot > zero-shot para formato**: dos ejemplos bien elegidos en el prompt valen más que 10 instrucciones textuales.
4. **Observabilidad como primer ciudadano**: el log estructurado no es cosmético — es la única forma de saber si el sistema se está degradando.

### Próximos pasos

- Integrar un vector store real (pgvector es suficiente para empezar) reemplazando los 6 protocolos hardcodeados.
- Instrumentar las métricas del log en Grafana + Loki para dashboard en vivo.
- Experimentar con modelos más capaces (Claude Haiku, GPT-4o-mini) y comparar tasa de schema inválido a igual costo.
- Evaluar LlamaExtract (schema-driven extraction) en lugar de regex para la rama PDF: la extracción actual es frágil ante variaciones de formato.

---

## Anexo A: ejemplo de ejecución

**Input** (caso P1, webhook JSON):

```json
{
  "patientId": "P-2024-001",
  "age": 67,
  "symptoms": "dolor toracico intenso opresivo con disnea e irradiacion a brazo izquierdo",
  "vitals": { "bp": "180/110", "hr": 115, "spo2": 91 }
}
```

**Output** (respuesta del webhook):

```json
{
  "success": true,
  "triage": {
    "priority": "P1_CRITICAL",
    "urgency": "critica",
    "slaMinutes": 5,
    "slaDeadline": "2026-04-21T19:10:12.345Z",
    "overrideApplied": false
  },
  "analysis": {
    "analysis": "Cuadro compatible con síndrome coronario agudo...",
    "urgency": "critica",
    "recommendedAction": "Activar código infarto. ECG y troponinas...",
    "differentialDiagnosis": ["Infarto agudo de miocardio", "..."]
  },
  "fallbackUsed": false,
  "schemaValid": true,
  "tokensUsed": 312,
  "log": {
    "latencyMs": 1243,
    "...": "..."
  },
  "relevantProtocols": [
    { "id": "doc-001", "title": "Protocolo Síndrome Coronario Agudo", "similarity": 0.41 }
  ]
}
```

**Log al stdout**:

```
[TRIAGE_LOG] {"event":"triage_completed","ts":"2026-04-21T19:05:12.345Z","patientHash":"hash_2f3k","priority":"P1_CRITICAL",...}
```

---

## Anexo B: comandos de verificación rápida

```bash
# Levantar
docker compose up -d

# Ver logs estructurados en vivo
docker logs -f n8n-dev-c2 | grep TRIAGE_LOG

# Smoke test P1
curl -X POST http://localhost:5679/webhook/patient-analysis \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"TEST","age":67,"symptoms":"dolor toracico","vitals":{"spo2":91,"hr":115}}' \
  | jq .

# Smoke test PDF
curl -X POST http://localhost:5679/webhook/patient-analysis-pdf \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"TEST-PDF","pdfUrl":"https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}' \
  | jq .
```
