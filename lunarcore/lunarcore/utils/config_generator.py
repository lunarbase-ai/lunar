from setuptools import find_packages, setup
import os

AUTHOR = "Lunarbase (https://lunarbase.ai/)"
AUTHOR_EMAIL = "contact@lunarbase.ai"
LICENSE = "SPDX-License-Identifier: GPL-3.0-or-later"
TEST_REQUIREMENTS = [
    'pytest'
]
EXTRAS_REQUIREMENTS = {
    'dev': [
        'pytest',
    ],
}

REQUIREMENTS_FILE_PATH = 'requirements.txt'

LUNARCORE_PACKAGE = "lunarcore @ git+https://github.com/lunarbase-ai/lunar.git@lunarbase#subdirectory=lunarbase/core"


class ComponentSetupGenerator:
    def __init__(self, name, version, description, requirements):
        self.name = name
        self.version = version
        self.description = description
        self.requirements = requirements

    def generate_arguments(self):
        return {
            "name": self.name,
            "version": self.version,
            # "packages":find_packages(where="src"),
            # "package_dir":{"": "src"},
            "install_requires": self.requirements,
            "tests_require": TEST_REQUIREMENTS,
            "extras_require": EXTRAS_REQUIREMENTS,
            "author": AUTHOR,
            "author_email": AUTHOR_EMAIL,
            "description": self.description,
            "license": LICENSE,
        }

    def generate_setup_file_content(self):
        arguments = self.generate_arguments()
        setup_file_string = f"from setuptools import setup\n\n"
        setup_file_string = setup_file_string + f"setup(\n"
        for key, value in arguments.items():
            setup_file_string = setup_file_string + f"    {key}={repr(value)},\n"
        setup_file_string = setup_file_string + f")\n"
        return setup_file_string
