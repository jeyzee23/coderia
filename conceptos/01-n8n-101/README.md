# Concepto 01 — n8n 101

## 🎯 Qué vas a aprender

Los **4 nodos fundamentales** de n8n en un solo workflow: cómo recibir un POST por webhook, procesar datos con JavaScript, bifurcar el flujo según una condición y devolver una respuesta. Este es el esqueleto de todo workflow que vas a construir después.

## 🧩 El workflow

```
Webhook (POST /concepto-01)
    ↓
Code — calcula hasCriticalVitals (SpO2 < 92)
    ↓
IF ¿vitales críticos?
    ├─ true  → 🚨 Respond Alerta
    └─ false → ✅ Respond OK
```

## 🧪 Cómo probarlo

**Caso crítico** (SpO2 bajo):

```bash
curl -X POST http://localhost:5678/webhook/concepto-01 \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"P-001","age":67,"vitals":{"spo2":88}}'
```

**Caso estable**:

```bash
curl -X POST http://localhost:5678/webhook/concepto-01 \
  -H 'Content-Type: application/json' \
  -d '{"patientId":"P-002","age":32,"vitals":{"spo2":98}}'
```

## 👀 Qué mirar

- Cómo el body llega en `$input.first().json.body` dentro del Code.
- Cómo el Code devuelve UN item: `return [{ json: {...} }]`.
- Cómo el IF compara `$json.hasCriticalVitals` con `true` y rutea a una de las dos salidas.
- Que ambos `Respond to Webhook` terminan el flujo y devuelven la respuesta HTTP.

**Respuesta esperada (caso crítico):**
```json
{
  "alert": true,
  "message": "🚨 Paciente con vitales críticos — derivar a guardia",
  "patient": { "patientId": "P-001", "age": 67, "spo2": 88, "hasCriticalVitals": true }
}
```

## 💡 Preguntas guía

1. **Cambiá el umbral** en el Code node: en vez de `spo2 < 92`, probá `spo2 < 95`. ¿Cómo cambia el resultado de los dos curls?
2. **Agregá otra condición** al Code: marcá como crítico también si `hr > 110`. Testeá con `"vitals":{"hr":120,"spo2":97}`.
3. **¿Qué pasa si mandás un body sin `vitals`?** Probá `-d '{"patientId":"X"}'`. ¿Por qué no rompe? (pista: `body.vitals || {}`).
