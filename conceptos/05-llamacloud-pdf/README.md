# Concepto 05 — LlamaCloud (PDF → texto)

## 🎯 Qué vas a aprender

Cómo convertir un **PDF en texto procesable** usando LlamaCloud. El parsing de documentos es **asíncrono** — aprendés el patrón: *subir → esperar → descargar*.

Una vez que tenés el PDF como markdown, podés pasarlo a un LLM para extraer información (síntomas, diagnóstico, etc.).

## 🧩 El workflow

```
Webhook (POST /concepto-05, body: { pdfUrl })
    ↓
HTTP Request ☁️ Upload a LlamaCloud (responde con job_id)
    ↓
Wait 8 segundos (para que LlamaCloud parsee)
    ↓
HTTP Request 📥 GET markdown del job_id
    ↓
Respond OK con el markdown
```

## 🧪 Cómo probarlo

**Requisito:** tu `.env` debe tener `LLAMA_CLOUD_API_KEY`. Sacá una gratis en [cloud.llamaindex.ai](https://cloud.llamaindex.ai) → API Keys.

**PDF dummy** (va a devolver markdown casi vacío, sirve para smoke test):

```bash
curl -X POST http://localhost:5678/webhook/concepto-05 \
  -H 'Content-Type: application/json' \
  -d '{"pdfUrl":"https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'
```

**Para demo más vistosa** — usá el informe clínico que está en este repo (hay que servirlo con una URL pública). O buscá cualquier PDF público (ej: un paper de arxiv).

## 👀 Qué mirar

**Respuesta esperada:**
```json
{
  "success": true,
  "pdfUrl": "https://.../dummy.pdf",
  "markdown": "# Dummy PDF file\n\n...",
  "charCount": 42
}
```

**Lo importante:**
- El nodo **Upload** devuelve un `job_id` (`{ id: 'xxx' }`). No devuelve el markdown directo.
- **Wait 8s** da tiempo al parsing. Si el PDF es grande, puede fallar — por eso el nodo GET tiene retry 5x.
- **GET** usa `{{ $json.id }}` para armar la URL con el `job_id` del upload.

## 💡 Preguntas guía

1. **¿Qué pasa si bajás el Wait a 1 segundo?** Probá. El GET va a fallar con 400 (job todavía PENDING) → el retry de 5x con 3s salva la situación igual.
2. **Probá con un PDF inválido** (ej: `pdfUrl: "https://google.com"`). ¿Qué error devuelve LlamaCloud?
3. **¿Cómo conectarías esto con el concepto 04?** Spoiler: después del markdown, pasás el texto al LLM y validás el schema de la extracción.
4. **¿Por qué el parsing es asíncrono?** Pista: parsear PDFs grandes con OCR puede tardar minutos. El patrón upload → job_id → poll es estándar en APIs de procesamiento pesado (Whisper, LlamaParse, etc.).

## ⚠️ Notas de privacidad

Al usar LlamaCloud, el PDF viaja a servidores de LlamaIndex Inc. (US por default). Para datos clínicos reales evaluá:
- **BAA** con el proveedor (HIPAA compliance)
- **LlamaParse self-hosted** (on-prem)
- **Borrar el documento** vía API apenas termina el parseo
