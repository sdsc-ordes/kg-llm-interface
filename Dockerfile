# Dockerfile for the fastAPI chatbot server
# It is based on the official python image and uses poetry to setup the environment

FROM python:3.10-slim-bullseye

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get -y install python3-dev

# Install poetry
RUN pip install poetry

# Copy the source code into docker image
COPY . /app

# Install project and dependencies
RUN poetry install --no-interaction --no-ansi -vvv

# Run the server
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
