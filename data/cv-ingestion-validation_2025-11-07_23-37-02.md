# LightRAG CV Ingestion Validation Report

**Generated:** 2025-11-07 23:37:02

---

## Summary

- **Total CV Chunks:** 177
- **Total Entities:** 2847
- **Total Relationships:** 1966
- **Expected Vector Dimension:** 1024

---

## 1. Vector Validation

**Status:** success

**Total Chunks:** 177

### Sample Chunks

#### Chunk 1

- **ID:** chunk-b3eaf9a0dee3ad8014118f7e400cc973
- **File Path:** cv_cv_020_10
- **Chunk Order Index:** 0
- **Tokens:** 67
- **Content Preview:** [CANDIDATE_LABEL: cv_020]
[JOB_TITLE: Head/Lead Projects]
[ROLE_DOMAIN: Software Development]
[EXPERIENCE_LEVEL: senior]
[PAGE: 2]

Salary:
+ Full-time: 50 milion VN Đ / month
+ Part-time: 250.000 VN ...

#### Chunk 2

- **ID:** chunk-5b4ef98cb1b49df5cfd363ae97937e26
- **File Path:** cv_cv_020_9
- **Chunk Order Index:** 0
- **Tokens:** 55
- **Content Preview:** [CANDIDATE_LABEL: cv_020]
[JOB_TITLE: Head/Lead Projects]
[ROLE_DOMAIN: Software Development]
[EXPERIENCE_LEVEL: senior]
[PAGE: 2]

Traveling, Relaxing, Walking, Running, Footbal, ..

#### Chunk 3

- **ID:** chunk-7bbfa3a42fbb16ffa7629a2645437faa
- **File Path:** cv_cv_020_11
- **Chunk Order Index:** 0
- **Tokens:** 70
- **Content Preview:** [CANDIDATE_LABEL: cv_020]
[JOB_TITLE: Head/Lead Projects]
[ROLE_DOMAIN: Software Development]
[EXPERIENCE_LEVEL: senior]
[PAGE: 2]

MALL, MART, SUPERMARTKET, COFFEE STORE, DEPARTMENT STORE, ...
Projec...

#### Chunk 4

- **ID:** chunk-5c6b8fed05632bc2b907ad2fc0d0865d
- **File Path:** cv_cv_020_8
- **Chunk Order Index:** 0
- **Tokens:** 103
- **Content Preview:** [CANDIDATE_LABEL: cv_020]
[JOB_TITLE: Head/Lead Projects]
[ROLE_DOMAIN: Software Development]
[EXPERIENCE_LEVEL: senior]
[PAGE: 1]


COMPUTER SCIENCE
// 10/2008 - 10/2012
Ho Chi Minh city open univer...

#### Chunk 5

- **ID:** chunk-6fc80e0e27d47e2e534eabd795ce30b0
- **File Path:** cv_cv_020_13
- **Chunk Order Index:** 0
- **Tokens:** 100
- **Content Preview:** [CANDIDATE_LABEL: cv_020]
[JOB_TITLE: Head/Lead Projects]
[ROLE_DOMAIN: Software Development]
[EXPERIENCE_LEVEL: senior]
[PAGE: 2]

IOS Customer App, Android Customer App, Web Customer App, Web Api Se...

---

## 2. Entity Validation

**Status:** success

**Total Entities:** 2847

### Entity Counts by Category

- **Skills/Technologies:** 3
- **Companies:** 0
- **Roles:** 18
- **Education:** 0
- **Other:** 29

### Top Skills/Technologies

- **HTML** (count: 9)
- **Information Systems Governance** (count: 8)
- **Air Transport Business Management** (count: 6)

### Top Roles/Titles

- **Enterprise Architect** (count: 16)
- **Operation Manager** (count: 16)
- **Information Systems Consultant** (count: 13)
- **senior** (count: 13)
- **Account Manager** (count: 12)
- **Data Engineer** (count: 12)
- **Applications Manager** (count: 11)
- **Business Information System Manager** (count: 11)
- **Software Engineer** (count: 11)
- **Functional Architect** (count: 10)

---

## 3. Relationship Validation

**Status:** success

**Total Relationships:** 1966

### Relationship Types

- **unknown:** 1966

### Sample Relationships

1. **None** --[unknown]--> **None** (count: 1)
2. **None** --[unknown]--> **None** (count: 1)
3. **None** --[unknown]--> **None** (count: 1)
4. **None** --[unknown]--> **None** (count: 1)
5. **None** --[unknown]--> **None** (count: 1)
6. **None** --[unknown]--> **None** (count: 1)
7. **None** --[unknown]--> **None** (count: 1)
8. **None** --[unknown]--> **None** (count: 1)
9. **None** --[unknown]--> **None** (count: 1)
10. **None** --[unknown]--> **None** (count: 1)

---

## 4. Query Test Results

### query_1_python

**Query:** Find candidates with Python experience

**Description:** Test Python skill search

**Status:** success

**Result Preview:**
```
{'response': "### Candidates with Python Experience\n\nBased on the information provided in the **Context**, one candidate has explicit mention of having Python experience:\n\n- **Bansi Vasoya (cv_013)**: This candidate is a Software Engineer, and among other tools and technologies mentioned, they have proficiency in Python. Specifically:\n  - [CANDIDATE_LABEL: cv_013] indicates that Bansi Vasoya holds the position of a Software Engineer.\n  - The document chunks list various programming languag...
```

### query_2_angular_nodejs

**Query:** Find candidates with Angular and Node.js skills

**Description:** Test multi-skill search

**Status:** success

**Result Preview:**
```
{'response': 'Based on the information provided, there are several candidates who have demonstrated experience with both Angular and Node.js technologies.\n\n### Candidates with Angular and Node.js Skills\n\n1. **Adit (cv_013)**\n   - **Role:** Software Engineer\n   - **Angular Involvement:**\n     - Worked with Angular in various modules, including a calling module where external calls for patient details were recorded.\n     - Involved in the SMS module using Plivo for communication and file u...
```

---

## 5. Data Quality Issues

✅ **No data quality issues detected**

---

## Conclusion

✅ **Validation PASSED:** CV ingestion successful, all checks passed.

---

*Report generated by validate_lightrag.py on 2025-11-07 23:37:02*
