#!/bin/bash
set -e
set -x

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    if [ -f ".venv/bin/activate" ]; then
        # shellcheck disable=SC1091
        source .venv/bin/activate
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
    fi
fi
