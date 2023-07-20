# Dockerfile for the fastAPI chatbot server
# It uses poetry to setup the environment
FROM nvidia/cuda:11.7.1-base-ubuntu22.04

# Set the working directory
WORKDIR /app

# Install system dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install \
    git \
    python3-dev \
    g++-11 \
    build-essential \
    curl wget tzdata

# Install poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.5.0
ENV PATH="$PATH:$POETRY_HOME/bin"
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy the source code into docker image
COPY . /app

# Install project and dependencies
RUN rm -f poetry.lock && make install
RUN poetry run python -m ipykernel install --user --name aikg

# Run the server
ENTRYPOINT ["/bin/bash", "-c", "poetry run uvicorn aikg.server:app --host 0.0.0.0 --port 80"]
