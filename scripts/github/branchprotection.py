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

from argparse import ArgumentParser, Namespace
from typing import Any, Dict, Iterable, Optional, Tuple

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.models import BranchProtection


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("repo")
    parser.add_argument("branch")


def update_from_applied_settings(
    branch_protection: BranchProtection,
    required_status_checks: Optional[Iterable[Tuple[str, str]]] = None,
    require_branches_to_be_up_to_date: Optional[bool] = None,
    enforce_admins: Optional[bool] = None,
    dismissal_restrictions_users: Optional[Iterable[str]] = None,
    dismissal_restrictions_teams: Optional[Iterable[str]] = None,
    dismissal_restrictions_apps: Optional[Iterable[str]] = None,
    dismiss_stale_reviews: Optional[bool] = None,
    require_code_owner_reviews: Optional[bool] = None,
    required_approving_review_count: Optional[int] = None,
    require_last_push_approval: Optional[bool] = None,
    bypass_pull_request_allowances_users: Optional[Iterable[str]] = None,
    bypass_pull_request_allowances_teams: Optional[Iterable[str]] = None,
    bypass_pull_request_allowances_apps: Optional[Iterable[str]] = None,
    restrictions_users: Optional[Iterable[str]] = None,
    restrictions_teams: Optional[Iterable[str]] = None,
    restrictions_apps: Optional[Iterable[str]] = None,
    required_linear_history: Optional[bool] = None,
    allow_force_pushes: Optional[bool] = None,
    allow_deletions: Optional[bool] = None,
    block_creations: Optional[bool] = None,
    required_conversation_resolution: Optional[bool] = None,
    lock_branch: Optional[bool] = None,
    allow_fork_syncing: Optional[bool] = None,
    required_signatures: Optional[bool] = None,
) -> Dict[str, Any]:
    kwargs = {}
    if enforce_admins is not None:
        kwargs["enforce_admins"] = enforce_admins
    elif branch_protection.enforce_admins:
        kwargs["enforce_admins"] = branch_protection.enforce_admins.enabled
    else:
        kwargs["enforce_admins"] = None

    if required_linear_history is not None:
        kwargs["required_linear_history"] = required_linear_history
    elif branch_protection.required_linear_history:
        kwargs[
            "required_linear_history"
        ] = branch_protection.required_linear_history.enabled
    else:
        kwargs["required_linear_history"] = None

    if allow_force_pushes is not None:
        kwargs["allow_force_pushes"] = allow_force_pushes
    elif branch_protection.allow_force_pushes:
        kwargs[
            "allow_force_pushes"
        ] = branch_protection.allow_force_pushes.enabled
    else:
        kwargs["allow_force_pushes"] = None

    if allow_deletions is not None:
        kwargs["allow_deletions"] = allow_deletions
    elif branch_protection.allow_deletions:
        kwargs["allow_deletions"] = branch_protection.allow_deletions.enabled
    else:
        kwargs["allow_deletions"] = None

    if required_conversation_resolution is not None:
        kwargs[
            "required_conversation_resolution"
        ] = required_conversation_resolution
    elif branch_protection.required_conversation_resolution:
        kwargs[
            "required_conversation_resolution"
        ] = branch_protection.required_conversation_resolution.enabled
    else:
        kwargs["required_conversation_resolution"] = None

    if block_creations is not None:
        kwargs["block_creations"] = block_creations
    elif branch_protection.block_creations:
        kwargs["block_creations"] = branch_protection.block_creations.enabled
    else:
        kwargs["block_creations"] = None

    if lock_branch is not None:
        kwargs["lock_branch"] = lock_branch
    elif branch_protection.lock_branch:
        kwargs["lock_branch"] = branch_protection.lock_branch.enabled
    else:
        kwargs["lock_branch"] = None

    if allow_fork_syncing is not None:
        kwargs["allow_fork_syncing"] = allow_fork_syncing
    elif branch_protection.allow_fork_syncing:
        kwargs[
            "allow_fork_syncing"
        ] = branch_protection.allow_fork_syncing.enabled
    else:
        kwargs["allow_fork_syncing"] = None
    if required_signatures is not None:
        kwargs["required_signatures"] = required_signatures
    elif branch_protection.required_signatures:
        kwargs[
            "required_signatures"
        ] = branch_protection.required_signatures.enabled
    else:
        kwargs["required_signatures"] = None

    existing_required_status_checks = branch_protection.required_status_checks
    if existing_required_status_checks:
        kwargs[
            "require_branches_to_be_up_to_date"
        ] = existing_required_status_checks.strict
        if existing_required_status_checks.checks is not None:
            kwargs["required_status_checks"] = [
                (c.context, c.app_id)
                for c in existing_required_status_checks.checks
            ]
    if required_status_checks is not None:
        kwargs["required_status_checks"] = required_status_checks
    if require_branches_to_be_up_to_date:
        kwargs[
            "require_branches_to_be_up_to_date"
        ] = require_branches_to_be_up_to_date

    required_pull_request_reviews = (
        branch_protection.required_pull_request_reviews
    )
    if required_pull_request_reviews:
        dismissal_restrictions = (
            required_pull_request_reviews.dismissal_restrictions
        )
        if dismissal_restrictions:
            if dismissal_restrictions.users:
                kwargs["dismissal_restrictions_users"] = [
                    u.login for u in dismissal_restrictions.users
                ]
            else:
                kwargs["dismissal_restrictions_users"] = []
            if dismissal_restrictions.teams:
                kwargs["dismissal_restrictions_teams"] = [
                    t.slug for t in dismissal_restrictions.teams
                ]
            else:
                kwargs["dismissal_restrictions_teams"] = []
            if dismissal_restrictions.apps:
                kwargs["dismissal_restrictions_apps"] = [
                    t.slug for t in dismissal_restrictions.apps
                ]
            else:
                kwargs["dismissal_restrictions_apps"] = []

        kwargs[
            "dismiss_stale_reviews"
        ] = required_pull_request_reviews.dismiss_stale_reviews
        kwargs[
            "require_code_owner_reviews"
        ] = required_pull_request_reviews.require_code_owner_reviews
        kwargs[
            "required_approving_review_count"
        ] = required_pull_request_reviews.required_approving_review_count
        kwargs[
            "require_last_push_approval"
        ] = required_pull_request_reviews.require_last_push_approval

        bypass_pull_request_allowances = (
            required_pull_request_reviews.bypass_pull_request_allowances
        )
        if bypass_pull_request_allowances:
            if bypass_pull_request_allowances.users is not None:
                kwargs["bypass_pull_request_allowances_users"] = [
                    u.login for u in bypass_pull_request_allowances.users
                ]
            else:
                kwargs["bypass_pull_request_allowances_users"] = []
            if bypass_pull_request_allowances.teams is not None:
                kwargs["bypass_pull_request_allowances_teams"] = [
                    t.slug for t in bypass_pull_request_allowances.teams
                ]
            else:
                kwargs["bypass_pull_request_allowances_teams"] = []
            if bypass_pull_request_allowances.apps is not None:
                kwargs["bypass_pull_request_allowances_apps"] = [
                    a.slug for a in bypass_pull_request_allowances.apps
                ]
            else:
                kwargs["bypass_pull_request_allowances_apps"] = []

    existing_restrictions = branch_protection.restrictions
    if existing_restrictions:
        if existing_restrictions.users is not None:
            kwargs["restrictions_users"] = [
                u.login for u in existing_restrictions.users
            ]
        else:
            kwargs["restrictions_users"] = []
        if existing_restrictions.teams is not None:
            kwargs["restrictions_teams"] = [
                t.slug for t in existing_restrictions.teams
            ]
        else:
            kwargs["restrictions_teams"] = []
        if existing_restrictions.apps is not None:
            kwargs["restrictions_apps"] = [
                a.slug for a in existing_restrictions.apps
            ]
        else:
            kwargs["restrictions_apps"] = []

    if dismissal_restrictions_users is not None:
        kwargs["dismissal_restrictions_users"] = list(
            dismissal_restrictions_users
        )
    if dismissal_restrictions_teams is not None:
        kwargs["dismissal_restrictions_teams"] = list(
            dismissal_restrictions_teams
        )
    if dismissal_restrictions_apps is not None:
        kwargs["dismissal_restrictions_apps"] = list(
            dismissal_restrictions_apps
        )
    if bypass_pull_request_allowances_users is not None:
        kwargs["bypass_pull_request_allowances_users"] = list(
            bypass_pull_request_allowances_users
        )
    if bypass_pull_request_allowances_teams is not None:
        kwargs["bypass_pull_request_allowances_teams"] = list(
            bypass_pull_request_allowances_teams
        )
    if bypass_pull_request_allowances_apps is not None:
        kwargs["bypass_pull_request_allowances_apps"] = list(
            bypass_pull_request_allowances_apps
        )
    if dismiss_stale_reviews is not None:
        kwargs["dismiss_stale_reviews"] = dismiss_stale_reviews
    if require_code_owner_reviews is not None:
        kwargs["require_code_owner_reviews"] = require_code_owner_reviews
    if required_approving_review_count is not None:
        kwargs[
            "required_approving_review_count"
        ] = required_approving_review_count
    if require_last_push_approval is not None:
        kwargs["require_last_push_approval"] = require_last_push_approval

    if restrictions_users is not None:
        kwargs["restrictions_users"] = restrictions_users
    if restrictions_teams is not None:
        kwargs["restrictions_teams"] = restrictions_teams
    if restrictions_apps is not None:
        kwargs["restrictions_apps"] = restrictions_apps

    return kwargs


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    # draft script for updating the branch protections
    data = await api.branches.protection_rules(args.repo, args.branch)
    branch_protection = BranchProtection.from_dict(data)
    # switch required signatures enabled/disabled
    kwargs = update_from_applied_settings(
        branch_protection,
        # pylint: disable=line-too-long
        required_signatures=not branch_protection.required_signatures.enabled,
    )
    await api.branches.update_protection_rules(
        args.repo,
        args.branch,
        **kwargs,
    )
    return 0
