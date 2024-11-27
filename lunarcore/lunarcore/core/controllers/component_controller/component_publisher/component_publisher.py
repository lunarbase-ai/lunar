# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from lunarcore.utils.config_generator import ComponentSetupGenerator


class PublisherService:

    def create_pull_request(
            self,
            component_name: str,
            new_branch_name: str,
            component_class: str,
            setup_file: Optional[str],
            component_documentation: Optional[str]
    ):
        raise NotImplementedError()


class ComponentPublisher:
    def __init__(self, publisher: PublisherService):
        self.publisher = publisher

    def publish_component(
            self,
            author: str,
            author_email: str,
            component_name: str,
            component_description: str,
            component_class: str,
            component_documentation: str,
            version: str
    ):
        #TODO: Validate

        setup_file_content = f"""from setuptools import find_packages, setup

AUTHOR = "{author}"
AUTHOR_EMAIL = "{author_email}"
"""

        setup_file_content = setup_file_content + """
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
            "package_dir":{"": "src"},
            "install_requires": self._load_requirements(),
            "tests_require": TEST_REQUIREMENTS,
            "extras_require": EXTRAS_REQUIREMENTS,
            "author": AUTHOR,
            "author_email": AUTHOR_EMAIL,
            "description": self.description,
            "license": LICENSE,
        }

    def _load_requirements(self):
        with open(REQUIREMENTS_FILE_PATH, 'r') as file:
            lines = file.read().splitlines()
            return [line for line in lines if line and not line.startswith('#')]

        """
        setup_file_content = setup_file_content + f"""
setup_generator = ComponentSetupGenerator(
    name="{component_name}",
    version="{version}",
    description="{component_description}"
)

setup(**setup_generator.generate())

"""

        self.publisher.create_pull_request(
            component_name=component_name,
            new_branch_name=f"component-submission/{component_name.replace(' ','_').lower()}",
            component_class=component_class,
            setup_file=setup_file_content,
            component_documentation=component_documentation
        )
