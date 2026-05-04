# Integración LlamaCloud + n8n — Clase 4

Clase 4 introduce el patrón de **parsing documental automatizado** usando LlamaCloud como servicio de extracción de documentos, con integración en n8n para workflows completos de procesamiento.

> ⚠️ Proyecto educativo. Datos sensibles en producción requieren BAA con proveedores.

## Qué construye esta clase

- Workflow completo de parsing con LlamaCloud.
- Receptor de documentos vía webhook (PDF, DOCX, PPTX).
- Extracción de texto, markdown y tablas.
- Anonimización de datos sensibles (PII masking).
- Almacenamiento estructurado (Google Sheets / Airtable).
- Propuesta conceptual de workflow auto-mejorable.

## Idea central

El pipeline recibe documentos clínicos, los envía a LlamaCloud para parseo, anonimiza datos sensibles, y almacena los resultados para uso downstream.

```
Webhook entrada
     -> Upload a LlamaCloud
     -> Poll resultado
     -> Parse y extracción
     -> Anonimización PII
     -> Storage (Sheets/Airtable)
     -> Respuesta
```

## Setup

Clase 4 corre en **puerto 5680**, compartiendo con clase 3.

```bash
cd clase-3
cp .env.example .env
# completar LLAMA_CLOUD_API_KEY

docker compose up -d
```

n8n queda en **http://localhost:5680**.

## Importar workflow

1. Abrir `http://localhost:5680`
2. Crear usuario owner
3. `Workflows -> Import from file -> partials/08-llamacloud-parse.json`
4. Importar también el workflow padre de clase 3 si no está

## Configurar credenciales n8n

### Google Sheets (opcional)

1. Ir a **Settings -> Credentials**
2.Agregar **Google OAuth2 API**
3. Configurar client ID y secret

### Airtable (opcional)

1. Ir a **Settings -> Credentials**
2. Agregar **Airtable API**
3. Ingresar API key y base ID

## Probar el workflow

```bash
curl -X POST http://localhost:5680/webhook/llamacloud-parse \
  -H 'Content-Type: application/json' \
  -d '{
    "fileUrl": "https://www.w3.org/WAI/ER/tests/xhtml/test/files/HelloWorld.pdf"
  }'
```

## Estructura

```
clase-3/
├── partials/
│   ├── 08-llamacloud-parse.json    # Workflow parsing
│   └── ...
├── scripts/
│   └── generate_assets.py
├── README.md
└── GUIA.md
```

## Notas de privacidad

- Los documentos se envían a LlamaCloud (servicio externo en US).
- La anonimización es heurística: revisar输出的 antes de usar.
- Para datos clínicos reales, evaluar LlamaParse self-hosted.
- Cumplimiento: Ley 25.326 (protección de datos), Ley 26.529 (derechos del paciente).