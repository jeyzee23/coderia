# Clase 6 HTL

Workflow educativo de **Human-in-the-Loop (HITL)** con bots/notificaciones, aprobacion humana por webhook, politicas de espera, fallback por escalamiento y observabilidad basica.

> Proyecto educativo. No usar para decisiones clinicas reales.

## Setup

```bash
cd /Users/juancavidela/Desktop/coder-ia/clase-6-htl
cp .env.example .env
# Por defecto usa https://postman-echo.com/post para notificaciones.
# Si queres verlas en vivo, reemplazar esos valores por URLs de Webhook.site.
docker compose up -d
```

Abrir n8n en:

```text
http://localhost:5684
```

Importar:

```text
workflow.json
```

Endpoint:

```text
POST http://localhost:5684/webhook/hitl-review-request
```

## Archivos

```text
clase-6-htl/
├── GUIA.md
├── README.md
├── workflow.json
├── postman_collection.json
├── docker-compose.yml
└── .env.example
```
