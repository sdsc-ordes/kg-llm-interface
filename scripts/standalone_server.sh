#!/usr/bin/env bash
# This script starts the server with a local Chroma instance and using
# an RDF file as knowledge graph.

# Local SPARQL+Chroma configs
export SPARQL_ENDPOINT="data/test_data.trig"
export CHROMA_HOST="local"
export CHROMA_MODEL="all-MiniLM-L6-v2"
export CHROMA_PERSIST_DIR="/tmp/chroma-test"
export CHAT_CONFIG="tests/chat.test.yml"

# Embed in Chroma
python aikg/flows/chroma_build.py --graph https://example.org/ontology
# Run server
uvicorn "aikg.server:app" --port 8001
