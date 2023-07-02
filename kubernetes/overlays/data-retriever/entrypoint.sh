cd /app
curl -u admin:admin -X POST http://${SPARQL_HOST}:${SPARQL_PORT}/rest/repositories -H 'Content-Type: multipart/form-data' -F "config=@kubernetes/overlays/data-retriever/repository_config.ttl"
cat kubernetes/overlays/data-retriever/entrypoint.sh
make test
