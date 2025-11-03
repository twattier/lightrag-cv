#!/usr/bin/env python3
"""
Validate Ollama connectivity and model availability.

This script verifies that Ollama is running and required models are available.
Run this before starting the LightRAG service.
"""

import json
import os
import sys
import time
from pathlib import Path

import httpx


def load_env() -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    env_file = Path(".env")

    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
                    except ValueError:
                        continue

    return env_vars


# Load configuration from .env
env_config = load_env()

OLLAMA_HOST_PORT = env_config.get("OLLAMA_HOST_PORT", "11434")
OLLAMA_BASE_URL = f"http://localhost:{OLLAMA_HOST_PORT}"

REQUIRED_MODELS = [
    env_config.get("OLLAMA_LLM_MODEL", "qwen3:8b"),
    env_config.get("OLLAMA_EMBEDDING_MODEL", "bge-m3:latest"),
    env_config.get("OLLAMA_RERANKER_MODEL", "xitao/bge-reranker-v2-m3")
]

EXPECTED_EMBEDDING_DIM = 1024


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    try:
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Ollama not accessible: {e}")
        return False


def list_available_models() -> list:
    """List all models available in Ollama."""
    try:
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return []


def validate_model_present(model_name: str, available_models: list) -> bool:
    """Check if a model is available."""
    # Ollama may return models with or without :latest suffix
    model_variants = [
        model_name,
        model_name.replace(":latest", ""),
        f"{model_name.split(':')[0]}:latest" if ":" not in model_name else model_name
    ]

    for variant in model_variants:
        if any(variant in available for available in available_models):
            return True
    return False


def test_generation(model: str = None) -> bool:
    """Test text generation with LLM model."""
    if model is None:
        model = REQUIRED_MODELS[0]  # Use LLM model from config
    print(f"\n🔄 Testing generation with {model}...")

    try:
        start_time = time.time()

        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": "Say 'Hello, LightRAG!' and nothing else.",
                "stream": False
            },
            timeout=60.0
        )
        response.raise_for_status()

        elapsed = time.time() - start_time
        result = response.json()

        print(f"✅ Generation successful (took {elapsed:.2f}s)")
        print(f"   Response: {result.get('response', '')[:100]}")

        if elapsed > 30:
            print("   ⚠️  First request was slow (model loading). Subsequent requests will be faster.")

        return True

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False


def test_embeddings(model: str = None) -> bool:
    """Test embedding generation with embedding model."""
    if model is None:
        model = REQUIRED_MODELS[1]  # Use embedding model from config
    print(f"\n🔄 Testing embeddings with {model}...")

    try:
        start_time = time.time()

        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": model,
                "prompt": "Test embedding for LightRAG validation"
            },
            timeout=60.0
        )
        response.raise_for_status()

        elapsed = time.time() - start_time
        result = response.json()
        embedding = result.get("embedding", [])

        if len(embedding) != EXPECTED_EMBEDDING_DIM:
            print(f"❌ Embedding dimension mismatch: got {len(embedding)}, expected {EXPECTED_EMBEDDING_DIM}")
            return False

        print(f"✅ Embeddings successful (took {elapsed:.2f}s)")
        print(f"   Embedding dimension: {len(embedding)} (correct)")

        if elapsed > 30:
            print("   ⚠️  First request was slow (model loading). Subsequent requests will be faster.")

        return True

    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False


def main():
    """Main validation routine."""
    print("=" * 60)
    print("Ollama Connectivity Validation")
    print("=" * 60)

    # Check Ollama is running
    print("\n🔄 Checking Ollama service...")
    if not check_ollama_running():
        print("\n❌ VALIDATION FAILED: Ollama is not running")
        print("\nTo start Ollama:")
        print("  1. Install Ollama from https://ollama.com")
        print("  2. Run: ollama serve")
        sys.exit(1)

    print("✅ Ollama service is running")

    # List available models
    print("\n🔄 Checking available models...")
    available_models = list_available_models()

    if not available_models:
        print("❌ No models found")
    else:
        print(f"✅ Found {len(available_models)} models:")
        for model in available_models:
            print(f"   - {model}")

    # Validate required models
    print("\n🔄 Validating required models...")
    missing_models = []

    for model in REQUIRED_MODELS:
        if validate_model_present(model, available_models):
            print(f"✅ {model} is available")
        else:
            print(f"❌ {model} is MISSING")
            missing_models.append(model)

    if missing_models:
        print("\n❌ VALIDATION FAILED: Missing required models")
        print("\nTo pull missing models:")
        for model in missing_models:
            print(f"  ollama pull {model}")
        sys.exit(1)

    # Test generation
    if not test_generation():
        print("\n❌ VALIDATION FAILED: Generation test failed")
        sys.exit(1)

    # Test embeddings
    if not test_embeddings():
        print("\n❌ VALIDATION FAILED: Embedding test failed")
        sys.exit(1)

    # Success
    print("\n" + "=" * 60)
    print("✅ ALL VALIDATIONS PASSED")
    print("=" * 60)
    print("\nOllama is configured correctly and ready for LightRAG.")
    print("\nNote: First requests to each model may take 30-60 seconds for model loading.")
    print("      Subsequent requests will be much faster (typically <1 second).")


if __name__ == "__main__":
    main()
