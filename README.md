# Healthcare AI Triage — Curso de IA aplicada

Workflow de **triage clínico** construido en n8n self-hosted + OpenRouter. Dos clases progresivas: arrancás con un flujo simple y lo vas extendiendo con técnicas de prompting avanzado, ingesta de PDFs y observabilidad.

> ⚠️ Proyecto educativo. No usar para decisiones clínicas reales.

---

## 📚 Estructura del repo

```
coder-ia/
├── clase-1/   → Workflow base (puerto 5678)
└── clase-2/   → Extensión avanzada (puerto 5679)
```

Cada carpeta es **auto-contenida**: tiene su propio `docker-compose.yml`, `.env.example`, `workflow.json` y `README.md`. Conviven sin chocar.

---

## 🎯 Qué aprendés en cada clase

| Clase | Tema | Qué construís |
|-------|------|---------------|
| **1️⃣** | Fundamentos | Webhook → validación → búsqueda semántica → LLM → clasificación P1–P4 + fallback por reglas |
| **2️⃣** | Prompting avanzado + ingesta + observabilidad | Few-shot, JSON Schema validator, ingesta de PDFs via LlamaCloud, logs estructurados y alertas |

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

### Postman

Cada clase trae su `postman_collection.json` con casos preparados (P1, P2, P3, P4, override por vitales, error 400, PDFs en clase 2). Importalo y listo.

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

---

## 🧯 Troubleshooting

| Problema | Solución |
|----------|----------|
| "Port 5678/5679 already in use" | Otro proceso ocupa el puerto. `docker ps` y bajá lo que sobra. |
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

Dudas → preguntá en clase.
