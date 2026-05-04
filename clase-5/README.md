# Clase 5

Multimodalidad aplicada a biomédica con foco en **modelos de audio**, STT, TTS, reconocimiento de imagen, chunking, embeddings, fallback y evaluación automática.

> Proyecto educativo. No usar para decisiones clínicas reales.

## Qué construye esta clase

- Un workflow importable en n8n para un caso biomédico multimodal.
- Recepción de imagen médica + audio clínico por webhook.
- STT real con **AssemblyAI** cuando llega `audioUrl`, o reutilización de `audioTranscript` para demo sincronizada.
- Reconocimiento de imagen simulado con API pública de transporte y parseo local, válido para la consigna.
- Chunking de transcripciones largas.
- Embeddings reales con **Cohere** y retrieval semántico sobre una base clínica pequeña.
- Fallback seguro cuando la evidencia es débil o la calidad cae.
- Preparación de salida TTS lista para conectar a **ElevenLabs**.
- Evaluación automática con métricas visibles en la respuesta.

## Caso de uso

Se modela un **asistente de documentación clínica** que recibe:

- una imagen médica o una descripción estructurada de hallazgos
- una nota de voz del profesional o una transcripción previa

El flujo:

1. normaliza y anonimiza el input
2. extrae etiquetas visuales
3. transcribe o reutiliza la transcripción
4. divide el texto en chunks
5. busca contexto clínico relevante con embeddings simulados
6. genera un resumen multimodal breve
7. evalúa calidad y grounding
8. si la calidad no alcanza, aplica fallback
9. prepara un payload TTS para reproducir la respuesta

## Setup

Clase 5 corre en **puerto 5682**.

```bash
cd /Users/juancavidela/Desktop/coder-ia/clase-5
cp .env.example .env
# completar al menos:
# - ASSEMBLYAI_API_KEY
# - COHERE_API_KEY
# - NOTIFICATION_WEBHOOK_URL
docker compose up -d
```

UI de n8n:

`http://localhost:5682`

## Importar el workflow

1. Abrir `http://localhost:5682`
2. Crear usuario owner
3. `Workflows -> Import from file -> workflow.json`
4. Activar el workflow

## Endpoint

- `POST /webhook/biomedical-multimodal-audio`

## Servicios integrados

- **Imagen**: API pública simulada con `postman-echo` + parseo de hallazgos
- **STT**: AssemblyAI
- **Embeddings**: Cohere
- **Notificaciones de fallback**: `NOTIFICATION_WEBHOOK_URL` (por ejemplo Webhook.site)
- **TTS**: payload listo para ElevenLabs

## Payload de ejemplo

```json
{
  "patientId": "P-5001",
  "imageStudyType": "radiografia_torax",
  "imageFindingsText": "Opacidad bibasal leve con infiltrado en base derecha y sin derrame pleural.",
  "audioTranscript": "Paciente masculino de 68 años con tos, fiebre y disnea progresiva desde hace 48 horas. Saturación reportada 93 por ciento. Se solicita correlacion clínica y control en menos de 24 horas.",
  "audioLanguage": "es"
}
```

## Opcion con STT real

Si querés probar AssemblyAI dentro del mismo flujo, en vez de `audioTranscript` enviá un `audioUrl` público:

```json
{
  "patientId": "P-5003",
  "imageStudyType": "radiografia_torax",
  "imageFindingsText": "Infiltrado basal derecho y opacidad bibasal leve.",
  "audioUrl": "https://assembly.ai/wildfires.mp3",
  "audioLanguage": "es"
}
```

## Probar con curl

```bash
curl -X POST http://localhost:5682/webhook/biomedical-multimodal-audio \
  -H 'Content-Type: application/json' \
  -d '{
    "patientId": "P-5001",
    "imageStudyType": "radiografia_torax",
    "imageFindingsText": "Opacidad bibasal leve con infiltrado en base derecha y sin derrame pleural.",
    "audioTranscript": "Paciente masculino de 68 años con tos, fiebre y disnea progresiva desde hace 48 horas. Saturacion reportada 93 por ciento. Se solicita correlacion clinica y control en menos de 24 horas.",
    "audioLanguage": "es"
  }'
```

## Respuesta esperada

La respuesta devuelve:

- `summary`
- `imageAnalysis`
- `stt`
- `chunks`
- `retrieval`
- `evaluation`
- `tts`
- `log`

## Arquitectura

```text
Webhook
  -> Validar + anonimizar
  -> Analisis de imagen
  -> STT / transcripcion
  -> Chunking
  -> Embeddings simulados + retrieval
  -> Resumen multimodal
  -> Evaluacion automatica
  -> IF calidad suficiente
       -> Preparar TTS
       -> Log estructurado
       -> Responder
     else
       -> Fallback seguro
       -> Preparar TTS
       -> Log estructurado
       -> Responder
```

## Qué está simulado y qué es real

- el reconocimiento de imagen sigue simulado, porque la consigna lo permite y evita meter un servicio médico no gratuito
- el STT puede ser real vía AssemblyAI si llega `audioUrl`
- los embeddings pueden ser reales vía Cohere
- la base clínica sigue embebida dentro del workflow a propósito, para que la búsqueda semántica sea transparente en clase

Los puntos de reemplazo naturales en producción son:

- nodo de imagen por un servicio real de computer vision
- nodo STT por Whisper/Groq o equivalente si querés menor latencia
- nodo TTS por ElevenLabs
- retrieval local por Qdrant, pgvector o servicio vectorial administrado

## Métricas que deja visibles

- `transcriptionQuality`
- `imageConfidence`
- `retrievalTopScore`
- `groundingScore`
- `overallScore`
- `fallbackUsed`
- `latencyMs`

## Fallback implementado

El flujo degrada a respuesta segura cuando:

- falta transcripción y no hay forma de resolverla
- la similitud semántica es baja
- el score global de evaluación queda por debajo del umbral

En fallback:

- el resumen evita inferencias clínicas fuertes
- fuerza `requiresHumanReview: true`
- arma una salida TTS breve y conservadora

## Trade-off cloud vs on-premise

### Cloud

- integración más rápida
- mejor elasticidad
- menor costo inicial
- mayor complejidad de cumplimiento y transferencia de datos

### On-premise

- mayor control sobre PHI y trazabilidad
- menor exposición externa
- más costo operativo
- más trabajo de MLOps, observabilidad y hardware

## Archivos

```text
clase-5/
├── README.md
├── docker-compose.yml
├── entregable-modelo.md
├── postman_collection.json
└── workflow.json
```
