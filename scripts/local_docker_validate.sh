#!/bin/bash
# Local Docker Validation Script
# Part of DevOps Governor governance (DEC-DEVOPS-006)
#
# Validates Docker build and health check locally before Fly.io deployment.
# This catches container issues before consuming cloud resources.
#
# Usage:
#   local_docker_validate.sh [OPTIONS]
#
# Options:
#   --port PORT       Container port to expose (default: 8080)
#   --health PATH     Health check endpoint path (default: /health)
#   --timeout SECS    Health check timeout in seconds (default: 30)
#   --image NAME      Custom image name (default: project-local-test)
#   --dockerfile PATH Path to Dockerfile (default: ./Dockerfile)
#   --skip-cleanup    Don't remove container/image after validation
#   --quiet           Minimal output (for CI)
#
# Exit codes:
#   0 - All validations passed
#   1 - Docker build failed
#   2 - Container failed to start
#   3 - Health check failed
#   4 - Port binding failed
#   5 - Docker not available
#
# Evidence output: .claude/evidence/local_docker_validation.json

set -e

# Default values
PORT=8080
HEALTH_PATH="/health"
TIMEOUT=30
IMAGE_NAME="project-local-test"
DOCKERFILE="./Dockerfile"
SKIP_CLEANUP=false
QUIET=false
CONTAINER_NAME="local-docker-validate-$$"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --health)
            HEALTH_PATH="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --dockerfile)
            DOCKERFILE="$2"
            shift 2
            ;;
        --skip-cleanup)
            SKIP_CLEANUP=true
            shift
            ;;
        --quiet)
            QUIET=true
            shift
            ;;
        --help)
            head -30 "$0" | tail -28
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging functions
log() {
    if [ "$QUIET" = false ]; then
        echo -e "$1"
    fi
}

log_success() {
    log "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

log_warn() {
    log "${YELLOW}!${NC} $1"
}

# Cleanup function
cleanup() {
    if [ "$SKIP_CLEANUP" = false ]; then
        log "\nCleaning up..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        docker rmi "$IMAGE_NAME" 2>/dev/null || true
    fi
}

# Set up trap for cleanup
trap cleanup EXIT

# Initialize evidence
EVIDENCE_DIR=".claude/evidence"
EVIDENCE_FILE="$EVIDENCE_DIR/local_docker_validation.json"
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mkdir -p "$EVIDENCE_DIR"

write_evidence() {
    local status="$1"
    local exit_code="$2"
    local message="$3"
    local build_time="${4:-0}"
    local startup_time="${5:-0}"

    cat > "$EVIDENCE_FILE" << EOF
{
    "validation": "local_docker",
    "decision_ref": "DEC-DEVOPS-006",
    "timestamp": "$START_TIME",
    "completed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "status": "$status",
    "exit_code": $exit_code,
    "message": "$message",
    "config": {
        "port": $PORT,
        "health_path": "$HEALTH_PATH",
        "timeout": $TIMEOUT,
        "dockerfile": "$DOCKERFILE",
        "image_name": "$IMAGE_NAME"
    },
    "metrics": {
        "build_time_seconds": $build_time,
        "startup_time_seconds": $startup_time
    },
    "checks": {
        "docker_available": ${DOCKER_AVAILABLE:-false},
        "dockerfile_exists": ${DOCKERFILE_EXISTS:-false},
        "build_success": ${BUILD_SUCCESS:-false},
        "container_started": ${CONTAINER_STARTED:-false},
        "health_check_passed": ${HEALTH_PASSED:-false}
    }
}
EOF
}

# Check Docker is available
log "╔══════════════════════════════════════════════════════════════╗"
log "║           Local Docker Validation (DEC-DEVOPS-006)           ║"
log "╚══════════════════════════════════════════════════════════════╝"
log ""

log "Checking Docker availability..."
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    write_evidence "failed" 5 "Docker not available" 0 0
    exit 5
fi

if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    write_evidence "failed" 5 "Docker daemon not running" 0 0
    exit 5
fi
DOCKER_AVAILABLE=true
log_success "Docker is available"

# Check Dockerfile exists
log "\nChecking Dockerfile..."
if [ ! -f "$DOCKERFILE" ]; then
    log_error "Dockerfile not found at: $DOCKERFILE"
    write_evidence "failed" 1 "Dockerfile not found" 0 0
    exit 1
fi
DOCKERFILE_EXISTS=true
log_success "Dockerfile found: $DOCKERFILE"

# Build Docker image
log "\nBuilding Docker image..."
BUILD_START=$(date +%s)

if docker build -t "$IMAGE_NAME" -f "$DOCKERFILE" . ; then
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    BUILD_SUCCESS=true
    log_success "Docker build completed in ${BUILD_TIME}s"
else
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    log_error "Docker build failed after ${BUILD_TIME}s"
    write_evidence "failed" 1 "Docker build failed" "$BUILD_TIME" 0
    exit 1
fi

# Start container
log "\nStarting container..."
STARTUP_START=$(date +%s)

# Detect if we need to expose internal port differently
# Check fly.toml for internal port if it exists
INTERNAL_PORT=$PORT
if [ -f "fly.toml" ]; then
    DETECTED_PORT=$(grep -E "^\s*internal_port\s*=" fly.toml 2>/dev/null | head -1 | sed 's/.*=\s*//' | tr -d ' "')
    if [ -n "$DETECTED_PORT" ]; then
        INTERNAL_PORT=$DETECTED_PORT
        log_warn "Detected internal_port=$INTERNAL_PORT from fly.toml"
    fi
fi

if ! docker run -d --name "$CONTAINER_NAME" -p "${PORT}:${INTERNAL_PORT}" "$IMAGE_NAME"; then
    log_error "Failed to start container"
    write_evidence "failed" 2 "Container failed to start" "$BUILD_TIME" 0
    exit 2
fi

# Wait for container to stabilize (5 seconds)
log "Waiting for container to stabilize..."
sleep 5

# Check if container is still running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    log_error "Container exited unexpectedly"
    log "\nContainer logs:"
    docker logs "$CONTAINER_NAME" 2>&1 | tail -50
    write_evidence "failed" 2 "Container exited unexpectedly" "$BUILD_TIME" 5
    exit 2
fi
CONTAINER_STARTED=true
log_success "Container is running"

# Health check
log "\nRunning health check (timeout: ${TIMEOUT}s)..."
HEALTH_URL="http://localhost:${PORT}${HEALTH_PATH}"
log "  URL: $HEALTH_URL"

ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        STARTUP_END=$(date +%s)
        STARTUP_TIME=$((STARTUP_END - STARTUP_START))
        HEALTH_PASSED=true
        log_success "Health check passed in ${STARTUP_TIME}s"
        break
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    log "  Waiting... (${ELAPSED}/${TIMEOUT}s)"
done

if [ "$HEALTH_PASSED" != "true" ]; then
    log_error "Health check failed after ${TIMEOUT}s"
    log "\nContainer logs:"
    docker logs "$CONTAINER_NAME" 2>&1 | tail -50
    write_evidence "failed" 3 "Health check timed out" "$BUILD_TIME" "$TIMEOUT"
    exit 3
fi

# All checks passed
log ""
log "╔══════════════════════════════════════════════════════════════╗"
log "║                    ${GREEN}ALL VALIDATIONS PASSED${NC}                    ║"
log "╚══════════════════════════════════════════════════════════════╝"
log ""
log "  Build time:   ${BUILD_TIME}s"
log "  Startup time: ${STARTUP_TIME}s"
log "  Health URL:   $HEALTH_URL"
log ""
log "Evidence written to: $EVIDENCE_FILE"

write_evidence "passed" 0 "All validations passed" "$BUILD_TIME" "$STARTUP_TIME"
exit 0
