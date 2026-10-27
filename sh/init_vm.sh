#!/usr/bin/env bash
# Claude cloud environment init: report available resources.
set -euo pipefail

pip install uv && uv sync --dev

if [[ -r /proc/meminfo ]]; then
    ram_gb=$(awk '/^MemTotal:/ {printf "%.1f", $2 / 1024 / 1024}' /proc/meminfo)
    cpus=$(nproc)
else
    # macOS fallback for local testing
    ram_gb=$(sysctl -n hw.memsize | awk '{printf "%.1f", $1 / 1024 / 1024 / 1024}')
    cpus=$(sysctl -n hw.ncpu)
fi

echo "RAM: ${ram_gb} GB"
echo "CPUs: ${cpus}"
