#!/usr/bin/env bash

## Variables

SCRIPTS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LUNARFLOW_ROOT=$(dirname "${SCRIPTS_ROOT}")
LUNAR_ROOT=$(dirname "${LUNARFLOW_ROOT}")
LUNARFLOW_NAME="lunarflow"
LUNARFLOW_ENV_NAME="../.env"
LUNARFLOW_EXAMPLE_ENV_NAME="../[EXAMPLE].env"
LUNARFLOW_ENV_PATH="${LUNARFLOW_ROOT}/${LUNARFLOW_ENV_NAME}"
LUNARFLOW_EXAMPLE_ENV_PATH="${LUNARFLOW_ROOT}/${LUNARFLOW_EXAMPLE_ENV_NAME}"

OS=$(uname)
if grep -qEi "(Microsoft|WSL)" /proc/sys/kernel/osrelease &> /dev/null ; then
    OS="Windows (WSL)"
fi


check_node_install() {
  command -v node >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    printf "Checking for node.js: node.js v18.20 is not installed and required! Exiting ..."
    exit 1
  else
    printf "Checking for node.js: node.js is installed. "
  fi
}

check_yarn_install() {
    command -v yarn >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        printf "Installing yarn (required by %s) ..." "${LUNARFLOW_NAME}"
        export NODE_OPTIONS="--dns-result-order=ipv4first"
        npm install yarn && npm install sharp
    fi
}


create_env_file() {
  if [ ! -f "${LUNARFLOW_ENV_PATH}" ]; then
    cp "${LUNARFLOW_EXAMPLE_ENV_PATH}" "${LUNARFLOW_ENV_PATH}"
  fi

  if [ $? -ne 0 ]; then
    printf "Failed to create %s file for %s! See above." "${LUNARFLOW_ENV_NAME}" "${LUNARFLOW_NAME}"
    exit 1
  fi
}

adapt_lunarverse_address_on_windows() {
    if [ "$OS" = "Windows (WSL)" ]; then
        sed -i 's|^NEXT_PUBLIC_LUNARVERSE_ADDRESS=.*|NEXT_PUBLIC_LUNARVERSE_ADDRESS=http://localhost:8088|' "${LUNARFLOW_ENV_PATH}"
        
        if [ $? -ne 0 ]; then
            printf "Failed to update NEXT_PUBLIC_LUNARVERSE_ADDRESS in %s! See above." "${LUNARFLOW_ENV_PATH}"
            exit 1
        fi
    fi
}

install_dependencies_and_build() {
    yarn && yarn build
    if [ $? -eq 0 ]; then
        printf "Successfully installed %s!" "${LUNARFLOW_NAME}"
    fi
}

printf "Installing %s ..." "${LUNARFLOW_NAME}"
cd "${LUNARFLOW_ROOT}"

check_node_install
check_yarn_install
create_env_file
adapt_lunarverse_address_on_windows
install_dependencies_and_build

cd -

printf "%s: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>" "${LUNARFLOW_NAME}"