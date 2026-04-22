# Conceptos — Mini-workflows pedagógicos

6 workflows aislados, cada uno enseñando **un concepto central** en 2-6 nodos. El objetivo es que entiendas cada pieza por separado antes de pelearte con los workflows "madre" de `clase-1/` y `clase-2/` que las integran todas.

> 💡 Cada workflow tiene **Sticky Notes amarillas** dentro del canvas explicando cada nodo. No te saltees esas notas — son el material didáctico principal.

---

## 📚 Orden sugerido

| # | Carpeta | Concepto | Prerrequisitos |
|---|---------|----------|----------------|
| 1 | [`01-n8n-101/`](./01-n8n-101/) | Webhook + Code + IF + Respond | ninguno |
| 2 | [`02-http-request/`](./02-http-request/) | HTTP Request + env vars | 01 |
| 3 | [`03-zero-shot-vs-few-shot/`](./03-zero-shot-vs-few-shot/) | Prompting con LLM (zero vs few-shot) | 02 |
| 4 | [`04-validar-output/`](./04-validar-output/) | JSON Schema validator | 03 |
| 5 | [`05-llamacloud-pdf/`](./05-llamacloud-pdf/) | Ingesta de PDFs | 02 |
| 6 | [`06-observabilidad-fallback/`](./06-observabilidad-fallback/) | Logs + fallback por reglas | 03 |

**Tiempo estimado:** 15-20 minutos por mini-workflow (leer + importar + probar + experimentar con las preguntas guía).

---

## 🚀 Setup (una sola vez)

Reutilizamos el n8n de `clase-1/`. **No hace falta otro docker-compose.**

### 1. Levantar n8n (si no está corriendo)

```bash
cd ../clase-1
cp .env.example .env
# Editá .env con tus keys:
#   - N8N_ENCRYPTION_KEY (openssl rand -hex 32)
#   - OPENROUTER_API_KEY
#   - NOTIFICATION_WEBHOOK_URL (de webhook.site)
#   - LLAMA_CLOUD_API_KEY  ← solo para el concepto 05

docker compose up -d
```

n8n queda en **http://localhost:5678**.

### 2. Importar un mini-workflow

1. Abrí http://localhost:5678 (creá el usuario owner la primera vez).
2. **Workflows → Import from file →** seleccioná el `workflow.json` del concepto que quieras ver.
3. Activá con el toggle arriba a la derecha.
4. Corré el curl del README de ese concepto.

Podés importar **todos los 6 al mismo tiempo** sin problema — cada uno usa un path distinto (`/webhook/concepto-01` hasta `/webhook/concepto-06`) así que no chocan entre sí ni con los workflows madre (que usan `/webhook/patient-analysis`).

---

## 🧭 Qué concepto de cuál workflow madre

| Concepto aislado | Dónde aparece en los workflows madre |
|------------------|--------------------------------------|
| 01 Webhook + Code + IF | `clase-1/workflow.json` — los primeros 4 nodos |
| 02 HTTP Request | `clase-1/workflow.json` — nodo `📨 Notificación` |
| 03 Zero-shot | `clase-1/workflow.json` — nodo `🤖 Análisis IA` |
| 03 Few-shot | `clase-2/workflow.json` — nodo `🤖 Análisis IA` (prompt con ejemplos) |
| 04 Validar output | `clase-2/workflow.json` — nodo `✅ Validar Output Schema` |
| 05 LlamaCloud | `clase-2/workflow.json` — nodos `☁️ Upload`, `⏳ Wait`, `📥 GET` |
| 06 Observabilidad + Fallback | `clase-2/workflow.json` — nodos `📊 Log Estructurado` + `⚠️ Fallback` |

Cuando entendés los 6 conceptos aislados, leer los workflows madre deja de ser caótico — **vas a reconocer cada parte**.

---

## 🧯 Troubleshooting

| Problema | Solución |
|----------|----------|
| "Webhook not registered" | Acordate de activar el workflow (toggle arriba a la derecha). |
| "Cannot read properties of undefined (body)" | Mandaste un body vacío o sin `Content-Type: application/json`. |
| El LLM devuelve 401 | Revisá `OPENROUTER_API_KEY` en `.env` y reiniciá el container (`docker compose restart`). |
| LlamaCloud: "Invalid API key" | Rotá la key en cloud.llamaindex.ai → API Keys → Generate New Key. |
| El curl tarda mucho (>15s) | Normal en concepto 05 (PDFs grandes). En los otros, revisá logs con `docker logs n8n-dev`. |

---

## 📖 Siguiente paso

Cuando te sientas cómodo con los 6 conceptos:

1. **Leé `clase-1/README.md`** — ahí están integrados los conceptos 01-03.
2. **Leé `clase-2/README.md`** + `clase-2/GUIA.md` — agrega los conceptos 04-06 y el workflow completo de triage clínico.
