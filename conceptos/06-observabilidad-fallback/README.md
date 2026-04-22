# Concepto 06 — Observabilidad + Fallback

## 🎯 Qué vas a aprender

Dos conceptos que van juntos porque ambos responden a **"qué hacer cuando algo puede salir mal":**

1. **Fallback:** si la IA falla (timeout, 5xx, sin content), clasificamos con reglas deterministas. El flujo nunca se corta.
2. **Observabilidad:** cada ejecución genera un log JSON estructurado con latencia, tokens usados, si se usó fallback, etc. Eso es lo que después alimenta tu dashboard (Grafana, Datadog, CloudWatch).

## 🧩 El workflow

```
Webhook (POST /concepto-06)
    ↓
Code — Start timer (guarda startedAtMs)
    ↓
HTTP Request LLM (timeout: 1500ms, para forzar fallos)
    ↓
IF ¿IA respondió OK?
    ├─ sí → Code Parse IA ──┐
    └─ no → Code Fallback ──┤
                             ↓
                   Code — Log JSON (latencia, tokens, fallbackUsed)
                             ↓
                        Respond OK
```

## 🧪 Cómo probarlo

```bash
curl -X POST http://localhost:5678/webhook/concepto-06 \
  -H 'Content-Type: application/json' \
  -d '{
    "age": 67,
    "symptoms": "dolor toracico intenso",
    "vitals": { "spo2": 91, "hr": 115 }
  }'
```

Con **timeout 1500ms**, el LLM no siempre alcanza a responder → vas a ver el fallback activarse. Si querés ver ambas ramas, subí el timeout a 10000ms en el nodo LLM.

## 👀 Qué mirar

**Respuesta con fallback activado (timeout):**
```json
{
  "triage": {
    "priority": "P1",
    "reasoning": "FALLBACK: SpO2 crítico (<92)."
  },
  "log": {
    "event": "triage_completed",
    "ts": "2026-04-21T...",
    "priority": "P1",
    "fallbackUsed": true,
    "tokensUsed": 0,
    "latencyMs": 1523
  }
}
```

**Respuesta con IA OK:**
```json
{
  "triage": {
    "priority": "P1",
    "reasoning": "Sospecha de síndrome coronario agudo..."
  },
  "log": {
    "event": "triage_completed",
    "ts": "2026-04-21T...",
    "priority": "P1",
    "fallbackUsed": false,
    "tokensUsed": 142,
    "latencyMs": 2341
  }
}
```

**Lo importante:**
- **Ambas ramas (IA y fallback) producen el mismo shape** (`priority` + `reasoning`). Esa es la regla de oro del fallback: no rompas el contrato del flujo.
- El `log` tiene las 4-5 métricas críticas que necesitás para operar: latencia, si se usó fallback, tokens, timestamp.
- `startedAtMs` se guarda al inicio. La latencia se calcula al final con `Date.now() - startedAtMs`. Patrón universal.

## 💡 Preguntas guía

1. **Subí el timeout a 10000ms** en el LLM. Corré el curl 5 veces. ¿Cuántas veces se activa el fallback ahora? ¿Qué cambia en `latencyMs`?
2. **Agregá una regla nueva al fallback**: si `age > 80` → siempre P1. Probá con un paciente de 85 años.
3. **¿Qué otras métricas agregarías al log?** Pista clásica: `modelVersion`, `errorType`, `retryCount`, `inputTokens`/`outputTokens` separados.
4. **¿Cómo dispararías una alerta a Slack** cuando `fallbackUsed: true` o `latencyMs > 5000`? Pista: IF + HTTP Request al webhook de Slack. (Spoiler: eso es lo que hace clase-2 completo).
5. Si en tu log real ves `fallbackUsed: true` en el 30% de las requests → ¿qué investigarías primero?

## 🔗 Cómo esto se conecta con los workflows madre

En `clase-2/workflow.json`, este mismo patrón aparece pero más rico:
- Log con 13 campos (vs 4 acá)
- Alerta HTTP adicional cuando `shouldAlert` es true
- `fallbackReason` distingue entre 3 motivos (timeout / parse fail / schema fail)
- Override por vitales que fuerza prioridad mínima

Acá simplificamos para que veas el **patrón esencial** sin ruido.
