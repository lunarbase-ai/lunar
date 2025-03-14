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
WORKDIR /app/base

# Copy lunar
COPY . /app

# Install Python dependencies using Poetry
RUN poetry install

# Install the current package with Poetry
RUN poetry install --only-root

RUN cp /app/\[EXAMPLE\]components.txt /app/components.txt

RUN printf 'LUNAR_STORAGE_TYPE="LOCAL"\n \
LUNAR_STORAGE_BASE_PATH="/app/lunar_data"\n \
LUNARCORE_ADDRESS="0.0.0.0"\n \
LUNARCORE_PORT=8088\n \
DEFAULT_USER_PROFILE=admin\n \
PERSISTENT_REGISTRY_STARTUP_FILE="/app/components.txt"' > /app/.env

# Flag to tell the app that we are in docker
RUN touch /app/in_docker

# Expose the required port
EXPOSE 8088

# Set the entrypoint to the application
CMD [ "poetry", "run", "lunarbase", "start" ]
#CMD ["sh", "-c", "tail -f /dev/null"]