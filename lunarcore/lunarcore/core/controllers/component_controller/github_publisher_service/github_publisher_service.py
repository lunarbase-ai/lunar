# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from github import Github, Auth

from lunarcore.core.controllers.component_controller.component_publisher.component_publisher import \
    PublisherService


class GithubPublisherService(PublisherService):

    def __init__(self, access_token: str):
        auth = Auth.Token(access_token)
        self.github = Github(auth=auth)

    def create_pull_request(
            self,
            component_name: str,
            new_branch_name: str,
            component_class: str,
            component_documentation: Optional[str]
    ):
        repo_path = "lunarbase-ai/lunarverse"

        repo = self.github.get_repo(repo_path)
        # TODO: get from config
        source_branch_name = "development"
        source_branch = repo.get_branch(source_branch_name)
        repo.create_git_ref(f"refs/heads/{new_branch_name}", sha=source_branch.commit.sha)
        component_base_path = component_name.replace(" ", "_").lower()
        repo.create_file(
            f"{component_base_path}/__init__.py",
            component_name,
            component_class,
            branch=new_branch_name
        )
        if component_documentation:
            repo.create_file(
                f"{component_base_path}/README.md",
                f"{component_name} documentation",
                component_documentation,
                branch=new_branch_name
            )
        repo.create_pull(source_branch_name, new_branch_name, title=new_branch_name)

