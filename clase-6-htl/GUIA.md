# Clase 6 - HITL con bots y notificaciones

> Practica educativa. No usar para decisiones clinicas reales.

## Objetivo

Armar un workflow Human-in-the-Loop donde una IA simulada propone una recomendacion, un humano aprueba/edita/rechaza y, si nadie responde, el sistema escala a supervisor.

```text
Entrada -> Politica HITL -> Notificacion -> Respuesta inmediata -> Wait -> Decision -> Resultado
```

## Layout visual recomendado

Ordenar el canvas de izquierda a derecha, en columnas:

```text
Columna 1: Webhook nuevo caso
Columna 2: Validar y anonimizar
Columna 3: Input valido?
Columna 4: Preparar politica HITL / Responder error
Columna 5: Notificar revisor
Columna 6: Preparar respuesta review requested
Columna 7: Responder review requested
Columna 8: Esperar decision humana
Columna 9: Parsear decision humana
Columna 10: Decision recibida?
Columna 11 arriba: Cierre decision humana
Columna 11 abajo: Escalar a supervisor -> Fallback seguro
Columna 12 centro: Armar respuesta final
```

Diagrama:

```text
Webhook nuevo caso
  -> Validar y anonimizar
  -> Input valido?
       false -> Responder error
       true  -> Preparar politica HITL
              -> Notificar revisor
              -> Preparar respuesta review requested
              -> Responder review requested
              -> Esperar decision humana
              -> Parsear decision humana
              -> Decision recibida?
                   true  -> Cierre decision humana
                   false -> Escalar a supervisor -> Fallback seguro
              -> Armar respuesta final
```

## Levantar n8n

```bash
cd /Users/juancavidela/Desktop/coder-ia/clase-6-htl
docker compose up -d
```

Abrir:

```text
http://localhost:5684
```

Tambien podes importar directamente `workflow.json`. Esta guia sirve para armarlo paso a paso en clase.

## Variables

Archivo `.env`:

```text
NOTIFICATION_WEBHOOK_URL=https://postman-echo.com/post
SUPERVISOR_WEBHOOK_URL=https://postman-echo.com/post
REVIEW_BASE_URL=http://localhost:5684
```

Con esos valores el workflow funciona sin configurar nada extra.

Si queres ver la notificacion en una pantalla externa, reemplazar por URLs de Webhook.site:

```text
NOTIFICATION_WEBHOOK_URL=https://webhook.site/TU-URL-DE-REVISOR
SUPERVISOR_WEBHOOK_URL=https://webhook.site/TU-URL-DE-SUPERVISOR
REVIEW_BASE_URL=http://localhost:5684
```

---

## Paso 1 - Webhook de entrada

Tipo de nodo:

```text
Webhook
```

Nombre:

```text
Webhook nuevo caso
```

Configuracion:

| Campo | Valor |
|-------|-------|
| HTTP Method | `POST` |
| Path | `hitl-review-request` |
| Response Mode | `Response Node` |

Endpoint final:

```text
POST http://localhost:5684/webhook/hitl-review-request
```

---

## Paso 2 - Validar y anonimizar

Tipo de nodo:

```text
Code
```

Nombre:

```text
Validar y anonimizar
```

Mode:

```text
Run Once for All Items
```

Codigo:

```javascript
// Este nodo recibe el body del Webhook y lo normaliza.
// En n8n, a veces el payload llega en json.body y otras directo en json.
const body = $input.first().json.body || $input.first().json || {};

// Campos minimos para poder operar el flujo HITL.
// Si falta alguno, no seguimos con la automatizacion.
const required = ['caseId', 'patientId', 'clinicalContext'];
const missing = required.filter((field) => !body[field]);

if (missing.length > 0) {
  return [{
    json: {
      valid: false,
      statusCode: 400,
      error: 'Faltan campos obligatorios: ' + missing.join(', ')
    }
  }];
}

// Hash simple para no arrastrar patientId en claro por logs y notificaciones.
// Es suficiente para clase; en produccion usar una estrategia de desidentificacion formal.
const hashId = (id) => {
  let h = 0;
  const value = String(id);
  for (let i = 0; i < value.length; i++) {
    h = ((h << 5) - h) + value.charCodeAt(i);
    h |= 0;
  }
  return 'hash_' + Math.abs(h).toString(36);
};

// Salida canonica para que todos los nodos siguientes trabajen con el mismo contrato.
return [{
  json: {
    valid: true,
    caseId: String(body.caseId),
    patientHash: hashId(body.patientId),
    domain: body.domain || 'salud',
    requestType: body.requestType || 'revision_clinica',
    clinicalContext: String(body.clinicalContext).trim(),
    aiRecommendation: String(body.aiRecommendation || '').trim(),
    riskLevel: String(body.riskLevel || 'medium').toLowerCase(),
    reviewer: body.reviewer || { name: 'Revisor asignado', role: 'especialista' },
    startedAtMs: Date.now()
  }
}];
```

Conexion:

```text
Webhook nuevo caso -> Validar y anonimizar
```

---

## Paso 3 - IF de input valido

Tipo de nodo:

```text
If
```

Nombre:

```text
Input valido?
```

Condicion:

| Campo | Valor |
|-------|-------|
| Value 1 | `{{ $json.valid }}` |
| Operation | `equals` |
| Value 2 | `true` |

Conexion:

```text
Validar y anonimizar -> Input valido?
```

---

## Paso 4 - Responder error

Tipo de nodo:

```text
Respond to Webhook
```

Nombre:

```text
Responder error
```

Configuracion:

| Campo | Valor |
|-------|-------|
| Respond With | `JSON` |
| Response Code | `400` |
| Response Body | `{{ { error: $json.error, statusCode: 400 } }}` |

Conexion:

```text
Input valido? false -> Responder error
```

---

## Paso 5 - Preparar politica HITL

Tipo de nodo:

```text
Code
```

Nombre:

```text
Preparar politica HITL
```

Codigo:

```javascript
const d = $input.first().json;

// Tabla de politicas para la demo.
// Usamos segundos para poder mostrar timeout en clase sin esperar minutos.
const policies = {
  critical: { score: 0.95, timeoutSeconds: 30 },
  high: { score: 0.82, timeoutSeconds: 60 },
  medium: { score: 0.62, timeoutSeconds: 120 },
  low: { score: 0.35, timeoutSeconds: 180 }
};

// Si llega un riskLevel desconocido, usamos medium como default conservador.
const policy = policies[d.riskLevel] || policies.medium;

// Simulamos una deteccion de sensibilidad buscando terminos de riesgo.
// Esto representa lo que en produccion podria decidir un modelo o un motor de reglas.
const text = (d.clinicalContext + ' ' + d.aiRecommendation).toLowerCase();
const sensitiveTerms = ['brca', 'patogenica', 'tratamiento', 'quimioterapia', 'diagnostico', 'critico', 'variante'];
const matchedSensitiveTerms = sensitiveTerms.filter((term) => text.includes(term));

// Pedimos revision humana si el score es medio/alto o si aparecen terminos sensibles.
const requiresHumanReview = policy.score >= 0.6 || matchedSensitiveTerms.length > 0;

// Si el caller no mando recomendacion, generamos una recomendacion conservadora.
const recommendation = d.aiRecommendation || (
  requiresHumanReview
    ? 'La IA detecto un caso sensible. Requiere revision humana antes de continuar.'
    : 'Caso de bajo riesgo. Registrar trazabilidad y continuar con controles habituales.'
);

// Dejamos separadas la evaluacion de IA y la politica HITL para que sea auditable.
return [{
  json: {
    ...d,
    aiAssessment: {
      model: 'simulated-hitl-policy-v1',
      recommendation,
      riskScore: policy.score,
      confidence: matchedSensitiveTerms.length > 0 ? 0.78 : 0.58,
      matchedSensitiveTerms
    },
    hitlPolicy: {
      requiresHumanReview,
      interventionPoint: 'antes_de_emitir_recomendacion_final',
      timeoutSeconds: policy.timeoutSeconds,
      fallbackAction: 'escalar_a_supervisor',
      autoApproveAllowed: false
    }
  }
}];
```

Conexion:

```text
Input valido? true -> Preparar politica HITL
```

Que explica este nodo:

- simula una evaluacion de IA
- define el punto de intervencion humana
- define timeout por riesgo
- prohibe aprobacion automatica

---

## Paso 6 - Notificar revisor

Tipo de nodo:

```text
HTTP Request
```

Nombre:

```text
Notificar revisor
```

Configuracion:

| Campo | Valor |
|-------|-------|
| Method | `POST` |
| URL | `{{ $env.NOTIFICATION_WEBHOOK_URL || 'https://postman-echo.com/post' }}` |
| Send Headers | `true` |
| Body Content Type | `JSON` |
| Timeout | `5000` |
| Retry on Fail | `true` |
| Max Tries | `3` |
| Wait Between Tries | `2000` |
| On Error | `Continue Regular Flow` |

Header:

| Name | Value |
|------|-------|
| `Content-Type` | `application/json` |

JSON Body:

```javascript
{{ (() => {
  const resumeUrl = $execution.resumeUrl;
  const approvalUrl = resumeUrl.includes('?')
    ? resumeUrl.replace('?', '/decision?')
    : resumeUrl + '/decision';

  return JSON.stringify({
    event: 'human_review_requested',
    caseId: $json.caseId,
    patientHash: $json.patientHash,
    domain: $json.domain,
    requestType: $json.requestType,
    reviewer: $json.reviewer,
    riskLevel: $json.riskLevel,
    riskScore: $json.aiAssessment.riskScore,
    recommendation: $json.aiAssessment.recommendation,
    timeoutSeconds: $json.hitlPolicy.timeoutSeconds,
    approvalUrl,
    method: 'POST',
    expectedBody: {
      decision: 'approved | edited | rejected',
      reviewerId: 'string',
      comments: 'string',
      editedRecommendation: 'string opcional'
    }
  });
})() }}
```

Conexion:

```text
Preparar politica HITL -> Notificar revisor
```

Nota:

```text
approvalUrl es la URL que el revisor debe llamar para reanudar el workflow. Como el Wait usa Webhook Suffix = `decision`, la URL correcta termina en `/decision?signature=...`.
```

---

## Paso 7 - Preparar respuesta inmediata

El nodo `HTTP Request` de notificacion cambia el `$json`. Por eso antes de responder al webhook inicial reconstruimos el body desde `Preparar politica HITL`.

Tipo de nodo:

```text
Code
```

Nombre:

```text
Preparar respuesta review requested
```

Codigo:

```javascript
// Este nodo arma la respuesta inmediata del webhook inicial.
// Es necesario porque el HTTP Request de notificacion cambia el $json.
const d = $('Preparar politica HITL').first().json;

// El Wait tiene Webhook Suffix = "decision".
// Por eso la URL usable debe ser /webhook-waiting/{id}/decision?signature=...
const resumeUrl = $execution.resumeUrl;
const approvalUrl = resumeUrl.includes('?')
  ? resumeUrl.replace('?', '/decision?')
  : resumeUrl + '/decision';

// El alumno copia approvalUrl desde esta respuesta y la usa para aprobar, editar o rechazar.
return [{
  json: {
    status: 'review_requested',
    message: 'Caso recibido. El workflow queda esperando decision humana.',
    caseId: d.caseId,
    patientHash: d.patientHash,
    approvalUrl,
    approvalMethod: 'POST',
    timeoutSeconds: d.hitlPolicy.timeoutSeconds,
    expectedBody: {
      decision: 'approved | edited | rejected',
      reviewerId: 'string',
      comments: 'string',
      editedRecommendation: 'string opcional'
    }
  }
}];
```

Conexion:

```text
Notificar revisor -> Preparar respuesta review requested
```

---

## Paso 8 - Responder approvalUrl al request inicial

Antes del `Wait`, agregamos una respuesta inmediata al webhook inicial. Esto evita que Postman quede cargando hasta el timeout.

Tipo de nodo:

```text
Respond to Webhook
```

Nombre:

```text
Responder review requested
```

Configuracion:

| Campo | Valor |
|-------|-------|
| Respond With | `JSON` |
| Response Code | `202` |
| Response Body | ver bloque de abajo |

Response Body:

```javascript
{{ $json }}
```

Conexion:

```text
Preparar respuesta review requested -> Responder review requested
```

Ahora si, despues de responder al request inicial, el workflow sigue en background y queda esperando al humano.

---

## Paso 9 - Esperar decision humana

Tipo de nodo:

```text
Wait
```

Nombre:

```text
Esperar decision humana
```

Configuracion:

| Campo | Valor |
|-------|-------|
| Resume | `On Webhook Call` |
| HTTP Method | `POST` |
| Response Code | `200` |
| Response Mode | `On Received` |
| Response Data | `First Entry JSON` |
| Limit Wait Time | `true` |
| Limit Type | `After Time Interval` |
| Amount | `{{ $('Preparar politica HITL').first().json.hitlPolicy.timeoutSeconds }}` |
| Unit | `Seconds` |
| Options -> Webhook Suffix | `decision` |

Conexion:

```text
Responder review requested -> Esperar decision humana
```

Body esperado para aprobar:

```json
{
  "decision": "approved",
  "reviewerId": "rev-gen-01",
  "comments": "Apruebo la recomendacion. Requiere firma profesional antes de emitir."
}
```

Decisiones aceptadas:

```text
approved
edited
rejected
```

---

## Paso 10 - Parsear decision humana

Tipo de nodo:

```text
Code
```

Nombre:

```text
Parsear decision humana
```

Codigo:

```javascript
// Recuperamos el caso original desde el nodo de politica.
// El Wait devuelve solamente lo que llega al webhook de aprobacion.
const original = $('Preparar politica HITL').first().json;
const current = $input.first().json || {};
const body = current.body || current;

// Solo aceptamos decisiones conocidas.
// Si no llega ninguna, interpretamos que el Wait vencio por timeout.
const allowed = ['approved', 'edited', 'rejected'];
const decision = String(body.decision || '').toLowerCase();
const received = allowed.includes(decision);

// Si el humano edita, usamos su version como recomendacion final.
// Si aprueba o rechaza, conservamos la recomendacion original de la IA.
const finalRecommendation = decision === 'edited'
  ? String(body.editedRecommendation || original.aiAssessment.recommendation)
  : original.aiAssessment.recommendation;

// Solo approved y edited permiten continuar.
const canProceed = decision === 'approved' || decision === 'edited';

return [{
  json: {
    ...original,
    humanReview: {
      received,
      decision: received ? decision : 'timeout',
      reviewerId: body.reviewerId || null,
      comments: body.comments || '',
      editedRecommendation: body.editedRecommendation || '',
      reviewedAt: received ? new Date().toISOString() : null
    },
    finalDecision: {
      status: received ? decision : 'pending_supervisor_review',
      recommendation: received ? finalRecommendation : 'No emitir resultado. Caso pendiente de supervisor por timeout.',
      canProceed,
      requiresSupervisor: !received || decision === 'rejected'
    }
  }
}];
```

Conexion:

```text
Esperar decision humana -> Parsear decision humana
```

---

## Paso 11 - IF decision recibida

Tipo de nodo:

```text
If
```

Nombre:

```text
Decision recibida?
```

Condicion:

| Campo | Valor |
|-------|-------|
| Value 1 | `{{ $json.humanReview.received }}` |
| Operation | `equals` |
| Value 2 | `true` |

Conexion:

```text
Parsear decision humana -> Decision recibida?
```

---

## Paso 12 - Cierre decision humana

Tipo de nodo:

```text
Code
```

Nombre:

```text
Cierre decision humana
```

Codigo:

```javascript
const d = $input.first().json;

// Esta rama se ejecuta cuando hubo respuesta humana.
// No la marcamos como fallback aunque el humano haya rechazado.
return [{
  json: {
    ...d,
    fallbackUsed: false,
    escalation: {
      // Si el humano rechaza, el caso queda para supervisor por discrepancia.
      escalated: d.finalDecision.requiresSupervisor,
      reason: d.humanReview.decision === 'rejected' ? 'human_rejected_ai_recommendation' : null,
      nextRole: d.humanReview.decision === 'rejected' ? 'supervisor_clinico' : null,
      action: d.humanReview.decision === 'rejected' ? 'revisar_discrepancia' : 'continuar_con_trazabilidad'
    }
  }
}];
```

Conexion:

```text
Decision recibida? true -> Cierre decision humana
```

---

## Paso 13 - Escalar a supervisor

Tipo de nodo:

```text
HTTP Request
```

Nombre:

```text
Escalar a supervisor
```

Configuracion:

| Campo | Valor |
|-------|-------|
| Method | `POST` |
| URL | `{{ $env.SUPERVISOR_WEBHOOK_URL || $env.NOTIFICATION_WEBHOOK_URL || 'https://postman-echo.com/post' }}` |
| Send Headers | `true` |
| Body Content Type | `JSON` |
| Timeout | `5000` |
| Retry on Fail | `true` |
| Max Tries | `3` |
| Wait Between Tries | `3000` |
| On Error | `Continue Regular Flow` |

Header:

| Name | Value |
|------|-------|
| `Content-Type` | `application/json` |

JSON Body:

```javascript
{{ JSON.stringify({
  event: 'human_review_timeout_escalated',
  caseId: $json.caseId,
  patientHash: $json.patientHash,
  riskLevel: $json.riskLevel,
  timeoutSeconds: $json.hitlPolicy.timeoutSeconds,
  previousReviewer: $json.reviewer,
  blockedRecommendation: $json.aiAssessment.recommendation,
  actionRequired: 'supervisor_review_required',
  ts: new Date().toISOString()
}) }}
```

Conexion:

```text
Decision recibida? false -> Escalar a supervisor
```

---

## Paso 14 - Fallback seguro

Tipo de nodo:

```text
Code
```

Nombre:

```text
Fallback seguro
```

Codigo:

```javascript
// Esta rama se usa cuando el Wait vencio y no hubo decision humana.
const d = $('Parsear decision humana').first().json;

// Regla clave HITL: timeout no significa aprobacion automatica.
// Se bloquea la emision y se escala a supervisor.
return [{
  json: {
    ...d,
    fallbackUsed: true,
    escalation: {
      escalated: true,
      reason: 'human_review_timeout',
      nextRole: 'supervisor_clinico',
      action: 'bloquear_emision_y_requerir_revision_supervisora'
    },
    finalDecision: {
      status: 'pending_supervisor_review',
      recommendation: 'No emitir resultado automaticamente. Se escalo a supervisor por falta de respuesta humana.',
      canProceed: false,
      requiresSupervisor: true
    }
  }
}];
```

Conexion:

```text
Escalar a supervisor -> Fallback seguro
```

---

## Paso 15 - Armar respuesta final

Tipo de nodo:

```text
Code
```

Nombre:

```text
Armar respuesta final
```

Codigo:

```javascript
const d = $input.first().json;
const now = Date.now();

// Latencia total desde que entro el caso al webhook inicial.
const latencyMs = d.startedAtMs ? now - d.startedAtMs : null;

// Si hubo revision humana, calculamos cuanto tardo en responder.
const reviewedAtMs = d.humanReview.reviewedAt ? new Date(d.humanReview.reviewedAt).getTime() : null;
const humanResponseMs = reviewedAtMs && d.startedAtMs ? reviewedAtMs - d.startedAtMs : null;

// Metricas operativas para dashboard o analisis posterior.
const metrics = {
  latencyMs,
  humanResponseMs,
  timeoutSeconds: d.hitlPolicy.timeoutSeconds,
  riskScore: d.aiAssessment.riskScore,
  aiConfidence: d.aiAssessment.confidence,
  fallbackUsed: d.fallbackUsed === true,
  escalated: d.escalation?.escalated === true,
  canProceed: d.finalDecision.canProceed === true
};

// Log estructurado: un evento por ejecucion completada.
const log = {
  event: 'hitl_review_completed',
  ts: new Date(now).toISOString(),
  caseId: d.caseId,
  patientHash: d.patientHash,
  domain: d.domain,
  requestType: d.requestType,
  riskLevel: d.riskLevel,
  reviewerRole: d.reviewer.role,
  humanDecision: d.humanReview.decision,
  fallbackUsed: metrics.fallbackUsed,
  escalated: metrics.escalated,
  latencyMs,
  humanResponseMs,
  timeoutSeconds: d.hitlPolicy.timeoutSeconds
};

// Respuesta final pensada para ser facil de leer en Postman y en clase.
return [{
  json: {
    caseId: d.caseId,
    patientHash: d.patientHash,
    workflow: {
      pattern: 'human-in-the-loop',
      interventionPoint: d.hitlPolicy.interventionPoint,
      autoApproveAllowed: d.hitlPolicy.autoApproveAllowed
    },
    aiAssessment: d.aiAssessment,
    humanReview: d.humanReview,
    finalDecision: d.finalDecision,
    escalation: d.escalation,
    metrics,
    log
  }
}];
```

Conexiones:

```text
Cierre decision humana -> Armar respuesta final
Fallback seguro -> Armar respuesta final
```

---

## Paso 16 - Responder OK

No agregamos otro `Respond to Webhook` al final.

Motivo:

```text
El webhook inicial ya respondio en `Responder review requested`.
La parte posterior al Wait corre asincronicamente.
El resultado final se ve en la ejecucion de n8n, nodo `Armar respuesta final`.
```

---

## Conexiones completas

```text
Webhook nuevo caso
  -> Validar y anonimizar
  -> Input valido?
       false -> Responder error
       true -> Preparar politica HITL
         -> Notificar revisor
         -> Preparar respuesta review requested
         -> Responder review requested
         -> Esperar decision humana
         -> Parsear decision humana
         -> Decision recibida?
              true -> Cierre decision humana
              false -> Escalar a supervisor -> Fallback seguro
         -> Armar respuesta final
```

---

## Probar con Postman

Importar:

```text
postman_collection.json
```

Requests principales:

| Request | Uso |
|---------|-----|
| `1 - Crear caso HITL high risk` | inicia caso y espera aprobacion |
| `2 - Crear caso critical para probar timeout rapido` | probar fallback sin responder |
| `3 - Responder approvalUrl - approved` | aprobar |
| `4 - Responder approvalUrl - edited` | editar |
| `5 - Responder approvalUrl - rejected` | rechazar |
| `6 - Error esperado por campos faltantes` | validar error 400 |

Flujo de prueba:

1. Ejecutar request `1`.
2. Copiar `approvalUrl` desde la respuesta del request `1`.
3. Pegar en variable Postman `approval_url`.
4. Ejecutar request `3`, `4` o `5`.
5. Mirar la ejecucion en n8n, nodo `Armar respuesta final`.

---

## Payload inicial

```json
{
  "caseId": "CASE-HTL-001",
  "patientId": "PAC-991",
  "domain": "genomica",
  "requestType": "validacion_variante",
  "clinicalContext": "Paciente con antecedente familiar de cancer de mama temprano. Se detecta variante BRCA1 c.5266dupC.",
  "aiRecommendation": "Clasificar como patogenica y solicitar revision por genetista antes de emitir informe.",
  "riskLevel": "high",
  "reviewer": {
    "name": "Dra. Alvarez",
    "role": "genetista_clinica"
  }
}
```

---

## Politicas de espera

En demo:

| Riesgo | Timeout |
|--------|---------|
| `critical` | 30 segundos |
| `high` | 60 segundos |
| `medium` | 120 segundos |
| `low` | 180 segundos |

Regla:

```text
Si no responde el humano, no se aprueba automaticamente.
Se escala a supervisor y se bloquea la emision.
```

---

## Entregable Google Docs

Debe incluir:

1. Descripcion del workflow HITL.
2. Diagrama del flujo.
3. APIs REST y webhooks usados.
4. Politicas de espera y fallback.
5. Logs y metricas.
6. Simulacion con roles y tiempos.

Metricas clave:

- `latencyMs`
- `humanResponseMs`
- `fallbackUsed`
- `escalated`
- tasa de aprobacion
- tasa de edicion
- tasa de rechazo
- tasa de timeout
