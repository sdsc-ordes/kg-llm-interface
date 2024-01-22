#!/bin/bash
set -e

cd /app
curl -v -u admin:admin -X POST http://${SPARQL_HOST}:${SPARQL_PORT}/rest/repositories -H 'Content-Type: multipart/form-data' -F "config=@kubernetes/overlays/data-retriever/repository_config.ttl"
export SPARQL_ENDPOINT=http://${SPARQL_HOST}:${SPARQL_PORT}/repositories/test
mkdir temp
cd temp
wget https://www.pokemonkg.org/ontology/ontology.nt
wget https://www.pokemonkg.org/download/dump/poke-a.nq.gz
gzip -d poke-a.nq.gz
head -n 1000 poke-a.nq > poke-a-c.nq
cd ..
poetry run python3 aikg/flows/insert_triples.py /app/temp/ontology.nt
poetry run python3 aikg/flows/insert_triples.py /app/temp/poke-a-c.nq
poetry run python3 aikg/flows/chroma_build.py

