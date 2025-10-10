#!/usr/bin/env bash
set -euo pipefail

poetry run python -m apps.etl.pipeline "$@"
