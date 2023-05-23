# Dockerfile for the fastAPI chatbot server
# It is based on the official python image and uses poetry to setup the environment

FROM python:3.10-slim-bullseye

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get -y install python3-dev g++-11 build-essential libopenblas-base libopenmpi-dev

# Install poetry
RUN pip install poetry
# RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy the source code into docker image
COPY . /app

# Install project and dependencies
RUN rm -f poetry.lock && poetry install --no-interaction -vvv

# Run the server
CMD ["poetry", "run", "uvicorn", "aikg.server:app", "--host", "0.0.0.0", "--port", "80"]
