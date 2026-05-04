# Concepto 02 — HTTP Request externo

## 🎯 Qué vas a aprender

Cómo hacer que n8n **llame a una API externa**. Es el nodo más usado en workflows reales (hablar con Slack, OpenAI, tu propia API, etc.). Además vas a entender cómo usar **variables de entorno** con `{{ $env.X }}` para no hardcodear secretos.

## 🧩 El workflow

```
Webhook (POST /concepto-02)
    ↓
HTTP Request (POST a un webhook externo fijo)
    ↓
Respond OK
```

## 🧪 Cómo probarlo

Este concepto quedó preparado con una URL fija de [webhook.site](https://webhook.site) dentro del nodo HTTP Request, así que no depende de `$env` ni de features pagas de la UI.

```bash
curl -X POST http://localhost:5678/webhook/concepto-02 \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"P-001","symptoms":"dolor toracico","age":67}'
```

Después abrí la URL configurada en el nodo HTTP Request — vas a ver el POST llegando.

## 👀 Qué mirar

- En el nodo **HTTP Request**: cómo se configuran `method`, `url`, `headers` y `body`.
- La URL está hardcodeada en el nodo HTTP Request para que el ejemplo funcione aunque la UI no te deje usar env vars.
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

1. **¿Qué pasa si cambiás la URL del nodo** por una URL inválida (ej: `https://nope.invalid`)? ¿Cuántas veces reintenta antes de fallar? (pista: mirá "Retry on Fail").
2. **Agregá otro header custom** al HTTP Request (ej: `X-Patient-Priority` con el valor del patientId). ¿Dónde aparece en webhook.site?
3. **Cambiá el method de POST a GET.** ¿Qué pasa con el body? (pista: GET no lleva body, n8n lo convierte en query params).
