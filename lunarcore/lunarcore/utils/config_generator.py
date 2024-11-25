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
    def __init__(self, name, version, description, package_dir):
        self.name = name
        self.version = version
        self.description = description
        self.package_dir = package_dir

    def generate_arguments(self):
        return {
            "name": self.name,
            "version": self.version,
            # "packages":find_packages(where="src"),
            # "package_dir":{"": "src"},
            "install_requires": self._load_requirements(os.path.join(self.package_dir, REQUIREMENTS_FILE_PATH)),
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

        with open(os.path.join(self.package_dir, 'setup.py'), 'w') as file:
            file.write(f"from setuptools import setup\n")
            file.write("\n")
            file.write(f"setup(\n")
            for key, value in arguments.items():
                file.write(f"    {key}={repr(value)},\n")
            file.write(f")\n")
    def generate_setup_file(self):
        file_content = self.generate_setup_file_content()
        
        arguments = self.generate_arguments()
        with open(os.path.join(self.package_dir, 'setup.py'), 'w') as file:
            file.write(f"from setuptools import setup\n")
            file.write("\n")
            file.write(f"setup(\n")
            for key, value in arguments.items():
                file.write(f"    {key}={repr(value)},\n")
            file.write(f")\n")

    def _load_requirements(self, requirements_path=REQUIREMENTS_FILE_PATH):
        requirements = []
        if os.path.isfile(requirements_path):
            with open(requirements_path, 'r') as file:
                lines = file.read().splitlines()
                requirements.extend(line for line in lines if line and not line.startswith('#'))

        if LUNARCORE_PACKAGE not in requirements:
            requirements.append(LUNARCORE_PACKAGE)

        return requirements
