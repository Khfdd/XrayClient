#!/usr/bin/env bash
# Made by Luna 6

set -e

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

"${PROJECT_DIR}/.venv/bin/python" "${PROJECT_DIR}/src/main.py"
systemctl restart xray
