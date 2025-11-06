#!/usr/bin/env python3
"""
LLM Client Integration Test Script

Part of lightrag-cv application workflows.
Module: app.tests.test_llm_client

Tests LLM and embedding client connectivity using .env configuration.
Validates:
- LLM generation (text and JSON formats)
- Embedding generation
- Connection to configured providers
- Error handling

Usage:
    # Method 1: As a module (recommended)
    export PYTHONPATH=/home/ubuntu/dev/lightrag-cv
    python -m app.tests.test_llm_client

    # Method 2: Direct execution (auto-detects path)
    python3 app/tests/test_llm_client.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Auto-detect and add project root to sys.path if needed
# This allows both direct execution and module execution
if __name__ == "__main__":
    # Get the project root (3 levels up from this file)
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.shared.config import settings
from app.shared.llm_client import (
    get_llm_client,
    get_embedding_client,
    LLMTimeoutError,
    LLMProviderError,
    LLMResponseError
)


class TestResults:
    """Track test results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []

    def pass_test(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")

    def fail_test(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")

    def skip_test(self, test_name: str, reason: str):
        self.skipped += 1
        print(f"⏭️  SKIP: {test_name} - {reason}")

    def summary(self):
        total = self.passed + self.failed + self.skipped
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests:  {total}")
        print(f"Passed:       {self.passed} ✅")
        print(f"Failed:       {self.failed} ❌")
        print(f"Skipped:      {self.skipped} ⏭️")

        if self.failed > 0:
            print("\n" + "=" * 70)
            print("FAILED TESTS:")
            print("=" * 70)
            for test_name, error in self.errors:
                print(f"\n{test_name}:")
                print(f"  {error}")

        return self.failed == 0


def print_config():
    """Display current configuration."""
    print("=" * 70)
    print("CONFIGURATION")
    print("=" * 70)
    print(f"LLM Provider:       {settings.LLM_BINDING}")
    print(f"LLM Host:           {settings.LLM_BINDING_HOST}")
    print(f"LLM Model:          {settings.LLM_MODEL}")
    print(f"LLM Timeout:        {settings.LLM_TIMEOUT}s")
    print(f"LLM API Key:        {'Set' if settings.LLM_BINDING_API_KEY else 'None'}")
    print()
    print(f"Embedding Provider: {settings.EMBEDDING_BINDING}")
    print(f"Embedding Host:     {settings.EMBEDDING_BINDING_HOST}")
    print(f"Embedding Model:    {settings.EMBEDDING_MODEL}")
    print(f"Embedding Dim:      {settings.EMBEDDING_DIM}")
    print(f"Embedding Timeout:  {settings.EMBEDDING_TIMEOUT}s")
    print(f"Embedding API Key:  {'Set' if settings.EMBEDDING_BINDING_API_KEY else 'None'}")
    print("=" * 70)
    print()


async def test_llm_basic_generation(results: TestResults):
    """Test 1: Basic LLM text generation."""
    test_name = "LLM Basic Text Generation"

    try:
        print(f"\n🔍 Testing: {test_name}")
        print("   Prompt: 'What is 2+2? Answer in one word.'")

        client = get_llm_client()
        response = await client.generate(
            prompt="What is 2+2? Answer in one word.",
            temperature=0.1
        )

        if response and len(response) > 0:
            print(f"   Response: {response[:100]}")
            results.pass_test(test_name)
        else:
            results.fail_test(test_name, f"Empty response received (likely due to token limit or model issue)")

    except LLMTimeoutError as e:
        results.fail_test(test_name, f"Timeout: {e}")
    except LLMProviderError as e:
        results.fail_test(test_name, f"Provider error: {e}")
    except Exception as e:
        results.fail_test(test_name, f"Unexpected error: {e}")


async def test_llm_json_generation(results: TestResults):
    """Test 2: LLM JSON format generation."""
    test_name = "LLM JSON Format Generation"

    try:
        print(f"\n🔍 Testing: {test_name}")
        print("   Prompt: 'Generate JSON with name and age fields'")

        client = get_llm_client()
        response = await client.generate(
            prompt='Generate a JSON object with these fields: {"name": "John", "age": 30}',
            temperature=0.1,
            format="json"
        )

        # Validate JSON format
        parsed = json.loads(response)

        if isinstance(parsed, dict):
            print(f"   Response (parsed): {parsed}")
            results.pass_test(test_name)
        else:
            results.fail_test(test_name, f"Response is not a JSON object: {type(parsed)}")

    except json.JSONDecodeError as e:
        results.fail_test(test_name, f"Invalid JSON response: {e}")
    except LLMTimeoutError as e:
        results.fail_test(test_name, f"Timeout: {e}")
    except LLMProviderError as e:
        results.fail_test(test_name, f"Provider error: {e}")
    except Exception as e:
        results.fail_test(test_name, f"Unexpected error: {e}")


async def test_llm_longer_generation(results: TestResults):
    """Test 3: LLM longer text generation."""
    test_name = "LLM Longer Text Generation"

    try:
        print(f"\n🔍 Testing: {test_name}")
        print("   Prompt: 'Explain Python in 2 sentences'")

        client = get_llm_client()
        response = await client.generate(
            prompt="Explain what Python programming language is in exactly 2 sentences.",
            temperature=0.7
        )

        if response and len(response) > 50:
            print(f"   Response length: {len(response)} chars")
            print(f"   Response preview: {response[:150]}...")
            results.pass_test(test_name)
        else:
            results.fail_test(test_name, f"Response too short: {len(response)} chars")

    except LLMTimeoutError as e:
        results.fail_test(test_name, f"Timeout: {e}")
    except LLMProviderError as e:
        results.fail_test(test_name, f"Provider error: {e}")
    except Exception as e:
        results.fail_test(test_name, f"Unexpected error: {e}")


async def test_embedding_single_text(results: TestResults):
    """Test 4: Single text embedding generation."""
    test_name = "Embedding Single Text"

    try:
        print(f"\n🔍 Testing: {test_name}")
        print("   Text: 'Hello, world!'")

        client = get_embedding_client()
        vector = await client.embed("Hello, world!")

        expected_dim = settings.EMBEDDING_DIM

        if isinstance(vector, list) and len(vector) == expected_dim:
            print(f"   Vector dimension: {len(vector)} (expected: {expected_dim})")
            print(f"   First 5 values: {vector[:5]}")
            print(f"   Vector type: {type(vector[0])}")
            results.pass_test(test_name)
        else:
            results.fail_test(
                test_name,
                f"Invalid embedding: expected list of {expected_dim} floats, got {type(vector)} with length {len(vector) if isinstance(vector, list) else 'N/A'}"
            )

    except LLMTimeoutError as e:
        results.fail_test(test_name, f"Timeout: {e}")
    except LLMProviderError as e:
        results.fail_test(test_name, f"Provider error: {e}")
    except Exception as e:
        results.fail_test(test_name, f"Unexpected error: {e}")


async def test_embedding_longer_text(results: TestResults):
    """Test 5: Longer text embedding generation."""
    test_name = "Embedding Longer Text"

    try:
        print(f"\n🔍 Testing: {test_name}")

        long_text = """
        Python is a high-level, interpreted programming language known for its readability
        and versatility. It supports multiple programming paradigms including procedural,
        object-oriented, and functional programming.
        """

        print(f"   Text length: {len(long_text)} chars")

        client = get_embedding_client()
        vector = await client.embed(long_text)

        expected_dim = settings.EMBEDDING_DIM

        if isinstance(vector, list) and len(vector) == expected_dim:
            print(f"   Vector dimension: {len(vector)} (expected: {expected_dim})")
            print(f"   First 5 values: {vector[:5]}")
            results.pass_test(test_name)
        else:
            results.fail_test(
                test_name,
                f"Invalid embedding: expected list of {expected_dim} floats, got length {len(vector) if isinstance(vector, list) else 'N/A'}"
            )

    except LLMTimeoutError as e:
        results.fail_test(test_name, f"Timeout: {e}")
    except LLMProviderError as e:
        results.fail_test(test_name, f"Provider error: {e}")
    except Exception as e:
        results.fail_test(test_name, f"Unexpected error: {e}")


async def test_embedding_consistency(results: TestResults):
    """Test 6: Embedding consistency (same text = similar vectors)."""
    test_name = "Embedding Consistency"

    try:
        print(f"\n🔍 Testing: {test_name}")
        print("   Testing same text produces similar embeddings")

        text = "The quick brown fox jumps over the lazy dog"

        client = get_embedding_client()
        vector1 = await client.embed(text)
        vector2 = await client.embed(text)

        # Calculate cosine similarity
        import math

        def cosine_similarity(v1, v2):
            dot_product = sum(a * b for a, b in zip(v1, v2))
            magnitude1 = math.sqrt(sum(a * a for a in v1))
            magnitude2 = math.sqrt(sum(b * b for b in v2))
            return dot_product / (magnitude1 * magnitude2)

        similarity = cosine_similarity(vector1, vector2)

        print(f"   Cosine similarity: {similarity:.6f}")

        # Embeddings should be very similar (>0.99) for identical text
        if similarity > 0.99:
            results.pass_test(test_name)
        else:
            results.fail_test(test_name, f"Similarity too low: {similarity:.6f} (expected > 0.99)")

    except LLMTimeoutError as e:
        results.fail_test(test_name, f"Timeout: {e}")
    except LLMProviderError as e:
        results.fail_test(test_name, f"Provider error: {e}")
    except Exception as e:
        results.fail_test(test_name, f"Unexpected error: {e}")


async def run_all_tests():
    """Run all integration tests."""
    print_config()

    results = TestResults()

    print("\n" + "=" * 70)
    print("RUNNING LLM CLIENT INTEGRATION TESTS")
    print("=" * 70)

    # LLM Tests
    await test_llm_basic_generation(results)
    await test_llm_json_generation(results)
    await test_llm_longer_generation(results)

    # Embedding Tests
    await test_embedding_single_text(results)
    await test_embedding_longer_text(results)
    await test_embedding_consistency(results)

    # Print summary
    success = results.summary()

    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nLLM client is properly configured and working!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        print("\nPlease check:")
        print("1. Services are running (Ollama at configured host)")
        print("2. Models are pulled:")
        print(f"   - LLM Model: {settings.LLM_MODEL}")
        print(f"   - Embedding Model: {settings.EMBEDDING_MODEL}")
        print("3. .env configuration is correct")
        print("4. Network connectivity to provider hosts")
        return 1


def main():
    """Main entry point."""
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
