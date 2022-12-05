# Copyright (C) 2022 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This script creates a new repository with default settings
"""

import shutil
from argparse import ArgumentParser, Namespace
from typing import Union

from pontos.git import Git, MergeStrategy
from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.api.repositories import GitIgnoreTemplate, LicenseType
from pontos.github.models.base import Permission
from pontos.testing import temp_directory

TEMPLATES = {
    "python": "https://github.com/greenbone/python-project-template.git",
    "go": "https://github.com/greenbone/go-project-template.git",
}

GITIGNORE = {"python": GitIgnoreTemplate.PYTHON, "go": GitIgnoreTemplate.GO}


def license_type(value: Union[str, LicenseType]) -> LicenseType:
    if isinstance(value, LicenseType):
        return value

    return LicenseType(value.lower())


def possible_license_types() -> str:
    return ", ".join(
        [
            LicenseType.GNU_GENERAL_PUBLIC_LICENSE_2_0.value,
            LicenseType.GNU_GENERAL_PUBLIC_LICENSE_3_0.value,
            LicenseType.GNU_AFFERO_GENERAL_PUBLIC_LICENSE_3_0.value,
        ]
    )


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--template",
        choices=("python", "go"),
        help="Use template repo as base for the new repository.",
    )
    parser.add_argument(
        "--team",
        help="Team that should have admin access to the repository.",
    )
    parser.add_argument(
        "--license",
        help=f"License to choose for the repo: {possible_license_types()}. "
        "Default: %(default)s.",
        type=license_type,
        default=LicenseType.GNU_AFFERO_GENERAL_PUBLIC_LICENSE_3_0.value,
    )
    parser.add_argument(
        "--visibility",
        choices=("public", "private"),
        default="private",
        help="Visibility of the repository. Default: %(default)s.",
    )
    parser.add_argument("--description", help="Description of the repository.")
    parser.add_argument("name", help="Repository to create.")
    parser.add_argument(
        "organization",
        nargs="?",
        default="greenbone",
        help="Organization to create the repo in. Default: %(default)s.",
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    organization = args.organization
    repository = args.name

    team_id = None
    if args.team:
        team = await api.teams.get(organization, args.team)
        team_id = team.id

    with temp_directory() as temp_dir:
        git = Git()

        if args.template:
            git.clone(TEMPLATES[args.template], temp_dir, remote="template")
            dot_git_dir = temp_dir / ".git"
            shutil.rmtree(dot_git_dir)

            git.cwd = temp_dir
            git.init()
            git.add(".")
            git.commit(f"Starting commit from {args.template} template")
        else:
            git.cwd = temp_dir
            git.init()

        private = True if args.visibility == "private" else False

        repo = await api.repositories.create(
            organization,
            repository,
            private=private,
            has_projects=False,
            has_wiki=False,
            allow_merge_commit=True,
            allow_auto_merge=True,
            allow_rebase_merge=True,
            allow_squash_merge=True,
            allow_update_branch=True,
            delete_branch_on_merge=True,
            is_template=False,
            license_template=args.license,
            description=args.description,
            auto_init=True,
            gitignore_template=GITIGNORE.get(args.template),
            team_id=team_id,
        )

        repo_url = repo.ssh_url

        git.add_remote("upstream", repo_url)
        git.fetch("upstream")

        if args.template:
            git.rebase("upstream/main", strategy=MergeStrategy.ORT_OURS)
        else:
            git.checkout("main", start_point="upstream/main")

        if args.team:
            await api.teams.update_permission(
                organization, team.slug, repository, Permission.ADMIN
            )

            code_owners_file = temp_dir / ".github" / "CODEOWNERS"
            code_owners_file.write_text(
                f"# default reviewers\n*\t@{organization}/{team.slug}\n"
            )
            git.add(code_owners_file)
            git.commit("Adjust CODEOWNERS file")

        git.push(remote="upstream", force=True)

        await api.branches.update_protection_rules(
            f"{organization}/{repository}",
            "main",
            require_branches_to_be_up_to_date=True,
            require_code_owner_reviews=True,
            required_approving_review_count=1,
            required_conversation_resolution=True,
            dismiss_stale_reviews=True,
            allow_force_pushes=False,
            allow_deletions=False,
            restrictions_users=[],
        )
