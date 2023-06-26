# Dockerfile for the fastAPI chatbot server
# It is based on the official python image and uses poetry to setup the environment

FROM python:3.10-slim-bullseye

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get -y install python3-dev g++-11 build-essential libopenblas-base libopenmpi-dev unzip

# Install poetry
RUN pip install 'poetry==1.5.0' pytest tqdm pydantic chromadb llama_index prefect prefect_dask rdflib SPARQLWrapper
#RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy the source code into docker image
COPY . /app

# Install project and dependencies
RUN rm -f poetry.lock && poetry install --no-interaction -vvv

# Run the server
ENTRYPOINT ["/bin/bash", "-c", "poetry run uvicorn aikg.server:app --host 0.0.0.0 --port 80"]
