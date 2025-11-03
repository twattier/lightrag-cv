#!/usr/bin/env python3
"""
Comprehensive health check for LightRAG-CV infrastructure.

Checks all services and returns JSON status report.
"""

import json
import os
import sys
from typing import Any, Dict

import httpx
import psycopg


def load_env() -> Dict[str, str]:
    """Load environment variables from .env file."""
    env = {}
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env[key] = value.strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def check_postgres(config: Dict[str, str]) -> Dict[str, Any]:
    """Check PostgreSQL connectivity and extensions."""
    result = {
        "name": "PostgreSQL",
        "healthy": False,
        "details": {}
    }

    try:
        dsn = (
            f"postgresql://{config.get('POSTGRES_USER', 'lightrag')}:"
            f"{config.get('POSTGRES_PASSWORD', '')}@localhost:"
            f"{config.get('POSTGRES_PORT', '5432')}/"
            f"{config.get('POSTGRES_DB', 'lightrag_cv')}"
        )

        with psycopg.connect(dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                # Check extensions
                cur.execute(
                    "SELECT extname FROM pg_extension WHERE extname IN ('vector', 'age')"
                )
                extensions = [row[0] for row in cur.fetchall()]

                result["healthy"] = True
                result["details"] = {
                    "connected": True,
                    "pgvector_installed": "vector" in extensions,
                    "age_installed": "age" in extensions
                }

    except Exception as e:
        result["details"]["error"] = str(e)

    return result


def check_http_service(name: str, url: str) -> Dict[str, Any]:
    """Check HTTP service health endpoint."""
    result = {
        "name": name,
        "healthy": False,
        "details": {}
    }

    try:
        response = httpx.get(url, timeout=5.0)
        result["healthy"] = response.status_code == 200
        result["details"] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        result["details"]["error"] = str(e)

    return result


def check_ollama(config: Dict[str, str]) -> Dict[str, Any]:
    """Check Ollama connectivity and models."""
    result = {
        "name": "Ollama",
        "healthy": False,
        "details": {}
    }

    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]

            required_models = [
                "qwen3:8b",
                "bge-m3:latest",
                "xitao/bge-reranker-v2-m3"
            ]

            models_present = {}
            for required in required_models:
                # Check for model with or without :latest
                present = any(
                    required in model or required.replace(":latest", "") in model
                    for model in models
                )
                models_present[required] = present

            result["healthy"] = True
            result["details"] = {
                "connected": True,
                "models": models_present,
                "total_models": len(models)
            }
    except Exception as e:
        result["details"]["error"] = str(e)

    return result


def main():
    """Main health check routine."""
    # Load configuration
    env = load_env()
    config = {**os.environ, **env}

    # Run checks
    checks = [
        check_postgres(config),
        check_http_service(
            "LightRAG",
            f"http://localhost:{config.get('LIGHTRAG_PORT', '9621')}/health"
        ),
        check_http_service(
            "Docling",
            f"http://localhost:{config.get('DOCLING_PORT', '8000')}/health"
        ),
        check_ollama(config),
    ]

    # Optional: MCP Server (may not be implemented yet)
    try:
        mcp_check = check_http_service(
            "MCP Server",
            f"http://localhost:{config.get('MCP_PORT', '3000')}/health"
        )
        checks.append(mcp_check)
    except:
        pass

    # Determine overall health
    all_healthy = all(check["healthy"] for check in checks)

    # Build report
    report = {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": "2025-11-03T10:00:00Z",  # TODO: Use actual timestamp
        "services": checks
    }

    # Output JSON
    print(json.dumps(report, indent=2))

    # Exit code
    sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    main()
