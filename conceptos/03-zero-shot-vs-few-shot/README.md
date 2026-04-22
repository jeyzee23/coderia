# Concepto 03 — Zero-shot vs Few-shot

## 🎯 Qué vas a aprender

Qué es **few-shot prompting** y por qué funciona mejor que zero-shot. El workflow corre el MISMO input por dos prompts distintos y te devuelve ambos outputs lado a lado para que veas la diferencia con tus propios ojos.

- **Zero-shot:** solo instrucciones, sin ejemplos.
- **Few-shot:** instrucciones + 2 ejemplos completos (un P1 crítico y un P4 leve).

## 🧩 El workflow

```
Webhook (POST /concepto-03)
    ↓
HTTP Request 🅰️ Zero-shot   (LLM sin ejemplos)
    ↓
HTTP Request 🅱️ Few-shot    (LLM con 2 ejemplos)
    ↓
Code Compare (junta ambas respuestas)
    ↓
Respond OK
```

> **Nota:** corren en serie, no en paralelo. El segundo HTTP Request toma el body del webhook vía `$('🩺 Webhook').first().json.body`, no depende del primero. Ejecutarlo en paralelo es posible pero requiere Merge node — acá priorizamos claridad.

## 🧪 Cómo probarlo

**Caso borderline** (donde el criterio importa):

```bash
curl -X POST http://localhost:5678/webhook/concepto-03 \
  -H 'Content-Type: application/json' \
  -d '{
    "age": 55,
    "symptoms": "dolor de cabeza moderado con nauseas",
    "vitals": { "hr": 95 }
  }'
```

## 👀 Qué mirar

El output te devuelve ambas respuestas crudas y parseadas:

```json
{
  "input": { "age": 55, "symptoms": "...", "vitals": {...} },
  "zeroShot": {
    "raw": "```json\n{\"urgency\": \"P3\", ...}\n```",
    "parsed": { "urgency": "P3", "reasoning": "..." },
    "tokens": 87
  },
  "fewShot": {
    "raw": "{\"urgency\":\"P3\",\"reasoning\":\"...\"}",
    "parsed": { "urgency": "P3", "reasoning": "..." },
    "tokens": 240
  }
}
```

**Cosas típicas que vas a ver:**

| | Zero-shot | Few-shot |
|---|-----------|----------|
| Formato | A veces con markdown fences ` ```json ` | Suele venir JSON limpio |
| Consistencia | Puede mezclar P1-P4 con "crítica"/"alta" | Respeta la escala de los ejemplos |
| Tokens usados | Menos (~80) | Más (~250, por los ejemplos) |
| Razonamiento | A veces genérico | Más alineado al estilo de los ejemplos |

## 💡 Preguntas guía

1. **Corré el mismo curl 3 veces seguidas.** ¿Las respuestas del zero-shot varían más que las del few-shot? ¿Por qué? (pista: `temperature: 0.2` + ejemplos ancla el criterio).
2. **Agregá un 3er ejemplo al few-shot** (ej: un caso P2). ¿Cambia el criterio para casos medios?
3. **Sacá los 2 ejemplos del few-shot** → se convierte en zero-shot. Probá con un caso borderline. ¿Cuánto varía el output entre 5 ejecuciones?
4. Contá los **tokens usados** en ambos (`usage.total_tokens`). ¿Cuánto más caro es el few-shot? ¿Vale la pena?
