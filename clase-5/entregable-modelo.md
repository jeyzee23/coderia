# Entregable modelo — Clase 5

**Autor:** [Tu nombre]  
**Fecha:** [Completar]  
**Curso:** AI Automation Avanzado — Clase 5

---

## 1. Caso de uso y objetivo

El flujo diseñado corresponde a un **asistente multimodal biomédico** orientado a documentación clínica y soporte operativo, no a diagnóstico autónomo. El sistema recibe dos fuentes principales de información:

- una imagen médica o una descripción estructurada de sus hallazgos
- una nota de voz del profesional tratante

El objetivo es transformar esas entradas heterogéneas en una **salida estructurada, trazable y reusable**, compuesta por:

- transcripción clínica
- etiquetas visuales relevantes
- contexto documental recuperado semánticamente
- resumen multimodal breve
- texto optimizado para respuesta hablada mediante TTS

En un entorno real, este patrón podría usarse para:

- asistir la redacción de historias clínicas
- resumir interconsultas
- generar notas de evolución preliminares
- dar soporte a centros de imágenes con alta carga operativa

La decisión central del diseño fue priorizar **seguridad, trazabilidad y degradación segura** por encima de cobertura o autonomía. Por ese motivo, el workflow incorpora chunking, retrieval con embeddings, métricas automáticas y políticas explícitas de fallback.

---

## 2. Diagrama del flujo

```text
Webhook multimodal
  -> Validación y anonimización
  -> Reconocimiento de imagen
  -> STT / reutilización de transcripción
  -> Chunking de la nota de voz
  -> Embeddings simulados
  -> Búsqueda semántica en base clínica
  -> Resumen multimodal
  -> Evaluación automática
  -> IF score suficiente
       -> Preparar payload TTS
       -> Log estructurado
       -> Respuesta final
     else
       -> Fallback seguro
       -> Preparar payload TTS
       -> Log estructurado
       -> Respuesta final
```

### Explicación de cada componente

**1. Webhook de entrada**  
El flujo se dispara mediante un webhook `POST` que recibe un JSON con identificador del paciente, tipo de estudio, hallazgos textuales de imagen y audio clínico o transcripción previa. Esto permite integrarlo fácilmente con Make, formularios internos, sistemas RIS/PACS o apps móviles.

**2. Validación y anonimización**  
Antes de cualquier procesamiento, el flujo verifica que existan campos mínimos y reemplaza el identificador del paciente por un hash. Esta decisión reduce exposición de datos sensibles en logs y en ramas intermedias del workflow.

**3. Reconocimiento de imagen**  
En el prototipo de clase, el análisis visual está simulado mediante reglas por keywords. Aun así, devuelve un contrato útil para producción: `labels`, `suspectedFinding`, `confidence`, `studyType` y `source`. Esto permite cambiar la implementación sin rediseñar el resto del pipeline.

**4. Speech To Text**  
La capa STT toma una transcripción ya disponible o una entrada simulada equivalente. En producción, aquí se conectaría un servicio como Whisper o un engine on-premise. La salida agrega metadatos de calidad, idioma y cobertura.

**5. Chunking**  
La transcripción se divide en fragmentos manejables por oraciones y tamaño aproximado. Esto evita mandar textos muy largos a un modelo en una sola unidad y mejora la futura recuperación semántica. En clínica, el chunking ayuda a preservar eventos relevantes como síntomas, medidas, tiempos y conductas.

**6. Embeddings y retrieval**  
Cada chunk y cada documento clínico de referencia se representan con embeddings simulados. Luego se calcula similitud coseno para recuperar los fragmentos más cercanos. El objetivo no es precisión de producción sino mostrar claramente el patrón: transformar texto en vectores, rankear y usar solo el contexto útil.

**7. Resumen multimodal**  
El resumen combina la evidencia de voz, imagen y retrieval. La salida prioriza:

- hallazgos visuales
- síntomas o contexto reportados
- documentos de soporte recuperados
- necesidad de revisión humana

**8. Evaluación automática**  
El flujo puntúa la calidad de la salida con varias métricas. Si la transcripción es dudosa, la imagen tiene baja confianza o el grounding documental es débil, el score global cae. Esto evita tratar como confiable una síntesis que en realidad está poco sostenida.

**9. Fallback seguro**  
Si la evaluación no supera el umbral, el workflow no intenta “inventar mejor”. En cambio, devuelve una respuesta conservadora, pide revisión humana y prepara un TTS breve que comunica la limitación sin inducir confianza injustificada.

**10. TTS y respuesta final**  
La última etapa no sintetiza audio directamente en esta versión, sino que construye un payload claro para un proveedor TTS. Esto separa la lógica clínica de la capa de voz y facilita elegir después entre cloud o infraestructura propia.

---

## 3. Criterios de éxito

Se definieron los siguientes criterios de éxito para considerar el flujo aceptable:

1. El webhook debe aceptar y normalizar correctamente entradas multimodales.
2. La capa de imagen debe devolver etiquetas y un score interpretable.
3. La capa STT debe producir una transcripción reutilizable en pasos posteriores.
4. El chunking debe fragmentar transcripciones largas sin perder demasiado contexto.
5. La búsqueda semántica debe recuperar al menos dos documentos relevantes para casos frecuentes.
6. La evaluación automática debe decidir de manera explícita cuándo usar fallback.
7. La respuesta final debe incluir trazabilidad mínima, score y marca de revisión humana cuando corresponda.

Estos criterios no miden solo “si el flujo corre”, sino si su comportamiento resulta razonable para un contexto sensible.

---

## 4. Métricas propuestas

Las métricas instrumentadas o sugeridas para este diseño son:

- **Transcription Quality**: score heurístico basado en longitud, cobertura y presencia de contenido clínico.
- **Image Confidence**: score del módulo visual para estimar qué tan confiable es el hallazgo etiquetado.
- **Retrieval Top Score**: mejor similitud entre consulta multimodal y documentos de referencia.
- **Grounding Score**: medida agregada de cuánto contexto útil recuperó el sistema.
- **Overall Score**: promedio ponderado para decidir continuidad o fallback.
- **Fallback Rate**: porcentaje de ejecuciones que no alcanzan el umbral.
- **Latency Ms**: tiempo total desde webhook hasta respuesta.
- **Requires Human Review Rate**: proporción de casos que requieren validación profesional.

En una versión productiva, estas métricas deberían consolidarse en un dashboard con series temporales y segmentación por tipo de estudio, idioma, institución o proveedor de STT/TTS.

---

## 5. Políticas de fallback

El diseño incluye fallback por tres grandes motivos:

**1. Falla de adquisición**  
Si no hay transcripción ni forma de obtenerla, el flujo no continúa como si el audio hubiese sido entendido.

**2. Evidencia insuficiente**  
Si el retrieval no encuentra suficiente contexto documental o la similitud es baja, el sistema reduce su ambición.

**3. Calidad global baja**  
Si la combinación de scores no alcanza el umbral definido, el resumen final se reemplaza por una salida segura.

La lógica del fallback busca evitar dos errores frecuentes en sistemas clínicos:

- presentar una respuesta “bien escrita” pero débilmente fundada
- ocultar la incertidumbre al usuario final

---

## 6. Trade-offs on-premise vs cloud

### Opción cloud

El enfoque cloud acelera mucho el time-to-market. Permite conectar rápido APIs de STT, TTS, visión y modelos de lenguaje sin desplegar infraestructura especializada. También simplifica escalado, mantenimiento y actualización de modelos.

Sin embargo, en biomédica esto trae costos regulatorios y arquitectónicos relevantes:

- transferencia de datos sensibles fuera de la institución
- necesidad de contratos específicos con proveedores
- evaluación de residencia de datos
- mayor superficie de riesgo si se procesan PHI o imágenes diagnósticas reales

### Opción on-premise

El enfoque on-premise o en VPC controlada mejora la gobernanza del dato. Permite integrar mejor con políticas internas, segmentación de red, auditoría y retención. Para hospitales, laboratorios o redes de clínicas, este control puede ser decisivo.

La contracara es clara:

- mayor costo inicial
- necesidad de hardware
- más complejidad de MLOps
- mantenimiento continuo de modelos y observabilidad

### Decisión recomendada

Para un piloto educativo o una prueba de concepto, cloud es razonable si se trabaja con datos simulados o anonimizados. Para un despliegue operativo con pacientes reales, la recomendación es al menos evaluar:

- anonimización fuerte antes de enviar datos
- procesamiento híbrido
- ejecución on-premise para imagen y STT
- cloud solo para capas no sensibles o ya desidentificadas

---

## 7. Conclusión

El principal valor del flujo no está en “usar muchos modelos”, sino en **coordinar modalidades distintas bajo una lógica segura y evaluable**. Imagen, voz y texto no se tratan como islas: se integran en una misma cadena operativa con trazabilidad, scores y degradación explícita.

Para biomédica, esto es más importante que la sofisticación aislada de cada modelo. Un sistema multimodal útil no es el que más genera, sino el que:

- expone sus límites
- mide su calidad
- protege datos sensibles
- facilita revisión humana

Ese es el criterio que guió el workflow propuesto para la clase 5.
