# Source Tree

**Repository Type:** Monorepo
**Organization Strategy:** Service-based directories with shared configuration at root level

## Complete Project Structure

```plaintext
lightrag-cv/
├── .env.example                      # Environment variable template
├── .env                              # Actual environment config (DO NOT COMMIT)
├── .gitignore                        # Git exclusions
├── docker-compose.yml                # Main orchestration file
├── docker-compose.gpu.yml            # GPU profile overrides
├── README.md                         # Project overview and setup
├── LICENSE
│
├── services/                         # Microservices implementations
│   ├── docling/                      # Docling REST API service
│   │   ├── Dockerfile
│   │   ├── Dockerfile.gpu
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── lightrag/                     # LightRAG service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   ├── storage/
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── mcp-server/                   # MCP protocol server
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── server.py
│   │   │   ├── tools/
│   │   │   ├── services/
│   │   │   └── config.py
│   │   └── tests/
│   │
│   └── postgres/                     # PostgreSQL configuration
│       ├── Dockerfile
│       ├── init/
│       │   ├── 01-init-db.sql
│       │   └── 02-create-tables.sql
│       └── conf/
│           └── postgresql.conf
│
├── data/                             # Data files (NOT committed)
│   ├── cigref/
│   ├── cvs/
│   └── lightrag/
│
├── docs/                             # Documentation
│   ├── prd.md
│   ├── architecture.md               # This document
│   ├── setup.md
│   └── testing/
│
├── scripts/                          # Utility scripts
│   ├── setup.sh
│   ├── pull-ollama-models.sh
│   ├── health-check.sh
│   ├── ingest-cigref.py
│   └── ingest-cvs.py
│
└── volumes/                          # Docker volume mount points
    └── postgres-data/
```

---
