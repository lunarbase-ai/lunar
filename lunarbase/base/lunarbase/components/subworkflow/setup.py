#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from setuptools import find_packages, setup

AUTHOR = "Lunarbase (https://lunarbase.ai/)"
AUTHOR_EMAIL = "contact@lunarbase.ai"
LICENSE = "SPDX-License-Identifier: GPL-3.0-or-later"

class ComponentSetupGenerator:
    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description

    def generate(self):
        return {
            "name": self.name,
            "version": self.version,
            "packages":find_packages(where="src"),
            "install_requires": [],
            "tests_require": [],
            "extras_require": {},
            "author": AUTHOR,
            "author_email": AUTHOR_EMAIL,
            "description": self.description,
            "license": LICENSE,
        }

setup_generator = ComponentSetupGenerator(
    name="subworkflow",
    version="0.1",
    description="Performs Subworkflow execution"
)

setup(**setup_generator.generate())