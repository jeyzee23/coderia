# Entregable modelo — Clase 3

**Autor:** [Tu nombre]  
**Fecha:** [Completar]  
**Curso:** AI Automation Avanzado — Clase 3

> Este documento funciona como referencia de entregable para la clase de RAG. Toma como caso implementado un asistente documental clínico con trazabilidad y compara sus decisiones con lo que cambiaría en otros dominios.

---

## 1. Resumen ejecutivo

Se diseñó un pipeline de **Retrieval-Augmented Generation (RAG)** orientado a healthcare, implementado en n8n y organizado en dos niveles:

- un **workflow padre** que resuelve el flujo completo
- una serie de **workflows parciales** que descomponen el pipeline en chunking, embeddings, retrieval, generation y guardrails

El objetivo del sistema no es diagnosticar ni recomendar tratamientos, sino **responder preguntas documentales con fuentes citadas** sobre una base de prospectos y guías clínicas simuladas.

La arquitectura aplicada sigue esta lógica:

1. recibir una pregunta
2. recuperar los fragmentos más relevantes de una base de conocimiento
3. inyectar solo esos fragmentos al prompt
4. pedir una respuesta grounded al modelo
5. validar fuentes y degradar a un fallback seguro si la evidencia es débil o la salida es inválida

Esta decisión es especialmente relevante en healthcare porque:

- la información cambia
- las respuestas deben ser trazables
- la alucinación del modelo es inaceptable
- los resultados tienen que quedar listos para revisión humana

---

## 2. Problema que RAG resuelve

Una LLM por sí sola no funciona como una base de conocimiento viva. Aunque razone bien sobre el texto que recibe, no puede cargar de forma práctica todos los documentos, protocolos o prospectos de una organización en cada consulta.

Si intentáramos resolverlo enviando toda la base documental al modelo:

- el costo crecería mucho
- la latencia aumentaría
- se mezclaría información relevante con ruido
- sería difícil justificar qué fuente sostiene cada frase

RAG corrige ese problema separando el proceso en dos etapas:

1. **retrieval**: el sistema busca qué fragmentos son más relevantes para la consulta
2. **generation**: la LLM recibe solo esos fragmentos y produce una respuesta fundada

En este entregable, el retrieval se simula dentro de n8n con embeddings hashed y cosine similarity. Aunque no es un stack de producción, permite mostrar de forma transparente el comportamiento del patrón.

---

## 3. Dataset y estrategia de chunking

La base documental usada contiene dos tipos de materiales:

- **prospectos**: ibuprofeno, metformina y amoxicilina
- **guías clínicas**: dolor torácico, náuseas / dolor abdominal y disnea

Cada documento se modela con:

- `docId`
- `title`
- `category`
- `version`
- `tags`
- `sections[]`

### Criterio de chunking

El chunking usado es **semántico por secciones**:

- cada sección del documento es el punto de partida
- si una sección es extensa, se divide en grupos cortos de oraciones
- no se usa overlap en esta versión

La decisión se justifica porque en un dominio clínico importa preservar unidades de significado como:

- “efectos adversos”
- “poblaciones especiales”
- “signos de alarma”
- “triage inicial”

Partir un documento solo cada N caracteres podría romper relaciones importantes entre síntomas, alertas y restricciones clínicas. Por eso el chunking semántico es más defendible que un corte puramente técnico.

---

## 4. Embeddings simulados y búsqueda semántica

En este prototipo no se usó una API real de embeddings. En cambio, se implementó una representación numérica simplificada:

- normalización del texto
- mapeo de algunos sinónimos
- hashed bag-of-words de 64 dimensiones

Esto no apunta a precisión de producción. Su función es didáctica:

- mostrar que los textos pasan a vectores
- hacer visible el ranking semántico
- mantener toda la lógica dentro de n8n

La consulta del usuario se vectoriza igual que los chunks. Luego se calcula un score combinado:

- similitud coseno
- pequeño refuerzo por overlap lexical

Con eso se ordenan los candidatos y se toman los `top_k` más relevantes.

### Ejemplo conceptual

Consulta:

> “Qué prospectos mencionan dolor abdominal y náuseas en adultos mayores?”

El retrieval eleva chunks de:

- ibuprofeno
- metformina
- amoxicilina

porque contienen combinaciones de:

- dolor abdominal
- náuseas
- molestias gastrointestinales
- adultos mayores

Aunque la consulta no copie literalmente el texto del prospecto, la representación vectorial aproximada permite acercarlos semánticamente.

---

## 5. Generation grounded con fuentes

Una vez recuperados los chunks, la LLM recibe:

- la pregunta
- los fragmentos rankeados
- una instrucción estricta para devolver JSON válido

El contrato de salida esperado es:

```json
{
  "answer": "respuesta breve y trazable",
  "sources": [
    {
      "chunkId": "id",
      "docId": "id",
      "title": "titulo",
      "section": "seccion"
    }
  ],
  "confidence": "alta|media|baja",
  "requiresHumanReview": true
}
```

Esto fuerza una separación clara:

- el retrieval trae evidencia
- la LLM sintetiza
- el sistema valida que las fuentes citadas existan de verdad

La respuesta, por diseño, no pretende reemplazar criterio médico profesional. Funciona como **asistente de búsqueda documental**.

---

## 6. Guardrails, fallback y observabilidad

En healthcare no alcanza con que el modelo “parezca razonable”. Se agregaron tres capas de control:

### 6.1 Guardrails

Se valida:

- que haya JSON
- que `answer` no esté vacío
- que `sources[]` exista
- que las fuentes citadas correspondan a chunks realmente recuperados

### 6.2 Fallback seguro

Si la evidencia es débil o la salida del modelo es inválida:

- no se acepta la respuesta del LLM
- se devuelve una salida segura
- se listan las mejores fuentes encontradas
- se fuerza `requiresHumanReview: true`

### 6.3 Log estructurado

Cada ejecución produce un log con:

- `latencyMs`
- `fallbackUsed`
- `fallbackReason`
- `returnedChunks`
- `topScore`
- `scopeUsed`
- `sourceType`

Eso permite instrumentar análisis posteriores sobre robustez, calidad del retrieval y necesidad de revisión humana.

---

## 7. Comparación conceptual con otro dominio

El mismo patrón RAG podría usarse en entretenimiento, por ejemplo para recomendar películas. Sin embargo, los parámetros cambiarían:

### En películas

- tolerancia mayor a omisiones
- top-k más bajo
- impacto más liviano de una respuesta imperfecta
- la LLM puede rankear resultados con más libertad

### En prospectos biomédicos

- tolerancia muy baja a omisiones relevantes
- prioridad de trazabilidad
- necesidad de revisión humana
- fallback seguro obligatorio

Esto muestra que **RAG no es una receta fija**. Chunking, retrieval y guardrails dependen del dominio.

---

## 8. Limitaciones actuales y evolución

El sistema implementado no es todavía un stack de producción. Sus límites principales son:

- embeddings simulados
- base documental en memoria
- sin persistencia de knowledge base viva
- sin re-ranking
- sin evaluación automática avanzada

La evolución natural sería:

1. reemplazar embeddings simulados por embeddings reales
2. conectar una base vectorial como Qdrant o pgvector
3. mover la ingesta documental al principio del pipeline
4. sumar evaluación y monitoreo más formales

Lo importante es que la clase deja clara la arquitectura base. Cambiar la implementación del retrieval no cambia el patrón conceptual.

---

## 9. Conclusión

El valor principal de RAG en healthcare no es “hacer que el modelo sepa más”, sino **hacer que responda sobre evidencia recuperada, trazable y verificable**.

El prototipo de clase 3 muestra ese principio de forma transparente porque:

- separa retrieval de generation
- expone el pipeline paso a paso
- hace visibles los contratos de datos
- incorpora una respuesta segura cuando la evidencia no alcanza

Ese enfoque prepara a los alumnos para una siguiente etapa donde el mismo diseño se conecte a embeddings reales, vector stores y parsing documental productivo.
