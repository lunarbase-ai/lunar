# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later


class ComponentError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class LLMResponseError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class ServerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ConfigFileIsMissing(ServerError):
    def __init__(self, config_file=None):
        if config_file is None:
            message = "A config file is missing"
        else:
            message = f"The config file at {config_file} is missing"
        super().__init__(message)
