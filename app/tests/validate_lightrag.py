#!/usr/bin/env python3
"""
LightRAG CV ingestion validation script.

This script validates that CVs have been successfully ingested into LightRAG by:
1. Validating vector embeddings storage
2. Validating knowledge graph entities
3. Validating knowledge graph relationships
4. Testing LightRAG query endpoint
5. Generating a validation report

Usage:
    python -m app.tests.validate_lightrag
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import psycopg

from app.shared.config import settings

# Configure logging with structured context (RULE 7)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LightRAGValidator:
    """Validator for LightRAG CV ingestion."""

    def __init__(self):
        """Initialize validator with database and HTTP connections."""
        self.postgres_dsn = settings.postgres_dsn
        self.lightrag_url = settings.lightrag_url
        self.data_dir = settings.DATA_DIR
        self.results: Dict[str, Any] = {}

    async def validate_vectors(self, conn) -> Dict[str, Any]:
        """
        Validate CV vector embeddings storage (AC: 1).

        Queries:
        - Count of CV chunks in lightrag_vdb_chunks
        - Sample 5 chunks to verify structure
        - Verify file_path contains 'cv_' prefix for CV documents
        """
        logger.info("Starting vector validation")

        try:
            # Count CV chunks (filter by file_path containing 'cv_')
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT COUNT(*)
                    FROM lightrag_vdb_chunks
                    WHERE workspace='default'
                    AND file_path LIKE 'cv_%'
                """)
                result = await cur.fetchone()
                total_chunks = result[0] if result else 0

                logger.info(
                    "CV chunks counted",
                    extra={"total_chunks": total_chunks}
                )

                # Sample 5 chunks to verify structure
                await cur.execute("""
                    SELECT id, content, file_path, chunk_order_index, tokens
                    FROM lightrag_vdb_chunks
                    WHERE workspace='default'
                    AND file_path LIKE 'cv_%'
                    ORDER BY create_time DESC
                    LIMIT 5
                """)
                samples = await cur.fetchall()

                sample_chunks = []
                for row in samples:
                    chunk_id, content, file_path, chunk_order, tokens = row
                    sample_chunks.append({
                        "id": chunk_id,
                        "content_preview": content[:200] + "..." if len(content) > 200 else content,
                        "file_path": file_path,
                        "chunk_order_index": chunk_order,
                        "tokens": tokens
                    })

                logger.info(
                    "Vector validation completed",
                    extra={
                        "total_chunks": total_chunks,
                        "samples_retrieved": len(sample_chunks)
                    }
                )

                return {
                    "total_chunks": total_chunks,
                    "sample_chunks": sample_chunks,
                    "expected_dimension": 1024,
                    "status": "success"
                }

        except Exception as e:
            logger.error(
                "Vector validation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "total_chunks": 0,
                "sample_chunks": [],
                "status": "error",
                "error": str(e)
            }

    async def validate_entities(self, conn) -> Dict[str, Any]:
        """
        Validate knowledge graph entities (AC: 2).

        Identifies:
        - Skills/technologies (Python, JavaScript, AWS, etc.)
        - Companies/employers
        - Roles/titles held
        - Education and certifications
        """
        logger.info("Starting entity validation")

        try:
            async with conn.cursor() as cur:
                # Get total entity count (sum of all entity counts from all documents)
                await cur.execute("""
                    SELECT SUM(count) as total_entities
                    FROM lightrag_full_entities
                    WHERE workspace='default'
                """)
                result = await cur.fetchone()
                total_entities = result[0] if result else 0

                # Get individual entities expanded from JSONB arrays with frequency count
                await cur.execute("""
                    SELECT
                        entity_name,
                        COUNT(*) as document_count
                    FROM (
                        SELECT
                            id as document_id,
                            jsonb_array_elements_text(entity_names) as entity_name
                        FROM lightrag_full_entities
                        WHERE workspace = 'default'
                    ) entities
                    GROUP BY entity_name
                    ORDER BY document_count DESC, entity_name
                    LIMIT 50
                """)
                entities = await cur.fetchall()

                # Categorize entities (heuristic-based)
                skills = []
                companies = []
                roles = []
                education = []
                other = []

                # Common skill/technology keywords
                skill_keywords = [
                    'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
                    'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'spring',
                    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
                    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
                    'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum',
                    'ml', 'ai', 'machine learning', 'deep learning', 'tensorflow', 'pytorch'
                ]

                role_keywords = [
                    'engineer', 'developer', 'architect', 'manager', 'lead', 'senior',
                    'analyst', 'consultant', 'specialist', 'administrator', 'designer'
                ]

                education_keywords = [
                    'university', 'college', 'institute', 'degree', 'bachelor', 'master',
                    'phd', 'certification', 'certified', 'diploma'
                ]

                for row in entities:
                    entity_name, document_count = row
                    entity_lower = entity_name.lower()

                    entity_info = {
                        "name": entity_name,
                        "count": document_count
                    }

                    # Categorize based on name
                    if any(skill in entity_lower for skill in skill_keywords):
                        skills.append(entity_info)
                    elif any(role in entity_lower for role in role_keywords):
                        roles.append(entity_info)
                    elif any(edu in entity_lower for edu in education_keywords):
                        education.append(entity_info)
                    else:
                        other.append(entity_info)

                logger.info(
                    "Entity validation completed",
                    extra={
                        "total_entities": total_entities,
                        "skills_count": len(skills),
                        "companies_count": len(companies),
                        "roles_count": len(roles),
                        "education_count": len(education)
                    }
                )

                return {
                    "total_entities": total_entities,
                    "skills": skills,
                    "companies": companies,
                    "roles": roles,
                    "education": education,
                    "other": other,
                    "status": "success"
                }

        except Exception as e:
            logger.error(
                "Entity validation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "total_entities": 0,
                "skills": [],
                "companies": [],
                "roles": [],
                "education": [],
                "other": [],
                "status": "error",
                "error": str(e)
            }

    async def validate_relationships(self, conn) -> Dict[str, Any]:
        """
        Validate knowledge graph relationships (AC: 3).

        Identifies:
        - CV internal relationships (candidate → skill, candidate → company)
        - Cross-document relationships (CV skill → CIGREF skill linking)
        """
        logger.info("Starting relationship validation")

        try:
            async with conn.cursor() as cur:
                # Get total relationship count (sum from all documents)
                await cur.execute("""
                    SELECT SUM(count) as total_relationships
                    FROM lightrag_full_relations
                    WHERE workspace='default'
                """)
                result = await cur.fetchone()
                total_relationships = result[0] if result else 0

                # Get individual relationships expanded from JSONB arrays
                await cur.execute("""
                    SELECT
                        rel_pair->>'src' as source_entity,
                        rel_pair->>'tgt' as target_entity,
                        rel_pair->>'description' as relationship_description
                    FROM lightrag_full_relations,
                         jsonb_array_elements(relation_pairs) as rel_pair
                    WHERE workspace='default'
                    ORDER BY id DESC
                    LIMIT 50
                """)
                relationships = await cur.fetchall()

                # Get relationship type counts (by description)
                await cur.execute("""
                    SELECT
                        rel_pair->>'description' as relationship_type,
                        COUNT(*) as occurrence_count
                    FROM lightrag_full_relations,
                         jsonb_array_elements(relation_pairs) as rel_pair
                    WHERE workspace='default'
                    GROUP BY rel_pair->>'description'
                    ORDER BY occurrence_count DESC
                    LIMIT 20
                """)
                type_counts = await cur.fetchall()

                relationship_types = {
                    row[0] or "unknown": row[1] for row in type_counts
                }

                sample_relationships = []
                for row in relationships[:20]:  # Limit to 20 samples for report
                    source, target, description = row
                    sample_relationships.append({
                        "source": source,
                        "relationship": description or "unknown",
                        "target": target,
                        "count": 1  # Individual occurrence
                    })

                logger.info(
                    "Relationship validation completed",
                    extra={
                        "total_relationships": total_relationships,
                        "relationship_types": len(relationship_types)
                    }
                )

                return {
                    "total_relationships": total_relationships,
                    "relationship_types": relationship_types,
                    "sample_relationships": sample_relationships,
                    "status": "success"
                }

        except Exception as e:
            logger.error(
                "Relationship validation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "total_relationships": 0,
                "relationship_types": {},
                "sample_relationships": [],
                "status": "error",
                "error": str(e)
            }

    async def test_queries(self) -> Dict[str, Any]:
        """
        Test LightRAG query endpoint (AC: 4).

        Test queries:
        1. "Find candidates with Python experience"
        2. "Find candidates with Angular and Node.js skills"
        """
        logger.info("Starting query tests")

        query_results = {}

        test_queries = [
            {
                "name": "query_1_python",
                "query": "Find candidates with Python experience",
                "description": "Test Python skill search"
            },
            {
                "name": "query_2_angular_nodejs",
                "query": "Find candidates with Angular and Node.js skills",
                "description": "Test multi-skill search"
            }
        ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            for test in test_queries:
                try:
                    logger.info(
                        "Executing test query",
                        extra={"query_name": test["name"], "query": test["query"]}
                    )

                    payload = {
                        "query": test["query"],
                        "mode": "hybrid",
                        "top_k": 5
                    }

                    response = await client.post(
                        f"{self.lightrag_url}/query",
                        json=payload
                    )
                    response.raise_for_status()

                    result = response.json()

                    # Extract relevant information
                    query_results[test["name"]] = {
                        "query": test["query"],
                        "description": test["description"],
                        "status": "success",
                        "response_received": True,
                        "result_preview": str(result)[:500] + "..." if len(str(result)) > 500 else str(result)
                    }

                    logger.info(
                        "Query test completed",
                        extra={"query_name": test["name"], "status": "success"}
                    )

                except httpx.HTTPError as e:
                    logger.error(
                        "Query test failed",
                        extra={"query_name": test["name"], "error": str(e)},
                        exc_info=True
                    )
                    query_results[test["name"]] = {
                        "query": test["query"],
                        "description": test["description"],
                        "status": "error",
                        "error": str(e)
                    }
                except Exception as e:
                    logger.error(
                        "Query test failed unexpectedly",
                        extra={"query_name": test["name"], "error": str(e)},
                        exc_info=True
                    )
                    query_results[test["name"]] = {
                        "query": test["query"],
                        "description": test["description"],
                        "status": "error",
                        "error": str(e)
                    }

        return {
            "query_results": query_results,
            "status": "success"
        }

    async def generate_report(self, results: Dict[str, Any]) -> Path:
        """
        Generate markdown validation report (AC: 5).

        Report includes:
        - Summary: Total CVs, chunks, entities, relationships
        - Vector Validation: Chunk count, sample chunks
        - Entity Validation: Entity counts by type, top entities
        - Relationship Validation: Relationship counts, sample relationships
        - Query Test Results: Results for each test query
        - Data Quality Issues: Any anomalies or concerns
        """
        logger.info("Generating validation report")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = self.data_dir / f"cv-ingestion-validation_{timestamp}.md"

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Build report content
        report_lines = [
            "# LightRAG CV Ingestion Validation Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Summary",
            "",
        ]

        # Summary section
        vectors = results.get("vectors", {})
        entities = results.get("entities", {})
        relationships = results.get("relationships", {})

        report_lines.extend([
            f"- **Total CV Chunks:** {vectors.get('total_chunks', 0)}",
            f"- **Total Entities:** {entities.get('total_entities', 0)}",
            f"- **Total Relationships:** {relationships.get('total_relationships', 0)}",
            f"- **Expected Vector Dimension:** {vectors.get('expected_dimension', 1024)}",
            "",
            "---",
            "",
        ])

        # Vector Validation section
        report_lines.extend([
            "## 1. Vector Validation",
            "",
            f"**Status:** {vectors.get('status', 'unknown')}",
            "",
            f"**Total Chunks:** {vectors.get('total_chunks', 0)}",
            "",
        ])

        if vectors.get('status') == 'error':
            report_lines.extend([
                f"**Error:** {vectors.get('error', 'Unknown error')}",
                "",
            ])
        else:
            sample_chunks = vectors.get('sample_chunks', [])
            if sample_chunks:
                report_lines.extend([
                    "### Sample Chunks",
                    "",
                ])
                for i, chunk in enumerate(sample_chunks, 1):
                    report_lines.extend([
                        f"#### Chunk {i}",
                        "",
                        f"- **ID:** {chunk.get('id', 'N/A')}",
                        f"- **File Path:** {chunk.get('file_path', 'N/A')}",
                        f"- **Chunk Order Index:** {chunk.get('chunk_order_index', 'N/A')}",
                        f"- **Tokens:** {chunk.get('tokens', 'N/A')}",
                        f"- **Content Preview:** {chunk.get('content_preview', 'N/A')}",
                        "",
                    ])

        report_lines.extend([
            "---",
            "",
        ])

        # Entity Validation section
        report_lines.extend([
            "## 2. Entity Validation",
            "",
            f"**Status:** {entities.get('status', 'unknown')}",
            "",
            f"**Total Entities:** {entities.get('total_entities', 0)}",
            "",
        ])

        if entities.get('status') == 'error':
            report_lines.extend([
                f"**Error:** {entities.get('error', 'Unknown error')}",
                "",
            ])
        else:
            report_lines.extend([
                "### Entity Counts by Category",
                "",
                f"- **Skills/Technologies:** {len(entities.get('skills', []))}",
                f"- **Companies:** {len(entities.get('companies', []))}",
                f"- **Roles:** {len(entities.get('roles', []))}",
                f"- **Education:** {len(entities.get('education', []))}",
                f"- **Other:** {len(entities.get('other', []))}",
                "",
            ])

            # Top skills
            skills = entities.get('skills', [])
            if skills:
                report_lines.extend([
                    "### Top Skills/Technologies",
                    "",
                ])
                for skill in skills[:10]:
                    report_lines.append(
                        f"- **{skill['name']}** (count: {skill['count']})"
                    )
                report_lines.append("")

            # Top roles
            roles = entities.get('roles', [])
            if roles:
                report_lines.extend([
                    "### Top Roles/Titles",
                    "",
                ])
                for role in roles[:10]:
                    report_lines.append(
                        f"- **{role['name']}** (count: {role['count']})"
                    )
                report_lines.append("")

            # Top companies
            companies = entities.get('companies', [])
            if companies:
                report_lines.extend([
                    "### Top Companies",
                    "",
                ])
                for company in companies[:10]:
                    report_lines.append(
                        f"- **{company['name']}** (count: {company['count']})"
                    )
                report_lines.append("")

        report_lines.extend([
            "---",
            "",
        ])

        # Relationship Validation section
        report_lines.extend([
            "## 3. Relationship Validation",
            "",
            f"**Status:** {relationships.get('status', 'unknown')}",
            "",
            f"**Total Relationships:** {relationships.get('total_relationships', 0)}",
            "",
        ])

        if relationships.get('status') == 'error':
            report_lines.extend([
                f"**Error:** {relationships.get('error', 'Unknown error')}",
                "",
            ])
        else:
            rel_types = relationships.get('relationship_types', {})
            if rel_types:
                report_lines.extend([
                    "### Relationship Types",
                    "",
                ])
                for rel_type, count in list(rel_types.items())[:10]:
                    report_lines.append(f"- **{rel_type}:** {count}")
                report_lines.append("")

            samples = relationships.get('sample_relationships', [])
            if samples:
                report_lines.extend([
                    "### Sample Relationships",
                    "",
                ])
                for i, rel in enumerate(samples[:10], 1):
                    report_lines.append(
                        f"{i}. **{rel['source']}** --[{rel['relationship']}]--> **{rel['target']}** (count: {rel['count']})"
                    )
                report_lines.append("")

        report_lines.extend([
            "---",
            "",
        ])

        # Query Test Results section
        queries = results.get("queries", {})
        query_results = queries.get('query_results', {})

        report_lines.extend([
            "## 4. Query Test Results",
            "",
        ])

        for query_name, query_result in query_results.items():
            report_lines.extend([
                f"### {query_name}",
                "",
                f"**Query:** {query_result.get('query', 'N/A')}",
                "",
                f"**Description:** {query_result.get('description', 'N/A')}",
                "",
                f"**Status:** {query_result.get('status', 'unknown')}",
                "",
            ])

            if query_result.get('status') == 'error':
                report_lines.extend([
                    f"**Error:** {query_result.get('error', 'Unknown error')}",
                    "",
                ])
            else:
                report_lines.extend([
                    "**Result Preview:**",
                    "```",
                    query_result.get('result_preview', 'No result'),
                    "```",
                    "",
                ])

        report_lines.extend([
            "---",
            "",
        ])

        # Data Quality Issues section
        report_lines.extend([
            "## 5. Data Quality Issues",
            "",
        ])

        issues = []

        # Check for missing data
        if vectors.get('total_chunks', 0) == 0:
            issues.append("- **CRITICAL:** No CV chunks found in database")

        if entities.get('total_entities', 0) == 0:
            issues.append("- **CRITICAL:** No entities extracted")

        if relationships.get('total_relationships', 0) == 0:
            issues.append("- **WARNING:** No relationships found")

        # Check for errors
        if vectors.get('status') == 'error':
            issues.append(f"- **ERROR:** Vector validation failed: {vectors.get('error', 'Unknown')}")

        if entities.get('status') == 'error':
            issues.append(f"- **ERROR:** Entity validation failed: {entities.get('error', 'Unknown')}")

        if relationships.get('status') == 'error':
            issues.append(f"- **ERROR:** Relationship validation failed: {relationships.get('error', 'Unknown')}")

        # Check query results
        for query_name, query_result in query_results.items():
            if query_result.get('status') == 'error':
                issues.append(f"- **ERROR:** Query test '{query_name}' failed: {query_result.get('error', 'Unknown')}")

        if not issues:
            report_lines.append("✅ **No data quality issues detected**")
        else:
            report_lines.extend(issues)

        report_lines.extend([
            "",
            "---",
            "",
            "## Conclusion",
            "",
        ])

        # Overall assessment
        all_success = (
            vectors.get('status') == 'success' and
            entities.get('status') == 'success' and
            relationships.get('status') == 'success' and
            vectors.get('total_chunks', 0) > 0
        )

        if all_success:
            report_lines.append("✅ **Validation PASSED:** CV ingestion successful, all checks passed.")
        else:
            report_lines.append("❌ **Validation FAILED:** Issues detected, please review above sections.")

        report_lines.extend([
            "",
            "---",
            "",
            f"*Report generated by validate_lightrag.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])

        # Write report to file
        report_content = "\n".join(report_lines)
        report_path.write_text(report_content, encoding='utf-8')

        logger.info(
            "Validation report generated",
            extra={"report_path": str(report_path)}
        )

        return report_path

    async def run_validation(self):
        """Execute all validations and generate report."""
        logger.info("Starting LightRAG validation")

        results = {}

        # Connect to PostgreSQL
        try:
            logger.info(
                "Connecting to PostgreSQL",
                extra={
                    "host": settings.POSTGRES_HOST,
                    "port": settings.POSTGRES_PORT,
                    "database": settings.POSTGRES_DB
                }
            )

            async with await psycopg.AsyncConnection.connect(
                self.postgres_dsn,
                autocommit=True
            ) as conn:
                # Run vector validation
                results['vectors'] = await self.validate_vectors(conn)

                # Run entity validation
                results['entities'] = await self.validate_entities(conn)

                # Run relationship validation
                results['relationships'] = await self.validate_relationships(conn)

        except Exception as e:
            logger.error(
                "Database connection failed",
                extra={"error": str(e)},
                exc_info=True
            )
            results['vectors'] = {"status": "error", "error": f"Database connection failed: {str(e)}"}
            results['entities'] = {"status": "error", "error": f"Database connection failed: {str(e)}"}
            results['relationships'] = {"status": "error", "error": f"Database connection failed: {str(e)}"}

        # Run query tests (independent of database connection)
        results['queries'] = await self.test_queries()

        # Generate report
        try:
            report_path = await self.generate_report(results)
            print(f"\n{'='*80}")
            print(f"✅ Validation report generated:")
            print(f"   {report_path}")
            print(f"{'='*80}\n")
            return 0
        except Exception as e:
            logger.error(
                "Report generation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            print(f"\n{'='*80}")
            print(f"❌ Report generation failed: {str(e)}")
            print(f"{'='*80}\n")
            return 1


async def main():
    """Main entry point."""
    validator = LightRAGValidator()
    return await validator.run_validation()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
