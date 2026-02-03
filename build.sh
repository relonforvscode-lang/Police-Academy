#!/bin/bash
# Wrapper build script at repository root for Render compatibility.
# Render attempted to run `bash build.sh`; this forwards to build/build.sh.
set -e

if [ -f "build/build.sh" ]; then
  echo "Found build/build.sh — executing it."
  bash build/build.sh
else
  echo "Error: build/build.sh not found."
  exit 1
fi
