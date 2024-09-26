#!/usr/bin/env bash

## Variables

SCRIPT=$(realpath "${BASH_SOURCE[0]}")
SCRIPTS_ROOT=$(dirname "${SCRIPT}")
LUNAR_ROOT=$(dirname "${SCRIPTS_ROOT}")
LUNARCORE_NAME="lunarcore"
LUNARCORE_ROOT="${LUNAR_ROOT}/${LUNARCORE_NAME}"
LUNARCORE_ENV_NAME=".env"
LUNARCORE_EXAMPLE_ENV_NAME="[EXAMPLE].env"
LUNARCORE_ENV_PATH="${LUNARCORE_ROOT}/${LUNARCORE_ENV_NAME}"
LUNARCORE_EXAMPLE_ENV_PATH="${LUNARCORE_ROOT}/${LUNARCORE_EXAMPLE_ENV_NAME}"

## Lunarcore installation
printf "Installing %s ...\n" "${LUNARCORE_NAME}"

command -v python3 >/dev/null 2>&1
if [ $? -ne 0 ]; then
  printf "Checking for Python: Python 3.8+ is not installed and required! Exiting ...\n"
  exit 1
else
  printf "Checking for Python: Python 3 is installed.\n"
fi

command -v poetry >/dev/null 2>&1
if [ $? -ne 0 ]; then
  printf "Installing poetry ...\n"
  command -v pipx >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    printf "Installing pipx (required by poetry) ...\n"
    python3 -m pip install --user pipx && python3 -m pipx ensurepath
  fi
  pipx install poetry
fi

cd "${LUNARCORE_ROOT}"
if [ ! -f "${LUNARCORE_ENV_PATH}" ]; then
  cp "${LUNARCORE_EXAMPLE_ENV_PATH}" "${LUNARCORE_ENV_PATH}"
fi

if [ $? -ne 0 ]; then
  printf "Failed to create %s file for %s! See above.\n" "${LUNARCORE_ENV_NAME}" "${LUNARCORE_NAME}"
  exit 1
fi

poetry lock --no-update && poetry install
if [ $? -eq 0 ]; then
  printf "Successfully installed %s!\n" "${LUNARCORE_NAME}"
fi
cd -

printf "%s: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>" "${LUNARCORE_NAME}"