#!/usr/bin/env bash
# Claude cloud environment init: report available resources.
set -euo pipefail
set -x
trap 'echo "init_vm.sh failed at line ${LINENO}: ${BASH_COMMAND}" >&2' ERR

pwd
python3 --version || true
cat .python-version || true

if ! command -v uv >/dev/null; then
    # --break-system-packages: Debian/Ubuntu pip refuses installs otherwise (PEP 668)
    pip install --break-system-packages uv || python3 -m pip install --break-system-packages uv
fi
uv --version

uv sync --dev
uv run pre-commit install

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
