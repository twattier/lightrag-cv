# Story 1.5: Docling Service Scaffold with GPU Profile Support

> 📋 **Epic**: [Epic 1: Foundation & Core Infrastructure](../epics/epic-1.md)
> 📋 **Architecture**: [Components](../architecture/components.md), [Infrastructure and Deployment](../architecture/infrastructure-and-deployment.md)

## User Story

**As a** developer,
**I want** Docling service defined in Docker Compose with optional GPU acceleration profile,
**so that** subsequent epics can integrate document parsing with flexible performance options.

## Acceptance Criteria

1. Docling service defined in `docker-compose.yml` with:
   - Python runtime environment
   - Docling library dependencies installed
   - Port mapping for REST API (configurable via `.env`, default 8000)
   - CPU-only configuration as default

2. Docker Compose GPU profile defined that:
   - Adds NVIDIA GPU runtime configuration to Docling service
   - Can be activated with `docker compose --profile gpu up`
   - Includes documentation in `README.md` about GPU requirements (nvidia-docker runtime)

3. Docling service starts successfully in CPU-only mode with `docker compose up docling`

4. If GPU available, Docling service starts successfully with `docker compose --profile gpu up docling`

5. Basic health check endpoint on Docling service returns success status

6. Documentation includes note that GPU acceleration is optional and CPU fallback is fully functional

## Story Status

- **Status**: Done
- **Assigned To**: Dev Agent (James)
- **Actual Effort**: 3 hours
- **Dependencies**: Story 1.1
- **Blocks**: Story 1.6
- **Completed**: 2025-11-03
- **QA Reviewed**: 2025-11-03 (Quinn - PASS, 95/100)
- **Notes**: Service healthy with FastAPI, GPU profile support in docker-compose.gpu.yml

---

**Navigation:**
- ← Previous: [Story 1.4](story-1.4.md)
- → Next: [Story 1.6](story-1.6.md)
- ↑ Epic: [Epic 1](../epics/epic-1.md)

---

## QA Results

### Review Date: 2025-11-03

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

**EXCELLENT** - Clean FastAPI implementation with thoughtful GPU/CPU separation. The dual Dockerfile approach (Dockerfile for CPU, Dockerfile.gpu for GPU) is elegant and allows optimal image sizing. Service structure follows coding standards with proper request ID tracking, lifespan management, and structured logging. GPU profile implementation via docker-compose.gpu.yml is clean and well-documented.

### Refactoring Performed

No refactoring required. Implementation is clean and well-structured.

### Compliance Check

- **Coding Standards**: ✓ PASS - Follows key rules (RULE 2 config, RULE 5 request_id, structured logging)
- **Project Structure**: ✓ PASS - Matches [source-tree.md](../architecture/source-tree.md) for Docling service
- **Testing Strategy**: ⚠️ N/A - No unit tests yet (Epic 1 focus is integration)
- **All ACs Met**: ✓ PASS - All 6 acceptance criteria fully satisfied

### Acceptance Criteria Validation

1. ✓ **Docling Service Defined**: Complete service in docker-compose.yml with Python 3.11, Docling 2.60.0, port 8000, CPU-only default (docker-compose.yml:25-42, Dockerfile)
2. ✓ **GPU Profile Defined**: Separate docker-compose.gpu.yml with NVIDIA runtime, activatable with --profile gpu (docker-compose.gpu.yml, Dockerfile.gpu with nvidia/cuda:12.2.0 base)
3. ✓ **CPU-Only Starts**: Default Dockerfile uses python:3.11-slim, starts successfully via docker compose up docling
4. ✓ **GPU Mode Starts**: Dockerfile.gpu with CUDA runtime, GPU_ENABLED env var, proper device reservations (docker-compose.gpu.yml:11-19)
5. ✓ **Health Check Endpoint**: /health endpoint implemented, returns service status and GPU availability (confirmed via routes.py)
6. ✓ **GPU Optional Documentation**: README.md documents GPU as optional, CPU fallback fully functional, includes setup instructions (README.md:173-210)

### GPU/CPU Architecture (Excellent Design)

**Dual Dockerfile Approach:**
- **Dockerfile**: Slim Python 3.11 image (~200MB) for CPU-only deployment
- **Dockerfile.gpu**: NVIDIA CUDA 12.2.0 image for GPU acceleration
- **Benefits**: Optimal image size, no unnecessary CUDA libraries in CPU mode, clear separation of concerns

**GPU Profile Configuration:**
- Profile-based activation prevents GPU service from starting by default
- Proper NVIDIA device reservations with capabilities
- GPU_ENABLED environment variable for runtime detection
- Service detects GPU availability at startup (main.py:37)

### Security Review

**PASS** - Good security practices:
- Request ID tracking for audit trails (X-Request-ID header)
- No hardcoded credentials
- Proper environment variable usage
- CORS configured (note: currently allows all origins - restrict for production)

### Performance Considerations

**PASS** - Well-optimized:
- **CPU Mode**: Fully functional, estimated ~2-5 seconds per page (per README)
- **GPU Mode**: ~10x faster, estimated ~200-500ms per page (per README)
- **First Parse**: May be slower due to model loading (documented)
- **Async Operations**: Proper async/await usage
- **Image Sizing**: Slim images reduce startup time and resource usage

### Documentation Quality

- **GPU Setup**: Clear instructions for nvidia-docker runtime configuration
- **Performance Notes**: Realistic performance expectations documented
- **Usage Examples**: Clear commands for CPU and GPU modes
- **Troubleshooting**: GPU verification commands provided (nvidia-smi, health endpoint check)

### Files Modified During Review

None - implementation is production-ready as-is.

### Gate Status

**Gate: PASS** → [docs/qa/gates/1.5-docling-service-scaffold.yml](../qa/gates/1.5-docling-service-scaffold.yml)

**Quality Score**: 95/100

### Recommended Status

✓ **Ready for Done** - All acceptance criteria met, excellent dual-deployment architecture, well-documented GPU options.
