-- Story 2.9.2: CV Custom Entity Creation - Validation Queries
-- Run these queries after CV import to verify entity and relationship creation

-- Query 1: Count entities by type
-- Expected: ~46 CV entities (one per CV with is_latin_text=true)
-- Expected: ~10-15 DOMAIN_JOB entities (shared)
-- Expected: ~30-40 JOB entities (shared)
-- Expected: ~3 XP entities (Junior, Mid, Senior)
SELECT entity_type, COUNT(*) as count
FROM lightrag_full_entities
WHERE entity_type IN ('CV', 'DOMAIN_JOB', 'JOB', 'XP')
GROUP BY entity_type
ORDER BY entity_type;

-- Query 2: Sample CV entities
SELECT entity_name, entity_type, description
FROM lightrag_full_entities
WHERE entity_type = 'CV'
LIMIT 10;

-- Query 3: Sample shared entities
SELECT entity_name, entity_type, description
FROM lightrag_full_entities
WHERE entity_type IN ('DOMAIN_JOB', 'JOB', 'XP')
ORDER BY entity_type, entity_name
LIMIT 20;

-- Query 4: Count relationships by type
-- Expected CV-specific relationships: ~46 per type (WORKS_IN, HAS_JOB_TITLE, HAS_EXPERIENCE_LEVEL)
-- Expected shared relationships: ~30-40 INCLUDES_JOB (unique domain-job pairs), ~30-40 REQUIRES_LEVEL (unique job-level pairs)
-- Total: ~210-250 relationships (138 CV-specific + 60-80 shared)
SELECT relation, COUNT(*) as count
FROM lightrag_full_relations
WHERE relation IN (
  'WORKS_IN', 'HAS_JOB_TITLE', 'HAS_EXPERIENCE_LEVEL',
  'INCLUDES_JOB', 'REQUIRES_LEVEL'
)
GROUP BY relation
ORDER BY relation;

-- Query 5: Sample CV relationships
SELECT src_id, relation, tgt_id
FROM lightrag_full_relations
WHERE src_id LIKE 'cv_%'
  AND relation IN ('WORKS_IN', 'HAS_JOB_TITLE', 'HAS_EXPERIENCE_LEVEL')
LIMIT 20;

-- Query 6: Sample shared relationships
SELECT src_id, relation, tgt_id
FROM lightrag_full_relations
WHERE relation IN ('INCLUDES_JOB', 'REQUIRES_LEVEL')
LIMIT 20;

-- Query 7: Find all CVs in "Software Development" domain
-- (or substitute with any domain from your data)
SELECT cv.entity_name, cv.description
FROM lightrag_full_entities cv
JOIN lightrag_full_relations r ON r.src_id = cv.entity_name
JOIN lightrag_full_entities domain ON domain.entity_name = r.tgt_id
WHERE cv.entity_type = 'CV'
  AND r.relation = 'WORKS_IN'
  AND domain.entity_name LIKE '%Software%';

-- Query 8: Find all Senior-level CVs
SELECT cv.entity_name, cv.description
FROM lightrag_full_entities cv
JOIN lightrag_full_relations r ON r.src_id = cv.entity_name
JOIN lightrag_full_entities xp ON xp.entity_name = r.tgt_id
WHERE cv.entity_type = 'CV'
  AND r.relation = 'HAS_EXPERIENCE_LEVEL'
  AND xp.entity_name IN ('senior', 'Senior');

-- Query 9: Verify CV entity structure
-- Each CV should have exactly 3 outgoing relationships
SELECT cv.entity_name,
       COUNT(CASE WHEN r.relation = 'WORKS_IN' THEN 1 END) as works_in_count,
       COUNT(CASE WHEN r.relation = 'HAS_JOB_TITLE' THEN 1 END) as job_title_count,
       COUNT(CASE WHEN r.relation = 'HAS_EXPERIENCE_LEVEL' THEN 1 END) as experience_level_count
FROM lightrag_full_entities cv
LEFT JOIN lightrag_full_relations r ON r.src_id = cv.entity_name
WHERE cv.entity_type = 'CV'
GROUP BY cv.entity_name
HAVING COUNT(r.relation) != 3
LIMIT 10;
-- Should return 0 rows if all CVs have correct relationships

-- Query 10: List all unique experience levels
SELECT DISTINCT entity_name
FROM lightrag_full_entities
WHERE entity_type = 'XP'
ORDER BY entity_name;
