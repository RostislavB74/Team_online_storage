#!/bin/bash

RESULT_FILE=${RESULT_FILE:-/build/build_info.env}
[ -d "/build" ] || RESULT_FILE="./build_info.env"

GIT_BRANCH=${GIT_BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")}
GIT_COMMIT=${GIT_COMMIT:-$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")}
GIT_COMMIT_DATE=${GIT_COMMIT_DATE:-$(git log -1 --format="%ad" --date="format:%Y%m%d%H%M" "${GIT_BRANCH}" 2>/dev/null || echo "unknown")}
BRANCH_INFO=${BRANCH_INFO:-${GIT_BRANCH}:${GIT_COMMIT}:${GIT_COMMIT_DATE}}

echo "export BRANCH_INFO=${BRANCH_INFO}" > ${RESULT_FILE}
echo "export GENERATED_AT=\"$(date)\"" >> ${RESULT_FILE}
