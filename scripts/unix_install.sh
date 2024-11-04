#!/usr/bin/env bash

## Variables

SCRIPT=$(realpath "$0")
SCRIPTS_ROOT=$(dirname "${SCRIPT}")
LUNAR_ROOT=$(dirname "${SCRIPTS_ROOT}")
LUNAR_SCRIPTS_DIR="scripts"
LUNARCORE_NAME="lunarcore"
LUNARFLOW_NAME="lunarflow"
LUNARCORE_INSTALLATION_SCRIPT_NAME="lunarcore_unix_install.sh"
LUNARFLOW_INSTALLATION_SCRIPT_NAME="lunarflow_unix_install.sh"
LUNARCORE_INSTALLATION_SCRIPT_PATH="${LUNAR_ROOT}/${LUNARCORE_NAME}/${LUNAR_SCRIPTS_DIR}/${LUNARCORE_INSTALLATION_SCRIPT_NAME}"
LUNARFLOW_INSTALLATION_SCRIPT_PATH="${LUNAR_ROOT}/${LUNARFLOW_NAME}/${LUNAR_SCRIPTS_DIR}/${LUNARFLOW_INSTALLATION_SCRIPT_NAME}"

## Lunarcore installation
cd "${LUNAR_ROOT}"
/bin/sh "${LUNARCORE_INSTALLATION_SCRIPT_PATH}"
if [ $? -ne 0 ]; then
  printf "Failed to install %s !\n" "${LUNARCORE_NAME}"
  exit 1
fi

## Lunarflow installation
cd "${LUNAR_ROOT}"
/bin/sh "${LUNARFLOW_INSTALLATION_SCRIPT_PATH}"
if [ $? -ne 0 ]; then
  printf "Failed to install %s See above.\n" "${LUNARFLOW_NAME}"
  exit 1
fi

printf "Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>"