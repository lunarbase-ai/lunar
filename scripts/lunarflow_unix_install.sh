#!/usr/bin/env bash

## Variables

SCRIPT=$(realpath "${BASH_SOURCE[0]}")
SCRIPTS_ROOT=$(dirname "${SCRIPT}")
LUNAR_ROOT=$(dirname "${SCRIPTS_ROOT}")
LUNARFLOW_NAME="lunarflow"
LUNARFLOW_ROOT="${LUNAR_ROOT}/${LUNARFLOW_NAME}"
LUNARFLOW_ENV_NAME=".env"
LUNARFLOW_EXAMPLE_ENV_NAME="[EXAMPLE].env"
LUNARFLOW_ENV_PATH="${LUNARFLOW_ROOT}/${LUNARFLOW_ENV_NAME}"
LUNARFLOW_EXAMPLE_ENV_PATH="${LUNARFLOW_ROOT}/${LUNARFLOW_EXAMPLE_ENV_NAME}"

## Lunarflow installation
printf "Installing %s ..." "${LUNARFLOW_NAME}"

command -v node >/dev/null 2>&1
if [ $? -ne 0 ]; then
  printf "Checking for node.js: node.js v18.20 is not installed and required! Exiting ..."
  exit 1
else
  printf "Checking for node.js: node.js is installed. "
fi
command -v yarn >/dev/null 2>&1
if [ $? -ne 0 ]; then
  printf "Installing yarn (required by %s) ..." "${LUNARFLOW_NAME}"
  npm install yarn && npm install sharp
fi

cd "${LUNARFLOW_ROOT}"
if [ ! -f "${LUNARFLOW_ENV_PATH}" ]; then
  cp "${LUNARFLOW_EXAMPLE_ENV_PATH}" "${LUNARFLOW_ENV_PATH}"
fi

if [ $? -ne 0 ]; then
  printf "Failed to create %s file for %s! See above." "${LUNARFLOW_ENV_NAME}" "${LUNARFLOW_NAME}"
  exit 1
fi

yarn && yarn build
if [ $? -eq 0 ]; then
  print "Successfully installed %s!" "${LUNARFLOW_NAME}"
fi
cd -

printf "%s: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>" "${LUNARFLOW_NAME}"