# Glosario RAG

## Embedding → Representación vectorial
Representación numérica (vector) que captura el significado de un texto. Permite comparar por semántica, no por palabras clave.

## Vector Space → Espacio vectorial
"Mapa" donde cada embedding es un punto. La cercanía entre puntos indica similitud conceptual.

## Similarity / Distance → Similitud / Distancia
Mide qué tan parecidos son dos vectores. Más cerca = más similar. Métricas comunes: cosine similarity, distancia euclidiana.

## Chunking → Fragmentación
Dividir documentos en partes más pequeñas y coherentes. Mejora la precisión en la búsqueda retrieval.

## Parsing → Parseo / Estructuración
Convertir documentos (PDF, DOCX, etc.) a texto limpio y estructurado. Es la base del pipeline RAG.

## Retrieval → Recuperación
Buscar los fragmentos más relevantes para una consulta del usuario. Se basa en similitud vectorial.

## RAG (Retrieval-Augmented Generation) → Generación aumentada con recuperación
Arquitectura que:
1. Busca información relevante en la base de conocimientos
2. La pasa al modelo como contexto
3. Genera una respuesta basada en eso

## Vector Database → Base de datos vectorial
Base optimizada para almacenar embeddings y buscar por similitud. Ejemplos: Chroma, Pinecone, Weaviate, Milvus.

## Semantic Search → Búsqueda semántica
Búsqueda por significado, no por coincidencia textual exacta.

## Context → Contexto
Información que se le pasa al modelo para responder. En RAG: los chunks recuperados.

## LLM (Large Language Model) → Modelo de lenguaje grande
Modelo que genera texto (ej: GPT-4, Claude, Llama). No "sabe" por sí mismo, solo responde con el contexto que recibe.

## Top-K → Número de resultados
Cantidad de fragmentos que se recuperan en la búsqueda. Balance entre precisión y cobertura.

## Overlap → Solapamiento
Superposición entre chunks consecutivos para no cortar ideas importantes entre fragmentos.

## Pipeline → Flujo de procesamiento
Cadena de pasos del sistema RAG:
1. Parsing → 2. Chunking → 3. Embeddings → 4. DB vectorial → 5. Retrieval → 6. LLM