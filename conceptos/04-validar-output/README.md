# Concepto 04 — Validar output del LLM

## 🎯 Qué vas a aprender

Por qué **no podés confiar ciegamente en el LLM** y cómo protegerte. Un LLM puede devolver:

- Texto con markdown fences (` ```json `) alrededor
- JSON con campos faltantes
- Valores fuera del enum esperado (ej: `"crítica"` en vez de `"P1"`)
- JSON truncado (si te quedás sin tokens)

Este workflow te muestra cómo validar el output con un **JSON Schema validator** manual y bifurcar el flujo si no cumple.

## 🧩 El workflow

```
Webhook (POST /concepto-04)
    ↓
HTTP Request LLM
    ↓
Code — Validar Schema
    ↓
IF ¿schemaValid?
    ├─ true  → ✅ Respond OK con el JSON parseado
    └─ false → ❌ Respond Error 400 con los errores
```

## 🧪 Cómo probarlo

**Caso normal** (debería validar OK):

```bash
curl -X POST http://localhost:5678/webhook/concepto-04 \
  -H 'Content-Type: application/json' \
  -d '{"age":67,"symptoms":"dolor toracico intenso con disnea"}'
```

**Forzar fallo de schema:**

Entrá al editor, abrí el nodo **🤖 LLM**, y cambiá `max_tokens: 200` → `max_tokens: 20`. Guardá el workflow y probá el mismo curl. El LLM va a cortar el JSON a la mitad y el validator lo va a rechazar.

## 👀 Qué mirar

**Respuesta OK:**
```json
{
  "success": true,
  "triage": { "urgency": "P1", "reasoning": "Sospecha de SCA..." }
}
```

**Respuesta Error (con `max_tokens: 20`):**
```json
{
  "success": false,
  "errors": ["no se pudo parsear el output como JSON"],
  "rawContent": "{\"urgency\":\"P1\",\"reason"
}
```

**Lo importante:**
- El validator no es una librería mágica — son `if/else` manuales sobre los campos esperados.
- `schemaValid` es un booleano limpio que el IF puede leer.
- El `rawContent` en el error te ayuda a debuggear qué devolvió realmente el LLM.

## 💡 Preguntas guía

1. **Cambiá el enum aceptado** a `['baja', 'alta']` en el Code validator. Corré un curl normal. ¿Qué error aparece ahora?
2. **Agregá una 3ra regla** al schema: que `reasoning` tenga al menos 20 caracteres. ¿Cuántas veces falla sobre 5 ejecuciones?
3. En vez de devolver error 400, **¿cómo harías un fallback por reglas** si el schema falla? (Spoiler: eso es el concepto 06).
4. ¿Por qué tener un **parser separado del validator** (vs todo junto)? Pista: separar sintaxis de semántica te permite auditar cada error por separado.
