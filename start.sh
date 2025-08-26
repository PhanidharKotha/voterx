#!/bin/bash
if [ ! -d "./frontend/build" ]; then
  echo "❌ Frontend build folder missing. Run 'npm run build' first."
  exit 1
fi