# Clase 4

Workflows de parsing documental y RAG sin vector DB para la clase de hoy.

Esta version esta pensada para alumnos que no programan:

- `09` tiene 1 sola caja negra de codigo
- `10` tiene 2 cajas negras de codigo
- el codigo esta escrito de forma declarativa, con pasos comentados

## Puesta en marcha

```bash
cd /Users/juancavidela/Desktop/coder-ia/clase-4
docker compose up -d
```

UI de n8n:

`http://localhost:5681`

## Workflows incluidos

- `partials/09-ingesta-rag-sin-vector-db.json`
- `partials/10-rag-consulta-sin-vector-db.json`
- `partials/11-llamacloud-rag-e2e.json`

## Idea de uso

1. `09-ingesta-rag-sin-vector-db`
   - recibe markdown o texto parseado
   - devuelve `embeddedChunks[]`

2. `10-rag-consulta-sin-vector-db`
   - recibe `question` + `embeddedChunks[]`
   - hace retrieval local, sintesis con LLM y fallback seguro

3. `11-llamacloud-rag-e2e`
   - recibe `fileUrl` + `question`
   - hace parsing con LlamaCloud y responde sobre ese documento

## Endpoints

- `POST /webhook/rag-ingesta-documental`
- `POST /webhook/rag-consulta-documental`
- `POST /webhook/llamacloud-rag-e2e`

## Nota

Las API keys estan hardcodeadas dentro de los workflows por una limitacion puntual de lectura de variables en este setup de n8n.
