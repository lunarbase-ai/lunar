# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

FROM python:3.10

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
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . /app

# Install the current package with Poetry (optional, for cases where the project itself is a package)
RUN poetry install --no-dev

# Flag to tell the app that we are in docker
RUN touch /app/in_docker

# Expose the required port
EXPOSE 8088

# Set the entrypoint to the application
CMD [ "lunarcore", "start"]
