# lightrag-cv

## Objective

Create a demo of LightRAG with CV 
Its a POC, don't require a production grade application
Limit the unit and integration tests to the minimum
Don't over design, we need quick result

## Application

Deploy as docker containers locally (Windows WSl - Docker desktop)
You can use default usual network port in documentation and .env.example, but insure all port are in .env for configuration (usual network port are already used)

Use a maximum of OpenSource library and ideally directly existing docker image

### Docker service : 

- Docling
Source : https://github.com/docling-project/docling
==> For documents parse and chunking (with docling HybridChunker)

- LightRAG server
Source : GitHub Project : https://github.com/HKUDS/LightRAG / Web UI and API support : https://github.com/HKUDS/LightRAG/blob/main/lightrag/api/README.md
==> For RAG engine
In gestion : store chunks in both vectors and graphs
Graph entity : allow to store entities definition
Retrieval : benefits many optimized query mode

- Postgre
Source : : https://github.com/docker-library/postgres
Use lastest version with VectorDB (pgvector) and GraphDB (apache AGE) extension

- LightRAG CV
Application to build that used generic services

### LightRAG CV : 

Containers Docling, LightRAG server, Postgre must reusable (by creating new instances)
LightRAG CV is a specific application that create a knowledge base, based on data :

- ProfileReference : use french reference 
Source :  https://www.cigref.fr/wp/wp-content/uploads/2024/10/Cigref_Nomenclature_des_profils_metiers_SI_version_2024.pdf
It describe Profile in IT development organized by domains, for each profile :
- Mission 
- Activities
- Deliverables 
- Performance indicators
- List of transversal skills
- List of profile skills

- CV
Sources for test using Huggingface dataset:
- CV1 = https://huggingface.co/datasets/gigswar/cv_files 
- CV2 = https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf 

# Configuration

## LLm config
Provider : ollama or openai compatible

### Ollama LLM + Ollama Embedding / reranking :
LLM_BINDING=ollama
LLM_MODEL=qwen3:8b
LLM_BINDING_HOST=http://localhost:11434
OLLAMA_LLM_NUM_CTX=40960

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024

RERANK_BINDING=ollama
RERANK_BINDING_HOST=http://localhost:11434
RERANK_MODEL=xitao/bge-reranker-v2-m3


## Storage

use Postgre database

LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_GRAPH_STORAGE=PGGraphStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage

