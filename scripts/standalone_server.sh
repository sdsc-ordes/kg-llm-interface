# Local SPARQL+Chroma configs
TEST_ENV="tests/.test.env"
# Download RDF file
set -o allexport && source ${TEST_ENV} && set +o allexport
# Embed in Chroma
python aikg/flows/chroma_build.py --graph https://example.org/ontology
# Run server
uvicorn "aikg.server:app" --env-file "${TEST_ENV}" --port 8001