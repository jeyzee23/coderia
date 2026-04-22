# Concepto 02 — HTTP Request externo

## 🎯 Qué vas a aprender

Cómo hacer que n8n **llame a una API externa**. Es el nodo más usado en workflows reales (hablar con Slack, OpenAI, tu propia API, etc.). Además vas a entender cómo usar **variables de entorno** con `{{ $env.X }}` para no hardcodear secretos.

## 🧩 El workflow

```
Webhook (POST /concepto-02)
    ↓
HTTP Request (POST a $env.NOTIFICATION_WEBHOOK_URL)
    ↓
Respond OK
```

## 🧪 Cómo probarlo

Antes de arrancar, asegurate de que tu `.env` de `clase-1/` tenga una URL real en `NOTIFICATION_WEBHOOK_URL` (conseguila gratis en [webhook.site](https://webhook.site)).

```bash
curl -X POST http://localhost:5678/webhook/concepto-02 \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"P-001","symptoms":"dolor toracico","age":67}'
```

Después abrí tu URL de webhook.site en el navegador — vas a ver el POST llegando.

## 👀 Qué mirar

- En el nodo **HTTP Request**: cómo se configuran `method`, `url`, `headers` y `body`.
- La expresión `{{ $env.NOTIFICATION_WEBHOOK_URL }}` — lee una variable de entorno del container.
- Cómo el `jsonBody` combina datos fijos (`event`, `ts`) con datos dinámicos del webhook (`$json.body`).
- La opción **Retry on Fail** del nodo: si el webhook externo está caído, reintenta 2 veces.

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "POST enviado al webhook externo",
  "externalResponse": { "status": "ok", "uuid": "..." }
}
```

Y en webhook.site:
```json
{
  "event": "paciente_recibido",
  "ts": "2026-04-21T...",
  "patient": { "patientId": "P-001", "symptoms": "dolor toracico", "age": 67 }
}
```

## 💡 Preguntas guía

1. **¿Qué pasa si cambiás `$env.NOTIFICATION_WEBHOOK_URL` por una URL inválida** (ej: `https://nope.invalid`)? ¿Cuántas veces reintenta antes de fallar? (pista: mirá "Retry on Fail").
2. **Agregá otro header custom** al HTTP Request (ej: `X-Patient-Priority` con el valor del patientId). ¿Dónde aparece en webhook.site?
3. **Cambiá el method de POST a GET.** ¿Qué pasa con el body? (pista: GET no lleva body, n8n lo convierte en query params).
