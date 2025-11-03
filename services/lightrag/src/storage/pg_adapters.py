"""PostgreSQL storage adapters for LightRAG.

This module re-exports the built-in PostgreSQL storage implementations
from LightRAG 1.4.9.7+ which provides complete PostgreSQL, pgvector,
and Apache AGE support out of the box.

LightRAG's built-in adapters:
- PGKVStorage: Key-value storage using PostgreSQL tables
- PGVectorStorage: Vector storage using pgvector extension
- PGGraphStorage: Graph storage using Apache AGE extension
- PGDocStatusStorage: Document processing status tracking
"""

# Import LightRAG's built-in PostgreSQL storage implementations
from lightrag.kg.postgres_impl import (
    PGKVStorage,
    PGVectorStorage,
    PGGraphStorage,
    PGDocStatusStorage,
)

# Re-export for convenience
__all__ = [
    "PGKVStorage",
    "PGVectorStorage",
    "PGGraphStorage",
    "PGDocStatusStorage",
]
