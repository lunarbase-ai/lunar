# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

FROM python:3.9

# Install Poetry
ENV POETRY_VERSION=1.7.0

# Install dependencies required for Poetry and ensure no virtualenvs are created
RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false

# Set working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml /app/

# Install Python dependencies using Poetry
RUN poetry install --no-root --only main

# Copy the rest of the application code
COPY . /app

# Install the current package with Poetry (optional, for cases where the project itself is a package)
RUN poetry install --only main

RUN cp /app/\[ALL\]components.json /app/components.json

RUN printf 'LUNAR_STORAGE_TYPE="LOCAL"\n \
LUNAR_STORAGE_BASE_PATH="/app/lunar_data"\n \
LUNARCORE_ADDRESS="0.0.0.0"\n \
LUNARCORE_PORT=8088\n \
DEFAULT_USER_PROFILE=admin\n \
PERSISTENT_REGISTRY_STARTUP_FILE="/app/components.json"' > /app/.env

# Flag to tell the app that we are in docker
RUN touch /app/in_docker

# Expose the required port
EXPOSE 8088

# Set the entrypoint to the application
CMD [ "poetry", "run", "lunarcore", "start" ]
