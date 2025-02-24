#!/bin/sh

echo "Starting the wrapper script..."
echo "Starting unicorn server..."
# https://www.uvicorn.org/settings/
uvicorn "app:app" --host=0.0.0.0 --port=8000
# uvicorn "app:app" --host=0.0.0.0 --port=8000 --log-level warning
