from __future__ import annotations

import copy
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path("/Users/juancavidela/Desktop/coder-ia/clase-3")
PARTIALS = ROOT / "partials"


DOCS = [
    {
        "docId": "doc-pro-ibuprofeno-v1",
        "title": "Prospecto - Ibuprofeno 400 mg",
        "category": "prospecto",
        "version": "2026-01",
        "tags": ["dolor", "antiinflamatorio", "gastrointestinal"],
        "sections": [
            {
                "slug": "indicaciones",
                "title": "Indicaciones",
                "text": (
                    "Indicado para dolor leve a moderado, fiebre e inflamacion. "
                    "Se usa en cuadros osteomusculares y cefaleas, pero no reemplaza "
                    "la evaluacion clinica cuando hay signos de alarma."
                ),
            },
            {
                "slug": "efectos-adversos",
                "title": "Efectos adversos",
                "text": (
                    "Puede provocar dolor abdominal, dispepsia, nauseas, gastritis y, "
                    "con menor frecuencia, vomitos o sangrado digestivo. El riesgo "
                    "gastrointestinal aumenta con dosis altas o uso prolongado."
                ),
            },
            {
                "slug": "adultos-mayores",
                "title": "Adultos mayores y alertas",
                "text": (
                    "En personas mayores de 65 anos conviene usar la menor dosis efectiva "
                    "y vigilar deshidratacion, deterioro renal y signos de hemorragia digestiva. "
                    "Si hay dolor abdominal persistente, se debe suspender y consultar."
                ),
            },
        ],
    },
    {
        "docId": "doc-pro-metformina-v1",
        "title": "Prospecto - Metformina 850 mg",
        "category": "prospecto",
        "version": "2026-02",
        "tags": ["diabetes", "nauseas", "gastrointestinal"],
        "sections": [
            {
                "slug": "indicaciones",
                "title": "Indicaciones",
                "text": (
                    "Medicamento para diabetes tipo 2. Se recomienda iniciar en forma gradual "
                    "y acompanar con plan alimentario y control de glucemia."
                ),
            },
            {
                "slug": "efectos-adversos",
                "title": "Efectos adversos",
                "text": (
                    "Los efectos adversos mas frecuentes son nauseas, diarrea, distension, "
                    "molestias gastrointestinales y dolor abdominal. Suelen aparecer al inicio "
                    "del tratamiento o al subir dosis."
                ),
            },
            {
                "slug": "poblaciones-especiales",
                "title": "Poblaciones especiales",
                "text": (
                    "En adultos mayores conviene revisar funcion renal y estado de hidratacion "
                    "antes de ajustar dosis. Si hay intolerancia digestiva marcada, debe "
                    "reevaluarse el esquema terapeutico."
                ),
            },
        ],
    },
    {
        "docId": "doc-pro-amoxicilina-v1",
        "title": "Prospecto - Amoxicilina 500 mg",
        "category": "prospecto",
        "version": "2026-01",
        "tags": ["antibiotico", "nauseas", "diarrea"],
        "sections": [
            {
                "slug": "indicaciones",
                "title": "Indicaciones",
                "text": (
                    "Antibiotico betalactamico para infecciones respiratorias, otitis, "
                    "sinusitis y otras infecciones bacterianas sensibles."
                ),
            },
            {
                "slug": "efectos-adversos",
                "title": "Efectos adversos",
                "text": (
                    "Puede asociarse a diarrea, nauseas, vomitos, dolor abdominal y rash "
                    "cutaneo. Ante diarrea intensa o persistente debe considerarse colitis "
                    "asociada a antibioticos."
                ),
            },
            {
                "slug": "alertas",
                "title": "Alertas",
                "text": (
                    "Si aparecen reacciones alergicas, disnea o compromiso hemodinamico, "
                    "suspender y derivar. La presencia de sintomas digestivos aislados no "
                    "equivale por si sola a una urgencia vital."
                ),
            },
        ],
    },
    {
        "docId": "doc-guia-dolor-toracico-v2",
        "title": "Guia - Manejo inicial del dolor toracico",
        "category": "guia",
        "version": "2026-03",
        "tags": ["triage", "dolor toracico", "cardiologia"],
        "sections": [
            {
                "slug": "banderas-rojas",
                "title": "Banderas rojas",
                "text": (
                    "Dolor toracico opresivo con irradiacion a brazo, disnea, sudoracion o "
                    "nauseas debe considerarse de alto riesgo hasta descartar sindrome "
                    "coronario agudo. Priorizar ECG y evaluacion urgente."
                ),
            },
            {
                "slug": "triaje",
                "title": "Triage inicial",
                "text": (
                    "Si el paciente presenta hipotension, saturacion baja o compromiso del "
                    "estado general, la derivacion debe ser inmediata. La guia no reemplaza "
                    "criterio medico ni protocolos institucionales."
                ),
            },
        ],
    },
    {
        "docId": "doc-guia-nauseas-v1",
        "title": "Guia - Nauseas, vomitos y dolor abdominal",
        "category": "guia",
        "version": "2026-02",
        "tags": ["gastrointestinal", "nauseas", "abdomen"],
        "sections": [
            {
                "slug": "evaluacion-inicial",
                "title": "Evaluacion inicial",
                "text": (
                    "Nauseas y dolor abdominal requieren valorar hidratacion, fiebre, vomitos "
                    "persistentes, diarrea y medicamentos recientes. La cronologia de los "
                    "sintomas ayuda a distinguir eventos adversos de causas infecciosas."
                ),
            },
            {
                "slug": "signos-de-alarma",
                "title": "Signos de alarma",
                "text": (
                    "Dolor abdominal intenso, sangrado digestivo, rigidez abdominal, compromiso "
                    "hemodinamico o dificultad respiratoria requieren evaluacion presencial "
                    "urgente. En adultos mayores el umbral de derivacion debe ser mas bajo."
                ),
            },
        ],
    },
    {
        "docId": "doc-guia-disnea-v1",
        "title": "Guia - Disnea y signos de alarma respiratorios",
        "category": "guia",
        "version": "2026-01",
        "tags": ["disnea", "respiratorio", "urgencia"],
        "sections": [
            {
                "slug": "triaje-respiratorio",
                "title": "Triage respiratorio",
                "text": (
                    "Disnea de inicio agudo, dolor toracico, sibilancias intensas o saturacion "
                    "menor a 92 por ciento exigen evaluacion rapida. La presencia de fiebre o "
                    "tos no reduce el riesgo por si sola."
                ),
            },
            {
                "slug": "derivacion",
                "title": "Derivacion",
                "text": (
                    "Si la disnea limita hablar, caminar o se acompana de confusion, la consulta "
                    "debe escalarse como prioritaria. Documentar tiempos, factores precipitantes "
                    "y antecedentes respiratorios."
                ),
            },
        ],
    },
]


RAG_LIB = dedent(
    r"""
    const DIMENSIONS = 64;

    function stripAccents(text) {
      return String(text || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    function normalize(text) {
      const replacements = {
        panza: 'abdominal',
        barriga: 'abdominal',
        estomago: 'abdominal',
        pecho: 'toracico',
        torax: 'toracico',
        nausea: 'nauseas',
        vomitar: 'vomito',
        vomitos: 'vomito',
        gastricas: 'gastrointestinal',
        gastrica: 'gastrointestinal',
        falta: 'disnea',
        aire: 'disnea',
        anciano: 'adulto',
        ancianos: 'adultos',
        geriatrico: 'adulto',
        remedio: 'medicamento',
        remedios: 'medicamentos'
      };

      const cleaned = stripAccents(text)
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

      return cleaned
        ? cleaned.split(' ').map((token) => replacements[token] || token)
        : [];
    }

    function hashText(text) {
      let hash = 0;
      for (const ch of String(text || '')) {
        hash = ((hash << 5) - hash) + ch.charCodeAt(0);
        hash |= 0;
      }
      return 'hash_' + Math.abs(hash).toString(36);
    }

    function buildVector(text, dims = DIMENSIONS) {
      const vec = Array(dims).fill(0);
      for (const token of normalize(text)) {
        let hash = 0;
        for (let i = 0; i < token.length; i++) {
          hash = ((hash << 5) - hash) + token.charCodeAt(i);
          hash |= 0;
        }
        const idx = Math.abs(hash) % dims;
        vec[idx] += 1;
      }
      const norm = Math.sqrt(vec.reduce((acc, value) => acc + (value * value), 0)) || 1;
      return vec.map((value) => Number((value / norm).toFixed(6)));
    }

    function cosine(a, b) {
      let sum = 0;
      for (let i = 0; i < Math.max(a.length, b.length); i++) {
        sum += (a[i] || 0) * (b[i] || 0);
      }
      return sum;
    }

    function overlapScore(queryText, candidateText) {
      const q = new Set(normalize(queryText));
      const c = new Set(normalize(candidateText));
      if (!q.size) return 0;
      let hits = 0;
      for (const token of q) if (c.has(token)) hits += 1;
      return hits / q.size;
    }

    function getDefaultDocuments() {
      return __DOCS_JSON__;
    }

    function chunkDocuments(documents) {
      const chunks = [];

      for (const doc of documents) {
        for (const [sectionIndex, section] of (doc.sections || []).entries()) {
          const rawSentences = String(section.text || '')
            .split(/(?<=[.!?])\s+/)
            .map((sentence) => sentence.trim())
            .filter(Boolean);
          const sentences = rawSentences.length
            ? rawSentences
            : [String(section.text || '').trim()].filter(Boolean);

          let buffer = [];
          let chunkCounter = 0;

          const flush = () => {
            const text = buffer.join(' ').trim();
            if (!text) return;
            chunkCounter += 1;
            chunks.push({
              chunkId: `${doc.docId}-${section.slug || ('sec' + (sectionIndex + 1))}-c${chunkCounter}`,
              docId: doc.docId,
              title: doc.title,
              category: doc.category,
              version: doc.version,
              section: section.title,
              sectionSlug: section.slug || `sec-${sectionIndex + 1}`,
              text,
              tags: doc.tags || [],
              sourceLabel: `${doc.title} / ${section.title}`
            });
            buffer = [];
          };

          for (const sentence of sentences) {
            const current = buffer.join(' ');
            if (current && (current.length + sentence.length + 1) > 320) flush();
            buffer.push(sentence);
          }
          flush();
        }
      }

      return chunks;
    }

    function embedChunks(chunks) {
      return chunks.map((chunk) => {
        const textForEmbedding = [chunk.title, chunk.section, ...(chunk.tags || []), chunk.text].join(' ');
        return {
          ...chunk,
          textForEmbedding,
          vector: buildVector(textForEmbedding)
        };
      });
    }

    function buildRetrieval(question, topK, embeddedChunks, scope, patientContext) {
      const safeTopK = Math.min(Math.max(Number(topK || 5), 1), 8);
      const safeScope = ['all', 'prospectos', 'guias'].includes(scope) ? scope : 'all';
      const patientBits = patientContext && typeof patientContext === 'object'
        ? Object.entries(patientContext).map(([key, value]) => `${key}: ${value}`).join(', ')
        : '';
      const queryText = [question, patientBits].filter(Boolean).join(' | ');
      const queryVector = buildVector(queryText);

      const filteredChunks = embeddedChunks.filter((chunk) => {
        if (safeScope === 'all') return true;
        if (safeScope === 'prospectos') return chunk.category === 'prospecto';
        if (safeScope === 'guias') return chunk.category === 'guia';
        return true;
      });

      const scored = filteredChunks
        .map((chunk) => {
          const semanticScore = cosine(queryVector, chunk.vector);
          const lexicalScore = overlapScore(queryText, chunk.textForEmbedding);
          const score = Number(((semanticScore * 0.75) + (lexicalScore * 0.25)).toFixed(4));
          return {
            ...chunk,
            semanticScore: Number(semanticScore.toFixed(4)),
            lexicalScore: Number(lexicalScore.toFixed(4)),
            score
          };
        })
        .filter((chunk) => chunk.score > 0.04)
        .sort((a, b) => b.score - a.score);

      const retrievedChunks = scored.slice(0, safeTopK).map((chunk) => {
        const { vector, textForEmbedding, ...rest } = chunk;
        return rest;
      });

      const topScore = retrievedChunks[0] ? retrievedChunks[0].score : 0;

      return {
        queryText,
        queryVector,
        retrievedChunks,
        retrieval: {
          topK: safeTopK,
          returned: retrievedChunks.length,
          topScore: Number(topScore.toFixed(4)),
          minScoreThreshold: 0.18,
          scopeUsed: safeScope,
          availableChunks: filteredChunks.length
        },
        evidenceSufficient: retrievedChunks.length > 0 && topScore >= 0.18
      };
    }
    """
).replace("__DOCS_JSON__", json.dumps(DOCS, ensure_ascii=False, indent=2))


PARSE_JSON_HELPER = dedent(
    r"""
    function extractJson(text) {
      if (text == null) return null;
      if (typeof text === 'object') return text;
      if (typeof text !== 'string') return null;

      try { return JSON.parse(text); } catch (error) {}

      const cleaned = text
        .replace(/^```(?:json)?\s*/i, '')
        .replace(/\s*```\s*$/i, '')
        .trim();
      try { return JSON.parse(cleaned); } catch (error) {}

      const match = cleaned.match(/\{[\s\S]*\}/);
      if (match) {
        try { return JSON.parse(match[0]); } catch (error) {}
      }

      return null;
    }
    """
)


MAIN_LLM_BODY = r"""={{ JSON.stringify({ model: 'google/gemini-2.0-flash-lite-001', temperature: 0.1, max_tokens: 700, messages: [ { role: 'system', content: 'Sos un asistente de RAG documental para healthcare. Tu tarea es responder SOLO con base en los fragmentos recuperados. No diagnostiques, no indiques dosis, no inventes fuentes. Tu salida DEBE ser EXCLUSIVAMENTE un JSON valido, sin markdown ni texto extra. Formato obligatorio: {"answer":"respuesta breve y trazable","sources":[{"chunkId":"id","docId":"id","title":"titulo","section":"seccion"}],"confidence":"alta|media|baja","requiresHumanReview":true }. Si la evidencia es debil, deja confidence baja y requiresHumanReview true.' }, { role: 'user', content: 'PREGUNTA:\n' + $json.question + '\n\nCONTEXTO RECUPERADO:\n' + $json.retrievedChunks.map((chunk, idx) => '[' + (idx + 1) + '] ' + chunk.title + ' / ' + chunk.section + ' / score=' + chunk.score + '\n' + chunk.text).join('\n\n') + '\n\nResponde solo con el JSON.' } ] }) }}"""

STEP4_LLM_BODY = r"""={{ JSON.stringify({ model: 'google/gemini-2.0-flash-lite-001', temperature: 0.1, max_tokens: 700, messages: [ { role: 'system', content: 'Sos un asistente de RAG documental. Responde solo con contexto recuperado y devuelve EXCLUSIVAMENTE JSON valido con este formato: {"answer":"...","sources":[{"chunkId":"..."}],"confidence":"alta|media|baja","requiresHumanReview":true }.' }, { role: 'user', content: 'PREGUNTA:\n' + $json.question + '\n\nCONTEXTO:\n' + $json.retrievedChunks.map((chunk, idx) => '[' + (idx + 1) + '] ' + chunk.chunkId + ' | ' + chunk.title + ' | ' + chunk.section + '\n' + chunk.text).join('\n\n') + '\n\nDevuelve solo JSON.' } ] }) }}"""


def with_lib(js: str) -> str:
    return dedent(f"{RAG_LIB}\n\n{js}").strip()


def sticky(node_id: str, name: str, content: str, pos: list[int], width=360, height=240, color=4) -> dict:
    return {
        "parameters": {"content": content, "height": height, "width": width, "color": color},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1,
        "position": pos,
    }


def webhook(node_id: str, name: str, path: str, pos: list[int]) -> dict:
    return {
        "parameters": {"httpMethod": "POST", "path": path, "responseMode": "responseNode", "options": {}},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": pos,
        "webhookId": path,
    }


def code(node_id: str, name: str, js: str, pos: list[int]) -> dict:
    return {
        "parameters": {"jsCode": js},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": pos,
    }


def if_boolean(node_id: str, name: str, expr: str, pos: list[int], strict=True) -> dict:
    return {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict" if strict else "loose",
                },
                "conditions": [
                    {
                        "id": f"{node_id}-cond",
                        "leftValue": expr,
                        "rightValue": True,
                        "operator": {"type": "boolean", "operation": "true", "singleValue": True},
                    }
                ],
                "combinator": "and",
            },
            "options": {},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": pos,
    }


def if_string_equals(node_id: str, name: str, expr: str, value: str, pos: list[int]) -> dict:
    return {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
                "conditions": [
                    {
                        "id": f"{node_id}-cond",
                        "leftValue": expr,
                        "rightValue": value,
                        "operator": {"type": "string", "operation": "equals"},
                    }
                ],
                "combinator": "and",
            },
            "options": {},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": pos,
    }


def respond(node_id: str, name: str, body_expr="={{ $json }}", pos=None, status_code: int | None = None) -> dict:
    node = {
        "parameters": {"respondWith": "json", "responseBody": body_expr, "options": {}},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": pos or [0, 0],
    }
    if status_code is not None:
        node["parameters"]["options"]["responseCode"] = status_code
    return node


def openrouter_http(node_id: str, name: str, json_body: str, pos: list[int]) -> dict:
    return {
        "parameters": {
            "method": "POST",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization", "value": "=Bearer {{ $env.OPENROUTER_API_KEY }}"},
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "HTTP-Referer", "value": "http://localhost:5680"},
                    {"name": "X-Title", "value": "Healthcare RAG - Clase 3"},
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": json_body,
            "options": {"timeout": 20000},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": pos,
        "retryOnFail": True,
        "maxTries": 3,
        "waitBetweenTries": 2000,
        "onError": "continueRegularOutput",
        "notes": (
            "Modelo: google/gemini-2.0-flash-lite-001\n"
            "Timeout: 20s\n"
            "Retry: 3 intentos\n"
            "Solo sintetiza lo recuperado: no inventa contexto."
        ),
    }


def llama_upload(node_id: str, name: str, pos: list[int]) -> dict:
    return {
        "parameters": {
            "method": "POST",
            "url": "https://api.cloud.llamaindex.ai/api/v1/parsing/upload",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization", "value": "=Bearer {{ $env.LLAMA_CLOUD_API_KEY }}"},
                    {"name": "Accept", "value": "application/json"},
                ]
            },
            "sendBody": True,
            "contentType": "multipart-form-data",
            "bodyParameters": {
                "parameters": [
                    {"name": "input_url", "value": "={{ $json.pdfUrl }}"},
                    {"name": "result_type", "value": "markdown"},
                    {"name": "language", "value": "es"},
                ]
            },
            "options": {"timeout": 15000},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": pos,
        "retryOnFail": True,
        "maxTries": 2,
        "waitBetweenTries": 2000,
        "onError": "continueRegularOutput",
    }


def llama_get(node_id: str, name: str, pos: list[int]) -> dict:
    return {
        "parameters": {
            "method": "GET",
            "url": "=https://api.cloud.llamaindex.ai/api/v1/parsing/job/{{ $json.id }}/result/markdown",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization", "value": "=Bearer {{ $env.LLAMA_CLOUD_API_KEY }}"},
                    {"name": "Accept", "value": "application/json"},
                ]
            },
            "options": {"timeout": 15000},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": pos,
        "retryOnFail": True,
        "maxTries": 5,
        "waitBetweenTries": 3000,
        "onError": "continueRegularOutput",
    }


def wait(node_id: str, name: str, pos: list[int], seconds=8) -> dict:
    return {
        "parameters": {"amount": seconds, "unit": "seconds"},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": pos,
        "webhookId": f"{node_id}-wait",
    }


def workflow(name: str, wf_id: str, nodes: list[dict], connections: dict) -> dict:
    return {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "active": False,
        "settings": {"executionOrder": "v1"},
        "versionId": "3.0.0-selfhosted",
        "meta": {"templateCreatedBy": "Juanca - AI Automation"},
        "id": wf_id,
        "tags": [{"name": tag} for tag in ["healthcare", "rag", "clase-3"]],
    }


VALIDATE_QUERY_JS = with_lib(
    r"""
    const input = $input.first().json.body || $input.first().json;
    const question = String(input.question || '').trim();
    if (!question) {
      return [{ json: { valid: false, error: 'Campo requerido: question', statusCode: 400 } }];
    }

    const topK = Math.min(Math.max(Number(input.topK || 5), 1), 8);
    const scope = ['all', 'prospectos', 'guias'].includes(input.scope) ? input.scope : 'all';
    const patientContext = input.patientContext && typeof input.patientContext === 'object'
      ? input.patientContext
      : {};

    return [{
      json: {
        valid: true,
        question,
        topK,
        scope,
        patientContext,
        startedAtMs: Date.now(),
        questionHash: hashText(question),
        requireCitations: input.requireCitations !== false,
        requestedWorkflow: input.requestedWorkflow || '06-rag-completo'
      }
    }];
    """
)

BASE_DOCS_JS = with_lib(
    r"""
    const current = $input.first().json;
    const hasCustomDocs = Array.isArray(current.documents) && current.documents.length > 0;
    const documents = hasCustomDocs ? current.documents : getDefaultDocuments();

    return [{
      json: {
        ...current,
        documents,
        didUseDefaultDocuments: !hasCustomDocs,
        documentCount: documents.length
      }
    }];
    """
)

CHUNKING_JS = with_lib(
    r"""
    const current = $input.first().json;
    const chunks = chunkDocuments(current.documents || getDefaultDocuments());

    return [{
      json: {
        ...current,
        chunks,
        chunking: {
          strategy: 'semantico-por-secciones',
          overlap: 0,
          chunkCount: chunks.length
        }
      }
    }];
    """
)

EMBEDDING_JS = with_lib(
    r"""
    const current = $input.first().json;
    const embeddedChunks = embedChunks(current.chunks || chunkDocuments(getDefaultDocuments()));

    return [{
      json: {
        ...current,
        embeddedChunks,
        embedding: {
          simulated: true,
          dimensions: DIMENSIONS,
          model: 'hashed-bow-demo'
        }
      }
    }];
    """
)

RETRIEVAL_JS = with_lib(
    r"""
    const current = $input.first().json;
    const question = current.question || 'Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?';
    const topK = current.topK || 5;
    const scope = current.scope || 'all';
    const patientContext = current.patientContext || { age: 60, sex: 'masculino' };
    const embeddedChunks = current.embeddedChunks || embedChunks(chunkDocuments(getDefaultDocuments()));
    const result = buildRetrieval(question, topK, embeddedChunks, scope, patientContext);

    return [{
      json: {
        ...current,
        question,
        topK,
        scope,
        patientContext,
        embeddedChunks,
        queryVectorPreview: result.queryVector.slice(0, 12),
        retrievedChunks: result.retrievedChunks,
        retrieval: result.retrieval,
        evidenceSufficient: result.evidenceSufficient,
        contractOut: {
          step: '03-retrieval-topk',
          expectsNext: '{question, retrievedChunks[], retrieval}'
        }
      }
    }];
    """
)

NORMALIZE_OK_JS = dedent(
    r"""
    const current = $input.first().json;
    const finalConfidence = current.draftResponse.confidence || (current.retrieval.topScore >= 0.32 ? 'alta' : 'media');

    return [{
      json: {
        step: '06-rag-completo',
        question: current.question,
        questionHash: current.questionHash,
        startedAtMs: current.startedAtMs,
        answer: current.draftResponse.answer,
        sources: current.draftResponse.sources,
        confidence: finalConfidence,
        fallbackUsed: false,
        fallbackReason: null,
        requiresHumanReview: true,
        retrieval: current.retrieval,
        sourceType: 'llm-grounded',
        contractOut: {
          step: 'respuesta-final',
          shape: '{answer, sources, confidence, fallbackUsed, requiresHumanReview, retrieval, log}'
        }
      }
    }];
    """
).strip()

FALLBACK_JS = dedent(
    r"""
    const current = $input.first().json;
    const retrievalNode = $('🔎 Retrieval Top-K').first().json;
    const base = current.retrievedChunks ? current : retrievalNode;
    const reason = current.fallbackReason
      || (base && base.evidenceSufficient === false ? 'insufficient-evidence' : null)
      || (current.outputErrors ? 'llm-output-invalid' : null)
      || (current.error ? 'llm-request-failed' : null)
      || 'guardrail-rejected';

    const topMatches = (base.retrievedChunks || []).slice(0, 3);
    const sources = topMatches.map((chunk) => ({
      chunkId: chunk.chunkId,
      docId: chunk.docId,
      title: chunk.title,
      section: chunk.section,
      score: chunk.score,
      evidence: String(chunk.text || '').slice(0, 160)
    }));

    const answer = topMatches.length
      ? 'Encontre evidencia parcial en la base documental simulada, pero no la suficiente como para confiar en una respuesta sintetizada sin revision humana. Usa las fuentes recuperadas como punto de partida y no como indicacion medica.'
      : 'No encontre evidencia suficiente en la base documental simulada para responder con trazabilidad. Conviene ampliar la busqueda documental o derivar a revision humana.';

    return [{
      json: {
        step: '06-rag-completo',
        question: base.question,
        questionHash: base.questionHash,
        startedAtMs: base.startedAtMs || Date.now(),
        answer,
        sources,
        confidence: topMatches[0] && topMatches[0].score >= 0.3 ? 'media' : 'baja',
        fallbackUsed: true,
        fallbackReason: reason,
        requiresHumanReview: true,
        retrieval: base.retrieval,
        sourceType: 'fallback-seguro',
        contractOut: {
          step: 'respuesta-final',
          shape: '{answer, sources, confidence, fallbackUsed, requiresHumanReview, retrieval, log}'
        }
      }
    }];
    """
).strip()

LOG_JS = dedent(
    r"""
    const current = $input.first().json;
    const latencyMs = Math.max(Date.now() - (current.startedAtMs || Date.now()), 0);

    return [{
      json: {
        success: true,
        step: current.step,
        question: current.question,
        answer: current.answer,
        sources: current.sources,
        confidence: current.confidence,
        fallbackUsed: current.fallbackUsed,
        fallbackReason: current.fallbackReason || null,
        requiresHumanReview: current.requiresHumanReview,
        retrieval: current.retrieval,
        sourceType: current.sourceType,
        contractOut: current.contractOut,
        log: {
          event: 'rag_query_completed',
          ts: new Date().toISOString(),
          questionHash: current.questionHash,
          latencyMs,
          fallbackUsed: current.fallbackUsed,
          fallbackReason: current.fallbackReason || null,
          returnedChunks: current.retrieval ? current.retrieval.returned : 0,
          topScore: current.retrieval ? current.retrieval.topScore : 0,
          scopeUsed: current.retrieval ? current.retrieval.scopeUsed : 'all',
          requiresHumanReview: current.requiresHumanReview,
          sourceType: current.sourceType
        }
      }
    }];
    """
).strip()

PARSE_VALIDATE_MAIN_JS = dedent(
    f"""
    {PARSE_JSON_HELPER}

    const aiData = $input.first().json;
    const previous = $('🔎 Retrieval Top-K').first().json;
    const raw = aiData?.choices?.[0]?.message?.content || aiData?.error?.message || '';
    const parsed = extractJson(raw);
    const errors = [];

    if (!parsed || typeof parsed !== 'object') errors.push('no-json');
    if (!parsed?.answer || typeof parsed.answer !== 'string' || !parsed.answer.trim()) errors.push('missing-answer');
    if (!Array.isArray(parsed?.sources) || parsed.sources.length === 0) errors.push('missing-sources');
    if (parsed?.confidence && !['alta', 'media', 'baja'].includes(parsed.confidence)) errors.push('invalid-confidence');

    const sourceMap = new Map((previous.retrievedChunks || []).map((chunk) => [chunk.chunkId, chunk]));
    const normalizedSources = Array.isArray(parsed?.sources)
      ? parsed.sources
          .map((source) => {{
            const match = sourceMap.get(source.chunkId)
              || (previous.retrievedChunks || []).find((chunk) => chunk.docId === source.docId)
              || (previous.retrievedChunks || []).find((chunk) => chunk.title === source.title);
            if (!match) return null;
            return {{
              chunkId: match.chunkId,
              docId: match.docId,
              title: match.title,
              section: match.section,
              score: match.score,
              evidence: String(match.text || '').slice(0, 160)
            }};
          }})
          .filter(Boolean)
      : [];

    const uniqueSources = Array.from(
      new Map(normalizedSources.map((source) => [source.chunkId, source])).values()
    );

    if (uniqueSources.length === 0) errors.push('sources-not-grounded');

    return [{{
      json: {{
        ...previous,
        aiRaw: raw,
        validOutput: errors.length === 0,
        outputErrors: errors,
        fallbackReason: errors.length === 0 ? null : 'llm-output-invalid',
        draftResponse: errors.length === 0 ? {{
          answer: parsed.answer.trim(),
          sources: uniqueSources.slice(0, 3),
          confidence: ['alta', 'media', 'baja'].includes(parsed.confidence)
            ? parsed.confidence
            : (previous.retrieval.topScore >= 0.32 ? 'alta' : 'media'),
          requiresHumanReview: true
        }} : null
      }}
    }}];
    """
).strip()

LOAD_DOCUMENTS_JS = with_lib(
    r"""
    const input = $input.first().json.body || $input.first().json;
    const hasCustomDocs = Array.isArray(input.documents) && input.documents.length > 0;
    const documents = hasCustomDocs ? input.documents : getDefaultDocuments();

    return [{
      json: {
        step: '01-chunking',
        documents,
        didUseDefaultDocuments: !hasCustomDocs,
        contractOut: {
          step: '01-chunking',
          shape: '{documents[], chunks[]}',
          next: '02-embeddings-simulados'
        }
      }
    }];
    """
)

LOAD_CHUNKS_JS = with_lib(
    r"""
    const input = $input.first().json.body || $input.first().json;
    const hasChunks = Array.isArray(input.chunks) && input.chunks.length > 0;
    const chunks = hasChunks ? input.chunks : chunkDocuments(getDefaultDocuments());

    return [{
      json: {
        step: '02-embeddings-simulados',
        chunks,
        didUseDefaultChunks: !hasChunks,
        contractOut: {
          step: '02-embeddings-simulados',
          shape: '{chunks[], embeddedChunks[]}',
          next: '03-retrieval-topk'
        }
      }
    }];
    """
)

EMBEDDINGS_ONLY_JS = with_lib(
    r"""
    const current = $input.first().json;
    const embeddedChunks = embedChunks(current.chunks || []);

    return [{
      json: {
        ...current,
        embeddedChunks,
        embedding: { simulated: true, dimensions: DIMENSIONS, model: 'hashed-bow-demo' },
        vectorPreview: embeddedChunks.slice(0, 2).map((chunk) => ({
          chunkId: chunk.chunkId,
          title: chunk.title,
          section: chunk.section,
          vector: chunk.vector.slice(0, 12)
        }))
      }
    }];
    """
)

LOAD_EMBEDDED_CHUNKS_JS = with_lib(
    r"""
    const input = $input.first().json.body || $input.first().json;
    const question = String(input.question || 'Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?').trim();
    const topK = Math.min(Math.max(Number(input.topK || 5), 1), 8);
    const scope = ['all', 'prospectos', 'guias'].includes(input.scope) ? input.scope : 'all';
    const patientContext = input.patientContext && typeof input.patientContext === 'object'
      ? input.patientContext
      : { age: 60, sex: 'masculino' };
    const embeddedChunks = Array.isArray(input.embeddedChunks) && input.embeddedChunks.length > 0
      ? input.embeddedChunks
      : embedChunks(chunkDocuments(getDefaultDocuments()));

    return [{
      json: {
        step: '03-retrieval-topk',
        question,
        topK,
        scope,
        patientContext,
        embeddedChunks,
        contractOut: {
          step: '03-retrieval-topk',
          shape: '{question, retrievedChunks[], retrieval}',
          next: '04-generation-with-sources'
        }
      }
    }];
    """
)

LOAD_RETRIEVAL_JS = with_lib(
    r"""
    const input = $input.first().json.body || $input.first().json;
    const question = String(input.question || 'Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?').trim();
    const topK = Math.min(Math.max(Number(input.topK || 4), 1), 8);
    const scope = ['all', 'prospectos', 'guias'].includes(input.scope) ? input.scope : 'all';
    const patientContext = input.patientContext && typeof input.patientContext === 'object'
      ? input.patientContext
      : { age: 60, sex: 'masculino' };

    let retrievedChunks = Array.isArray(input.retrievedChunks) && input.retrievedChunks.length > 0
      ? input.retrievedChunks
      : null;
    let retrieval = input.retrieval || null;

    if (!retrievedChunks) {
      const embeddedChunks = embedChunks(chunkDocuments(getDefaultDocuments()));
      const built = buildRetrieval(question, topK, embeddedChunks, scope, patientContext);
      retrievedChunks = built.retrievedChunks;
      retrieval = built.retrieval;
    }

    return [{
      json: {
        step: '04-generation-with-sources',
        question,
        retrievedChunks,
        retrieval,
        patientContext,
        contractOut: {
          step: '04-generation-with-sources',
          shape: '{question, retrievedChunks[], draftResponse}',
          next: '05-guardrails-fallback-logs'
        }
      }
    }];
    """
)

PARSE_DRAFT_JS = dedent(
    f"""
    {PARSE_JSON_HELPER}

    const current = $input.first().json;
    const previous = $('📥 Cargar retrieval').first().json;
    const raw = current?.choices?.[0]?.message?.content || current?.error?.message || '';
    const parsed = extractJson(raw);
    const validDraft = Boolean(parsed && typeof parsed.answer === 'string' && parsed.answer.trim() && Array.isArray(parsed.sources));

    return [{{
      json: {{
        ...previous,
        llmRaw: raw,
        llmError: current?.error || null,
        validDraft,
        draftResponse: validDraft ? {{
          answer: parsed.answer.trim(),
          sources: parsed.sources,
          confidence: parsed.confidence || 'media',
          requiresHumanReview: parsed.requiresHumanReview !== false
        }} : null,
        contractOut: {{
          step: '04-generation-with-sources',
          shape: '{{question, retrievedChunks[], draftResponse}}',
          next: '05-guardrails-fallback-logs'
        }}
      }}
    }}];
    """
).strip()

LOAD_DRAFT_JS = with_lib(
    r"""
    const input = $input.first().json.body || $input.first().json;
    const demoMode = input.demoMode || 'valid';
    const question = String(input.question || 'Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?').trim();
    const topK = Math.min(Math.max(Number(input.topK || 4), 1), 8);
    const patientContext = input.patientContext && typeof input.patientContext === 'object'
      ? input.patientContext
      : { age: 60, sex: 'masculino' };

    let retrievedChunks = Array.isArray(input.retrievedChunks) && input.retrievedChunks.length > 0
      ? input.retrievedChunks
      : null;
    let retrieval = input.retrieval || null;

    if (!retrievedChunks) {
      const embeddedChunks = embedChunks(chunkDocuments(getDefaultDocuments()));
      const built = buildRetrieval(question, topK, embeddedChunks, 'prospectos', patientContext);
      retrievedChunks = built.retrievedChunks;
      retrieval = built.retrieval;
    }

    let draftResponse = input.draftResponse;
    if (!draftResponse) {
      draftResponse = demoMode === 'invalid'
        ? { answer: '', sources: [], confidence: 'alta', requiresHumanReview: false }
        : {
            answer: 'Los fragmentos recuperados asocian dolor abdominal y nauseas sobre todo con ibuprofeno, metformina y amoxicilina. La salida debe usarse como busqueda documental con trazabilidad, no como recomendacion medica.',
            sources: retrievedChunks.slice(0, 3).map((chunk) => ({ chunkId: chunk.chunkId })),
            confidence: retrievedChunks[0] && retrievedChunks[0].score >= 0.32 ? 'alta' : 'media',
            requiresHumanReview: true
          };
    }

    return [{
      json: {
        step: '05-guardrails-fallback-logs',
        question,
        startedAtMs: Date.now(),
        questionHash: hashText(question),
        retrievedChunks,
        retrieval,
        draftResponse,
        demoMode,
        contractOut: {
          step: '05-guardrails-fallback-logs',
          shape: '{answer, sources, confidence, fallbackUsed, retrieval, log}',
          next: '06-rag-completo'
        }
      }
    }];
    """
)

GUARDRAILS_JS = dedent(
    r"""
    const current = $input.first().json;
    const sourceMap = new Map((current.retrievedChunks || []).map((chunk) => [chunk.chunkId, chunk]));
    const draft = current.draftResponse || {};
    const errors = [];

    if (!draft.answer || typeof draft.answer !== 'string' || !draft.answer.trim()) errors.push('missing-answer');
    if (!Array.isArray(draft.sources) || draft.sources.length === 0) errors.push('missing-sources');
    if (current.retrieval && current.retrieval.topScore < (current.retrieval.minScoreThreshold || 0.18)) errors.push('insufficient-evidence');

    const groundedSources = Array.isArray(draft.sources)
      ? draft.sources
          .map((source) => {
            const match = sourceMap.get(source.chunkId)
              || (current.retrievedChunks || []).find((chunk) => chunk.docId === source.docId)
              || (current.retrievedChunks || []).find((chunk) => chunk.title === source.title);
            if (!match) return null;
            return {
              chunkId: match.chunkId,
              docId: match.docId,
              title: match.title,
              section: match.section,
              score: match.score,
              evidence: String(match.text || '').slice(0, 160)
            };
          })
          .filter(Boolean)
      : [];

    const uniqueGroundedSources = Array.from(
      new Map(groundedSources.map((source) => [source.chunkId, source])).values()
    );

    if (!uniqueGroundedSources.length) errors.push('sources-not-grounded');

    if (errors.length) {
      const topMatches = (current.retrievedChunks || []).slice(0, 3);
      return [{
        json: {
          step: '05-guardrails-fallback-logs',
          question: current.question,
          questionHash: current.questionHash,
          startedAtMs: current.startedAtMs,
          answer: topMatches.length
            ? 'El borrador no paso los guardrails o la evidencia fue debil. Dejo las mejores fuentes recuperadas para revision humana.'
            : 'No hay suficiente evidencia recuperada para responder con trazabilidad. Se recomienda ampliar la busqueda o pasar a revision humana.',
          sources: topMatches.map((chunk) => ({
            chunkId: chunk.chunkId,
            docId: chunk.docId,
            title: chunk.title,
            section: chunk.section,
            score: chunk.score,
            evidence: String(chunk.text || '').slice(0, 160)
          })),
          confidence: 'baja',
          fallbackUsed: true,
          fallbackReason: errors[0],
          requiresHumanReview: true,
          retrieval: current.retrieval,
          sourceType: 'guardrail-fallback'
        }
      }];
    }

    return [{
      json: {
        step: '05-guardrails-fallback-logs',
        question: current.question,
        questionHash: current.questionHash,
        startedAtMs: current.startedAtMs,
        answer: draft.answer.trim(),
        sources: uniqueGroundedSources.slice(0, 3),
        confidence: ['alta', 'media', 'baja'].includes(draft.confidence) ? draft.confidence : 'media',
        fallbackUsed: false,
        fallbackReason: null,
        requiresHumanReview: true,
        retrieval: current.retrieval,
        sourceType: 'draft-validated'
      }
    }];
    """
).strip()

VALIDATE_PDF_JS = dedent(
    r"""
    const input = $input.first().json.body || $input.first().json;
    const pdfUrl = String(input.pdfUrl || '').trim();
    if (!pdfUrl) {
      return [{ json: { valid: false, error: 'Campo requerido: pdfUrl', statusCode: 400 } }];
    }

    return [{
      json: {
        valid: true,
        pdfUrl,
        source: input.source || 'llamacloud-demo',
        startedAtMs: Date.now()
      }
    }];
    """
).strip()

BUILD_CANONICAL_DOC_JS = with_lib(
    r"""
    const current = $input.first().json;
    if (current?.error) {
      return [{
        json: {
          success: false,
          error: current.error.message || 'No se pudo obtener markdown desde LlamaCloud',
          details: current.error,
          contractOut: null
        }
      }];
    }

    const markdown = typeof current === 'string'
      ? current
      : current.markdown || current.text || current.result || current.data || '';

    const rawText = typeof markdown === 'string' ? markdown : JSON.stringify(markdown);
    const sections = rawText
      .split(/\n(?=#{1,3}\s)/)
      .map((block) => block.trim())
      .filter(Boolean)
      .slice(0, 8)
      .map((block, index) => {
        const lines = block.split('\n').filter(Boolean);
        const first = lines[0] || `Seccion ${index + 1}`;
        const title = first.replace(/^#{1,3}\s*/, '') || `Seccion ${index + 1}`;
        const text = lines.slice(1).join(' ').trim() || block.replace(/^#{1,3}\s*/, '').trim();
        return { slug: `sec-${index + 1}`, title, text: text.slice(0, 900) };
      });

    const safeSections = sections.length
      ? sections
      : [{ slug: 'texto-completo', title: 'Texto completo', text: rawText.slice(0, 1800) }];
    const document = {
      docId: 'doc-llamacloud-' + Date.now(),
      title: 'Documento parseado por LlamaCloud',
      category: 'externo',
      version: new Date().toISOString().slice(0, 10),
      tags: ['llamacloud', 'parsing', 'externo'],
      sections: safeSections
    };

    return [{
      json: {
        success: true,
        step: '07-ingesta-llamacloud-opcional',
        markdownPreview: rawText.slice(0, 500),
        documents: [document],
        contractOut: {
          step: '07-ingesta-llamacloud-opcional',
          shape: '{documents[]}',
          next: '01-chunking o workflow padre'
        }
      }
    }];
    """
)


def build_main_workflow() -> tuple[list[dict], dict]:
    nodes = [
        sticky(
            "note-doc-main",
            "📘 Documentación",
            (
                "## Clase 3 - RAG documental\n\n"
                "Flujo padre completo:\n"
                "1. Consulta\n2. Chunking\n3. Embeddings simulados\n4. Retrieval top-k\n"
                "5. Respuesta grounded\n6. Guardrails y log\n\n"
                "Endpoint: `POST /webhook/rag-clinical-query`"
            ),
            [-360, 120],
            430,
            310,
            7,
        ),
        sticky(
            "note-setup-main",
            "⚙️ Setup",
            (
                "## Setup\n\n"
                "Requiere solo `OPENROUTER_API_KEY`.\n"
                "`LLAMA_CLOUD_API_KEY` queda para el workflow 07 opcional.\n\n"
                "Input minimo:\n```json\n{\n  \"question\": \"Que prospectos mencionan dolor abdominal y nauseas?\"\n}\n```"
            ),
            [60, -250],
            360,
            260,
            6,
        ),
        sticky(
            "note-chunk-main",
            "📝 Nota Chunking",
            "## Chunking\n\nPartimos documentos por secciones semanticas y, si hace falta, por grupos cortos de oraciones.\n\nIdea: no cortar conceptos clinicos a la mitad.",
            [820, -250],
            320,
            220,
            4,
        ),
        sticky(
            "note-retrieval-main",
            "📝 Nota Retrieval",
            "## Retrieval\n\nLa consulta se transforma en un vector simulado.\nSe rankean chunks por similitud + overlap lexical.\n\nSolo los mejores fragmentos entran al prompt.",
            [1580, -250],
            330,
            240,
            4,
        ),
        sticky(
            "note-generation-main",
            "📝 Nota Generation",
            "## Generation\n\nLa LLM entra al final.\nNo busca ni memoriza toda la base: sintetiza solo el contexto recuperado y cita fuentes.",
            [2240, -250],
            330,
            240,
            3,
        ),
        sticky(
            "note-safety-main",
            "📝 Nota Seguridad",
            "## Guardrails\n\nSi hay poca evidencia, si la salida no valida o si las fuentes no cierran, el flujo cae a una respuesta segura con revision humana.",
            [3040, -250],
            360,
            240,
            2,
        ),
        webhook("webhook-main", "🔎 Webhook - Consulta RAG", "rag-clinical-query", [160, 420]),
        code("code-validate-main", "✅ Validar Consulta", VALIDATE_QUERY_JS, [380, 420]),
        if_boolean("if-valid-main", "❓ ¿Consulta válida?", "={{ $json.valid }}", [600, 420]),
        respond("respond-error-main", "❌ Respuesta Error", "={{ { error: $json.error, statusCode: $json.statusCode || 400 } }}", [820, 560], 400),
        code("code-base-main", "📚 Base documental simulada", BASE_DOCS_JS, [820, 320]),
        code("code-chunk-main", "✂️ Chunking semántico", CHUNKING_JS, [1040, 320]),
        code("code-embed-main", "🧮 Embeddings simulados", EMBEDDING_JS, [1260, 320]),
        code("code-retrieval-main", "🔎 Retrieval Top-K", RETRIEVAL_JS, [1480, 320]),
        if_boolean("if-evidence-main", "❓ ¿Evidencia suficiente?", "={{ $json.evidenceSufficient }}", [1700, 320]),
        openrouter_http("http-llm-main", "🤖 Respuesta grounded (OpenRouter)", MAIN_LLM_BODY, [1920, 220]),
        if_string_equals(
            "if-llm-main",
            "❓ ¿LLM respondió OK?",
            "={{ $json.choices && $json.choices[0] && $json.choices[0].message && $json.choices[0].message.content ? 'ok' : '' }}",
            "ok",
            [2140, 220],
        ),
        code("code-parse-main", "🧪 Parsear y validar salida", PARSE_VALIDATE_MAIN_JS, [2360, 120]),
        if_boolean("if-output-main", "❓ ¿Salida válida?", "={{ $json.validOutput }}", [2580, 120]),
        code("code-normalize-main", "🧩 Normalizar respuesta OK", NORMALIZE_OK_JS, [2800, 40]),
        code("code-fallback-main", "⚠️ Fallback seguro", FALLBACK_JS, [2800, 360]),
        code("code-log-main", "📈 Log estructurado", LOG_JS, [3020, 200]),
        respond("respond-main", "📤 Respuesta RAG", "={{ $json }}", [3240, 200]),
    ]

    connections = {
        "🔎 Webhook - Consulta RAG": {"main": [[{"node": "✅ Validar Consulta", "type": "main", "index": 0}]]},
        "✅ Validar Consulta": {"main": [[{"node": "❓ ¿Consulta válida?", "type": "main", "index": 0}]]},
        "❓ ¿Consulta válida?": {
            "main": [
                [{"node": "📚 Base documental simulada", "type": "main", "index": 0}],
                [{"node": "❌ Respuesta Error", "type": "main", "index": 0}],
            ]
        },
        "📚 Base documental simulada": {"main": [[{"node": "✂️ Chunking semántico", "type": "main", "index": 0}]]},
        "✂️ Chunking semántico": {"main": [[{"node": "🧮 Embeddings simulados", "type": "main", "index": 0}]]},
        "🧮 Embeddings simulados": {"main": [[{"node": "🔎 Retrieval Top-K", "type": "main", "index": 0}]]},
        "🔎 Retrieval Top-K": {"main": [[{"node": "❓ ¿Evidencia suficiente?", "type": "main", "index": 0}]]},
        "❓ ¿Evidencia suficiente?": {
            "main": [
                [{"node": "🤖 Respuesta grounded (OpenRouter)", "type": "main", "index": 0}],
                [{"node": "⚠️ Fallback seguro", "type": "main", "index": 0}],
            ]
        },
        "🤖 Respuesta grounded (OpenRouter)": {"main": [[{"node": "❓ ¿LLM respondió OK?", "type": "main", "index": 0}]]},
        "❓ ¿LLM respondió OK?": {
            "main": [
                [{"node": "🧪 Parsear y validar salida", "type": "main", "index": 0}],
                [{"node": "⚠️ Fallback seguro", "type": "main", "index": 0}],
            ]
        },
        "🧪 Parsear y validar salida": {"main": [[{"node": "❓ ¿Salida válida?", "type": "main", "index": 0}]]},
        "❓ ¿Salida válida?": {
            "main": [
                [{"node": "🧩 Normalizar respuesta OK", "type": "main", "index": 0}],
                [{"node": "⚠️ Fallback seguro", "type": "main", "index": 0}],
            ]
        },
        "🧩 Normalizar respuesta OK": {"main": [[{"node": "📈 Log estructurado", "type": "main", "index": 0}]]},
        "⚠️ Fallback seguro": {"main": [[{"node": "📈 Log estructurado", "type": "main", "index": 0}]]},
        "📈 Log estructurado": {"main": [[{"node": "📤 Respuesta RAG", "type": "main", "index": 0}]]},
    }
    return nodes, connections


def build_step_01() -> tuple[list[dict], dict]:
    nodes = [
        sticky(
            "note-doc-01",
            "📘 Paso 1",
            "## Paso 1 - Chunking\n\nEntrada: `documents[]` (o dataset por defecto).\nSalida: `chunks[]`.\n\nEste workflow explica como pasamos de documentos largos a unidades recuperables.",
            [-320, 120],
            380,
            220,
            7,
        ),
        sticky(
            "note-theory-01",
            "📝 Nota Teórica",
            "## Asociacion teoria-practica\n\nRAG no busca sobre PDFs completos. Busca sobre fragmentos.\nSi el chunk parte mal una idea, la respuesta final nace mal.",
            [520, -180],
            320,
            220,
            4,
        ),
        webhook("webhook-01", "📥 Webhook - Step 01", "rag-step-01-chunking", [180, 360]),
        code("code-docs-01", "📚 Preparar documentos", LOAD_DOCUMENTS_JS, [400, 360]),
        code("code-chunk-01", "✂️ Chunking semántico", CHUNKING_JS, [620, 360]),
        respond("respond-01", "📤 Respuesta Step 01", "={{ $json }}", [840, 360]),
    ]
    connections = {
        "📥 Webhook - Step 01": {"main": [[{"node": "📚 Preparar documentos", "type": "main", "index": 0}]]},
        "📚 Preparar documentos": {"main": [[{"node": "✂️ Chunking semántico", "type": "main", "index": 0}]]},
        "✂️ Chunking semántico": {"main": [[{"node": "📤 Respuesta Step 01", "type": "main", "index": 0}]]},
    }
    return nodes, connections


def build_step_02() -> tuple[list[dict], dict]:
    nodes = [
        sticky(
            "note-doc-02",
            "📘 Paso 2",
            "## Paso 2 - Embeddings simulados\n\nEntrada: `chunks[]`.\nSalida: `embeddedChunks[]` con `vector`.",
            [-320, 120],
            360,
            200,
            7,
        ),
        sticky(
            "note-theory-02",
            "📝 Nota Teórica",
            "## Asociacion teoria-practica\n\nEl vector no guarda texto legible: guarda una posicion numerica aproximada en el espacio semantico.\nAca lo simulamos para entender la idea.",
            [500, -180],
            320,
            220,
            4,
        ),
        webhook("webhook-02", "📥 Webhook - Step 02", "rag-step-02-embeddings", [180, 360]),
        code("code-load-02", "📥 Cargar chunks", LOAD_CHUNKS_JS, [400, 360]),
        code("code-embed-02", "🧮 Embeddings simulados", EMBEDDINGS_ONLY_JS, [620, 360]),
        respond("respond-02", "📤 Respuesta Step 02", "={{ $json }}", [840, 360]),
    ]
    connections = {
        "📥 Webhook - Step 02": {"main": [[{"node": "📥 Cargar chunks", "type": "main", "index": 0}]]},
        "📥 Cargar chunks": {"main": [[{"node": "🧮 Embeddings simulados", "type": "main", "index": 0}]]},
        "🧮 Embeddings simulados": {"main": [[{"node": "📤 Respuesta Step 02", "type": "main", "index": 0}]]},
    }
    return nodes, connections


def build_step_03() -> tuple[list[dict], dict]:
    nodes = [
        sticky(
            "note-doc-03",
            "📘 Paso 3",
            "## Paso 3 - Retrieval top-k\n\nEntrada: `question` + `embeddedChunks[]`.\nSalida: `retrievedChunks[]` ordenados por score.",
            [-330, 120],
            370,
            220,
            7,
        ),
        sticky(
            "note-theory-03",
            "📝 Nota Teórica",
            "## Asociacion teoria-practica\n\nRAG no manda toda la base al modelo.\nPrimero filtra. `top_k` decide cuantos fragmentos entran al prompt.",
            [540, -180],
            320,
            220,
            4,
        ),
        webhook("webhook-03", "📥 Webhook - Step 03", "rag-step-03-retrieval", [180, 360]),
        code("code-load-03", "📥 Cargar chunks embebidos", LOAD_EMBEDDED_CHUNKS_JS, [420, 360]),
        code("code-retrieval-03", "🔎 Retrieval Top-K", RETRIEVAL_JS, [640, 360]),
        respond("respond-03", "📤 Respuesta Step 03", "={{ $json }}", [860, 360]),
    ]
    connections = {
        "📥 Webhook - Step 03": {"main": [[{"node": "📥 Cargar chunks embebidos", "type": "main", "index": 0}]]},
        "📥 Cargar chunks embebidos": {"main": [[{"node": "🔎 Retrieval Top-K", "type": "main", "index": 0}]]},
        "🔎 Retrieval Top-K": {"main": [[{"node": "📤 Respuesta Step 03", "type": "main", "index": 0}]]},
    }
    return nodes, connections


def build_step_04() -> tuple[list[dict], dict]:
    nodes = [
        sticky(
            "note-doc-04",
            "📘 Paso 4",
            "## Paso 4 - Generation con fuentes\n\nEntrada: `question` + `retrievedChunks[]`.\nSalida: `draftResponse`.",
            [-330, 120],
            370,
            220,
            7,
        ),
        sticky(
            "note-theory-04",
            "📝 Nota Teórica",
            "## Asociacion teoria-practica\n\nLa LLM no reemplaza retrieval.\nSu trabajo aca es sintetizar y citar lo ya recuperado.",
            [760, -200],
            300,
            200,
            3,
        ),
        webhook("webhook-04", "📥 Webhook - Step 04", "rag-step-04-generation", [180, 360]),
        code("code-load-04", "📥 Cargar retrieval", LOAD_RETRIEVAL_JS, [420, 360]),
        openrouter_http("http-llm-04", "🤖 Respuesta grounded (OpenRouter)", STEP4_LLM_BODY, [660, 360]),
        code("code-parse-04", "🧪 Parsear borrador", PARSE_DRAFT_JS, [900, 360]),
        respond("respond-04", "📤 Respuesta Step 04", "={{ $json }}", [1120, 360]),
    ]
    connections = {
        "📥 Webhook - Step 04": {"main": [[{"node": "📥 Cargar retrieval", "type": "main", "index": 0}]]},
        "📥 Cargar retrieval": {"main": [[{"node": "🤖 Respuesta grounded (OpenRouter)", "type": "main", "index": 0}]]},
        "🤖 Respuesta grounded (OpenRouter)": {"main": [[{"node": "🧪 Parsear borrador", "type": "main", "index": 0}]]},
        "🧪 Parsear borrador": {"main": [[{"node": "📤 Respuesta Step 04", "type": "main", "index": 0}]]},
    }
    return nodes, connections


def build_step_05() -> tuple[list[dict], dict]:
    nodes = [
        sticky(
            "note-doc-05",
            "📘 Paso 5",
            "## Paso 5 - Guardrails, fallback y logs\n\nEntrada: `draftResponse` + `retrievedChunks[]`.\nSalida: respuesta final segura.",
            [-350, 120],
            390,
            220,
            7,
        ),
        sticky(
            "note-theory-05",
            "📝 Nota Teórica",
            "## Asociacion teoria-practica\n\nEn healthcare no alcanza con que el modelo responda.\nHay que validar evidencia, chequear fuentes y dejar trazabilidad.",
            [700, -200],
            320,
            220,
            2,
        ),
        webhook("webhook-05", "📥 Webhook - Step 05", "rag-step-05-guardrails", [180, 360]),
        code("code-load-05", "📥 Cargar borrador", LOAD_DRAFT_JS, [420, 360]),
        code("code-guardrails-05", "🛡️ Guardrails + Fallback", GUARDRAILS_JS, [660, 360]),
        code("code-log-05", "📈 Log estructurado", LOG_JS, [900, 360]),
        respond("respond-05", "📤 Respuesta Step 05", "={{ $json }}", [1120, 360]),
    ]
    connections = {
        "📥 Webhook - Step 05": {"main": [[{"node": "📥 Cargar borrador", "type": "main", "index": 0}]]},
        "📥 Cargar borrador": {"main": [[{"node": "🛡️ Guardrails + Fallback", "type": "main", "index": 0}]]},
        "🛡️ Guardrails + Fallback": {"main": [[{"node": "📈 Log estructurado", "type": "main", "index": 0}]]},
        "📈 Log estructurado": {"main": [[{"node": "📤 Respuesta Step 05", "type": "main", "index": 0}]]},
    }
    return nodes, connections


def build_step_07() -> tuple[list[dict], dict]:
    nodes = [
        sticky(
            "note-doc-07",
            "📘 Paso 7",
            "## Paso 7 - Ingesta opcional con LlamaCloud\n\nEntrada: `pdfUrl`.\nSalida: `documents[]` listos para entrar al paso 01 o al workflow padre.",
            [-340, 120],
            390,
            240,
            7,
        ),
        sticky(
            "note-theory-07",
            "📝 Nota Teórica",
            "## Asociacion teoria-practica\n\nLlamaCloud resuelve el parsing.\nDespues igual hay que normalizar el documento para poder chunkearlo y recuperarlo bien.",
            [820, -200],
            320,
            220,
            4,
        ),
        webhook("webhook-07", "📥 Webhook - Step 07", "rag-step-07-llamacloud-ingest", [180, 360]),
        code("code-validate-07", "✅ Validar PDF URL", VALIDATE_PDF_JS, [400, 360]),
        if_boolean("if-valid-07", "❓ ¿PDF válido?", "={{ $json.valid }}", [620, 360]),
        respond("respond-error-07", "❌ Respuesta Error", "={{ { error: $json.error, statusCode: $json.statusCode || 400 } }}", [840, 520], 400),
        llama_upload("llama-upload-07", "☁️ LlamaCloud Upload", [840, 260]),
        wait("wait-07", "⏳ Wait 8s", [1060, 260], 8),
        llama_get("llama-get-07", "📥 Obtener Markdown", [1280, 260]),
        code("code-canonical-07", "📝 Armar documento canónico", BUILD_CANONICAL_DOC_JS, [1500, 260]),
        respond("respond-07", "📤 Respuesta Step 07", "={{ $json }}", [1720, 260]),
    ]
    connections = {
        "📥 Webhook - Step 07": {"main": [[{"node": "✅ Validar PDF URL", "type": "main", "index": 0}]]},
        "✅ Validar PDF URL": {"main": [[{"node": "❓ ¿PDF válido?", "type": "main", "index": 0}]]},
        "❓ ¿PDF válido?": {
            "main": [
                [{"node": "☁️ LlamaCloud Upload", "type": "main", "index": 0}],
                [{"node": "❌ Respuesta Error", "type": "main", "index": 0}],
            ]
        },
        "☁️ LlamaCloud Upload": {"main": [[{"node": "⏳ Wait 8s", "type": "main", "index": 0}]]},
        "⏳ Wait 8s": {"main": [[{"node": "📥 Obtener Markdown", "type": "main", "index": 0}]]},
        "📥 Obtener Markdown": {"main": [[{"node": "📝 Armar documento canónico", "type": "main", "index": 0}]]},
        "📝 Armar documento canónico": {"main": [[{"node": "📤 Respuesta Step 07", "type": "main", "index": 0}]]},
    }
    return nodes, connections


def build_postman_collection() -> dict:
    return {
        "info": {
            "name": "Healthcare RAG - Clase 3 (n8n Local)",
            "description": (
                "Coleccion para probar el workflow padre y los workflows parciales de clase 3.\n\n"
                "Orden sugerido: 01 chunking -> 02 embeddings -> 03 retrieval -> 04 generation -> "
                "05 guardrails -> workflow padre.\n\nPuerto: 5680."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "_postman_id": "healthcare-rag-clase-3",
        },
        "variable": [
            {"key": "baseUrl", "value": "http://localhost:5680", "type": "string"},
            {
                "key": "pdfUrl",
                "value": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "type": "string",
            },
        ],
        "item": [
            {
                "name": "Workflow padre",
                "description": "Requiere workflow activo.",
                "item": [
                    {
                        "name": "RAG completo - prospectos GI",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "type": "text/javascript",
                                    "exec": [
                                        "pm.test('Status 200', () => pm.response.to.have.status(200));",
                                        "const b = pm.response.json();",
                                        "pm.test('answer existe', () => pm.expect(b.answer).to.be.a('string'));",
                                        "pm.test('sources no vacio', () => pm.expect(b.sources.length).to.be.greaterThan(0));",
                                        "pm.test('retrieval presente', () => pm.expect(b.retrieval).to.be.an('object'));",
                                    ],
                                },
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-clinical-query",
                                "host": ["{{baseUrl}}/webhook/rag-clinical-query"],
                            },
                            "body": {
                                "mode": "raw",
                                "raw": (
                                    "{\n"
                                    '  "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?",\n'
                                    '  "topK": 4,\n'
                                    '  "scope": "prospectos",\n'
                                    '  "patientContext": { "age": 68, "sex": "masculino" }\n'
                                    "}"
                                ),
                            },
                        },
                    },
                    {
                        "name": "Error 400 - falta question",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "type": "text/javascript",
                                    "exec": [
                                        "pm.test('Status 400', () => pm.response.to.have.status(400));"
                                    ],
                                },
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-clinical-query",
                                "host": ["{{baseUrl}}/webhook/rag-clinical-query"],
                            },
                            "body": {"mode": "raw", "raw": '{\n  "topK": 4\n}'},
                        },
                    },
                ],
            },
            {
                "name": "Workflows parciales",
                "item": [
                    {
                        "name": "01 - Chunking",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "type": "text/javascript",
                                    "exec": [
                                        "pm.test('Status 200', () => pm.response.to.have.status(200));",
                                        "const b = pm.response.json();",
                                        "pm.test('chunks > 0', () => pm.expect(b.chunks.length).to.be.greaterThan(0));",
                                    ],
                                },
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-step-01-chunking",
                                "host": ["{{baseUrl}}/webhook/rag-step-01-chunking"],
                            },
                            "body": {"mode": "raw", "raw": "{ }"},
                        },
                    },
                    {
                        "name": "02 - Embeddings simulados",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "type": "text/javascript",
                                    "exec": [
                                        "pm.test('Status 200', () => pm.response.to.have.status(200));",
                                        "const b = pm.response.json();",
                                        "pm.test('embeddedChunks > 0', () => pm.expect(b.embeddedChunks.length).to.be.greaterThan(0));",
                                    ],
                                },
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-step-02-embeddings",
                                "host": ["{{baseUrl}}/webhook/rag-step-02-embeddings"],
                            },
                            "body": {"mode": "raw", "raw": "{ }"},
                        },
                    },
                    {
                        "name": "03 - Retrieval top-k",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "type": "text/javascript",
                                    "exec": [
                                        "pm.test('Status 200', () => pm.response.to.have.status(200));",
                                        "const b = pm.response.json();",
                                        "pm.test('retrievedChunks > 0', () => pm.expect(b.retrievedChunks.length).to.be.greaterThan(0));",
                                    ],
                                },
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-step-03-retrieval",
                                "host": ["{{baseUrl}}/webhook/rag-step-03-retrieval"],
                            },
                            "body": {
                                "mode": "raw",
                                "raw": (
                                    "{\n"
                                    '  "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?",\n'
                                    '  "scope": "prospectos"\n'
                                    "}"
                                ),
                            },
                        },
                    },
                    {
                        "name": "04 - Generation con fuentes",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "type": "text/javascript",
                                    "exec": [
                                        "pm.test('Status 200', () => pm.response.to.have.status(200));",
                                        "const b = pm.response.json();",
                                        "pm.test('llmRaw existe', () => pm.expect(b.llmRaw).to.be.a('string'));",
                                    ],
                                },
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-step-04-generation",
                                "host": ["{{baseUrl}}/webhook/rag-step-04-generation"],
                            },
                            "body": {
                                "mode": "raw",
                                "raw": (
                                    "{\n"
                                    '  "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?",\n'
                                    '  "scope": "prospectos"\n'
                                    "}"
                                ),
                            },
                        },
                    },
                    {
                        "name": "05 - Guardrails y fallback",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "type": "text/javascript",
                                    "exec": [
                                        "pm.test('Status 200', () => pm.response.to.have.status(200));",
                                        "const b = pm.response.json();",
                                        "pm.test('log existe', () => pm.expect(b.log).to.be.an('object'));",
                                    ],
                                },
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-step-05-guardrails",
                                "host": ["{{baseUrl}}/webhook/rag-step-05-guardrails"],
                            },
                            "body": {
                                "mode": "raw",
                                "raw": '{\n  "question": "Que prospectos mencionan dolor abdominal y nauseas en adultos mayores?"\n}',
                            },
                        },
                    },
                    {
                        "name": "07 - LlamaCloud opcional",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "url": {
                                "raw": "{{baseUrl}}/webhook/rag-step-07-llamacloud-ingest",
                                "host": ["{{baseUrl}}/webhook/rag-step-07-llamacloud-ingest"],
                            },
                            "body": {"mode": "raw", "raw": '{\n  "pdfUrl": "{{pdfUrl}}"\n}'},
                        },
                    },
                ],
            },
        ],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    PARTIALS.mkdir(parents=True, exist_ok=True)

    main_nodes, main_connections = build_main_workflow()
    step1_nodes, step1_connections = build_step_01()
    step2_nodes, step2_connections = build_step_02()
    step3_nodes, step3_connections = build_step_03()
    step4_nodes, step4_connections = build_step_04()
    step5_nodes, step5_connections = build_step_05()
    step7_nodes, step7_connections = build_step_07()

    assets = {
        ROOT / "workflow.json": workflow(
            "Healthcare RAG Assistant - Clase 3 (workflow padre)",
            "healthcare-rag-clase-3",
            main_nodes,
            main_connections,
        ),
        PARTIALS / "01-chunking.json": workflow(
            "Clase 3 - Step 01 - Chunking",
            "clase-3-step-01-chunking",
            step1_nodes,
            step1_connections,
        ),
        PARTIALS / "02-embeddings-simulados.json": workflow(
            "Clase 3 - Step 02 - Embeddings simulados",
            "clase-3-step-02-embeddings",
            step2_nodes,
            step2_connections,
        ),
        PARTIALS / "03-retrieval-topk.json": workflow(
            "Clase 3 - Step 03 - Retrieval Top-K",
            "clase-3-step-03-retrieval",
            step3_nodes,
            step3_connections,
        ),
        PARTIALS / "04-generation-with-sources.json": workflow(
            "Clase 3 - Step 04 - Generation with sources",
            "clase-3-step-04-generation",
            step4_nodes,
            step4_connections,
        ),
        PARTIALS / "05-guardrails-fallback-logs.json": workflow(
            "Clase 3 - Step 05 - Guardrails + fallback + logs",
            "clase-3-step-05-guardrails",
            step5_nodes,
            step5_connections,
        ),
        PARTIALS / "06-rag-completo.json": workflow(
            "Healthcare RAG Assistant - Clase 3 (workflow padre)",
            "healthcare-rag-clase-3-partial",
            copy.deepcopy(main_nodes),
            copy.deepcopy(main_connections),
        ),
        PARTIALS / "07-ingesta-llamacloud-opcional.json": workflow(
            "Clase 3 - Step 07 - Ingesta LlamaCloud opcional",
            "clase-3-step-07-llamacloud",
            step7_nodes,
            step7_connections,
        ),
    }

    for path, payload in assets.items():
        write_json(path, payload)

    write_json(ROOT / "postman_collection.json", build_postman_collection())


if __name__ == "__main__":
    main()
