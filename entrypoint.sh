#!/bin/bash

case "$1" in
  receiver)
    echo "Loading env variables..."
    source .env
    echo "Starting microservice receiver..."
    echo "Starting python..."
    python -u receiver.py
    ;;
  producer)
    echo "Loading env variables..."
    source .env
    echo "Starting producer..."
    python -u main.py
    ;;
  *)
    echo "Error: Unknown command '$1'."
    exit 1
    ;;
esac
