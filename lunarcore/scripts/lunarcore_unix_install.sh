#!/usr/bin/env bash

## Variables
SCRIPTS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LUNARCORE_ROOT=$(dirname "${SCRIPTS_ROOT}")
LUNAR_ROOT=$(dirname "${LUNARCORE_ROOT}")

LUNARCORE_NAME="lunarcore"
LUNARCORE_ENV_NAME=".env"
LUNARCORE_EXAMPLE_ENV_NAME="[EXAMPLE].env"
LUNARCORE_ENV_PATH="${LUNAR_ROOT}/${LUNARCORE_ENV_NAME}"
LUNARCORE_EXAMPLE_ENV_PATH="${LUNAR_ROOT}/${LUNARCORE_EXAMPLE_ENV_NAME}"

EXAMPLE_PERSISTENT_REGISTRY_STARTUP_FILE="${LUNARCORE_ROOT}/[ALL]components.json"
DEFAULT_PERSISTENT_REGISTRY_STARTUP_FILE="${LUNARCORE_ROOT}/components2.json"

# Lunarcore installation
printf "Installing %s ...\n" "${LUNARCORE_NAME}"
cd "${LUNARCORE_ROOT}"


# Check for Python 3.8+
command -v python3 >/dev/null 2>&1
if [ $? -ne 0 ]; then
  printf "Checking for Python: Python 3.8+ is not installed and required! Exiting ...\n"
  exit 1
else
  printf "Checking for Python: Python 3 is installed.\n"
fi

# Check for pipx and poetry
command -v poetry >/dev/null 2>&1
if [ $? -ne 0 ]; then
  printf "Installing poetry ...\n"
  command -v pipx >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    printf "Installing pipx (required by poetry) ...\n"
    python3 -m pip install --user pipx
  fi
  python3 -m pipx ensurepath
  python3 -m pipx install poetry
fi

# Create .env from example file if it doesn't exist
if [ ! -f "${LUNARCORE_ENV_PATH}" ]; then
  cp "${LUNARCORE_EXAMPLE_ENV_PATH}" "${LUNARCORE_ENV_PATH}"
fi

if [ $? -ne 0 ]; then
  printf "Failed to create %s file for %s! See above.\n" "${LUNARCORE_ENV_NAME}" "${LUNARCORE_NAME}"
  exit 1
fi

# Create default persistent registry startup file if it doesn't exist
if [ ! -f "$DEFAULT_PERSISTENT_REGISTRY_STARTUP_FILE" ]; then
    cp "$EXAMPLE_PERSISTENT_REGISTRY_STARTUP_FILE" "$DEFAULT_PERSISTENT_REGISTRY_STARTUP_FILE"
    echo "Created $DEFAULT_PERSISTENT_REGISTRY_STARTUP_FILE from $EXAMPLE_PERSISTENT_REGISTRY_STARTUP_FILE"
else
    echo "$DEFAULT_PERSISTENT_REGISTRY_STARTUP_FILE already exists"
fi

# Register PERSISTENT_REGISTRY_STARTUP_FILE in .env
if grep -q "^PERSISTENT_REGISTRY_STARTUP_FILE=" "${LUNARCORE_ENV_PATH}"; then
  sed -i "s|^PERSISTENT_REGISTRY_STARTUP_FILE=.*|PERSISTENT_REGISTRY_STARTUP_FILE=\"${DEFAULT_PERSISTENT_REGISTRY_STARTUP_FILE}\"|" "${LUNARCORE_ENV_PATH}"
else
  echo -e "\nPERSISTENT_REGISTRY_STARTUP_FILE=\"${DEFAULT_PERSISTENT_REGISTRY_STARTUP_FILE}\"" >> "${LUNARCORE_ENV_PATH}"
fi

# Install dependencies with poetry
poetry lock --no-update && poetry install --only main
if [ $? -eq 0 ]; then
  printf "Successfully installed %s!\n" "${LUNARCORE_NAME}"
fi
cd -

printf "%s: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>" "${LUNARCORE_NAME}"