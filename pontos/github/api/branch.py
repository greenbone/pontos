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

from typing import Any, Dict, Iterable, Optional, Tuple

import httpx

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.branch import BranchProtection

GITHUB_ACTIONS_APP_ID = 15368


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
    """
    Return keyword arguments for update_protection_rules by merging existing
    settings with desired updated values.
    """
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


class GitHubAsyncRESTBranches(GitHubAsyncREST):
    async def exists(self, repo: str, branch: str) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch name to check
        """
        api = f"/repos/{repo}/branches/{branch}"
        response = await self._client.get(api)
        return response.is_success

    async def delete(self, repo: str, branch: str) -> None:
        """
        Delete a branch on GitHub

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch to be deleted

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/git/refs/{branch}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def protection_rules(
        self, repo: str, branch: str
    ) -> BranchProtection:
        """
        Get branch protection rules for a specific repository
        branch

        https://docs.github.com/en/rest/branches/branch-protection#get-branch-protection

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Get protection rules for this branch

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection"
        response = await self._client.get(api)
        response.raise_for_status()
        return BranchProtection.from_dict(response.json())

    async def update_protection_rules(
        self,
        repo: str,
        branch: str,
        *,
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
    ) -> BranchProtection:
        """
        Update or create branch protection rules for a specific repository
        branch.

        https://docs.github.com/en/rest/branches/branch-protection#update-branch-protection

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Get protection rules for this branch
            required_status_checks: An iterable of status checks to require in
                order to merge into this branch. Contains tuples of the name of
                the required check and the ID of the GitHub App that must
                provide this check. Set this App ID to None to automatically
                select the GitHub App that has recently provided this check
            require_branches_to_be_up_to_date: Require branches to be up to date
                before merging.
            enforce_admins: Enforce all configured restrictions for
                administrators.
            dismissal_restrictions_users: Specify which users can dismiss pull
                request reviews.
            dismissal_restrictions_teams: Specify which teams can dismiss pull
                request reviews
            dismissal_restrictions_apps: Specify which apps can dismiss pull
                request reviews
            dismiss_stale_reviews: Set to True if you want to automatically
                dismiss approving reviews when someone pushes a new commit.
            require_code_owner_reviews: Blocks merging pull requests until code
                owners review them.
            required_approving_review_count: Specify the number of reviewers
                required to approve pull requests. Use a number between 1 and 6
                or 0 to not require reviewers.
            require_last_push_approval: Whether someone other than the person
                who last pushed to the branch must approve this pull request.
            bypass_pull_request_allowances_users: The list of user logins
                allowed to bypass pull request requirements.
            bypass_pull_request_allowances_teams: The list of team slugs allowed
                to bypass pull request requirements.
            bypass_pull_request_allowances_apps: The list of app slugs allowed
                to bypass pull request requirements.
            restrictions_users: Restrict users who can push to the protected
                branch.
            restrictions_teams: Restrict teams which can push to the protected
                branch.
            restrictions_apps: Restrict apps which can push to the protected
                branch.
            required_linear_history: Enforce a linear commit Git history.
            allow_force_pushes: Permit force pushes to the protected branch by
                anyone with write access to the repository
            allow_deletions: Allow deletion of the protected branch by anyone
                with write access to the repository.
            block_creations: If set to True, the restrictions branch protection
                settings which limits who can push will also block pushes which
                create new branches, unless the push is initiated by a user,
                team, or app which has the ability to push.
            required_conversation_resolution: Require all conversations on code
                to be resolved before a pull request can be merged into a branch
                that matches this rule.
            lock_branch: Whether to set the branch as read-only. If this is
                True, users will not be able to push to the branch.
            allow_fork_syncing: Whether users can pull changes from upstream
                when the branch is locked. Set to True to allow fork syncing.
                Set to False to prevent fork syncing.
            required_signature: True to require signed commits on a branch.

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection"
        data = {
            "enforce_admins": None,
            "required_status_checks": None,
            "required_pull_request_reviews": None,
            "restrictions": None,
        }

        if enforce_admins is not None:
            data["enforce_admins"] = enforce_admins
        if required_linear_history is not None:
            data["required_linear_history"] = required_linear_history
        if allow_force_pushes is not None:
            data["allow_force_pushes"] = allow_force_pushes
        if allow_deletions is not None:
            data["allow_deletions"] = allow_deletions
        if block_creations is not None:
            data["block_creations"] = block_creations
        if required_conversation_resolution is not None:
            data[
                "required_conversation_resolution"
            ] = required_conversation_resolution
        if lock_branch is not None:
            data["lock_branch"] = lock_branch
        if allow_fork_syncing is not None:
            data["allow_fork_syncing"] = allow_fork_syncing

        if require_branches_to_be_up_to_date is not None:
            status_checks = data.get("required_status_checks") or {}
            # checks must be set if strict is set
            status_checks["checks"] = []
            status_checks["strict"] = require_branches_to_be_up_to_date
            data["required_status_checks"] = status_checks

        if required_status_checks is not None:
            status_checks = data.get("required_status_checks") or {}
            checks = []

            for context, app_id in required_status_checks:
                check = {"context": context}
                if app_id:
                    check["app_id"] = app_id

                checks.append(check)

            status_checks["checks"] = checks
            data["required_status_checks"] = status_checks

        if restrictions_users is not None:
            restrictions = data.get("restrictions") or {}
            # teams must be set too if users are set
            r_teams = restrictions.get("teams", [])
            restrictions["teams"] = r_teams
            restrictions["users"] = list(restrictions_users)
            data["restrictions"] = restrictions
        if restrictions_teams is not None:
            restrictions = data.get("restrictions") or {}
            # users must be set too if teams are set
            r_users = restrictions.get("users", [])
            restrictions["users"] = r_users
            restrictions["teams"] = list(restrictions_teams)
            data["restrictions"] = restrictions
        if restrictions_apps is not None:
            restrictions = data.get("restrictions") or {}
            restrictions["apps"] = list(restrictions_apps)
            data["restrictions"] = restrictions

        if dismiss_stale_reviews is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            required_pull_request_reviews[
                "dismiss_stale_reviews"
            ] = dismiss_stale_reviews
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if require_code_owner_reviews is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            required_pull_request_reviews[
                "require_code_owner_reviews"
            ] = require_code_owner_reviews
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if required_approving_review_count is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            required_pull_request_reviews[
                "required_approving_review_count"
            ] = required_approving_review_count
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if require_last_push_approval is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            required_pull_request_reviews[
                "require_last_push_approval"
            ] = require_last_push_approval
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if dismissal_restrictions_users is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            dismissal_restrictions = required_pull_request_reviews.get(
                "dismissal_restrictions", {}
            )
            dismissal_restrictions["users"] = list(dismissal_restrictions_users)
            required_pull_request_reviews[
                "dismissal_restrictions"
            ] = dismissal_restrictions
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if dismissal_restrictions_teams is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            dismissal_restrictions = required_pull_request_reviews.get(
                "dismissal_restrictions", {}
            )
            dismissal_restrictions["teams"] = list(dismissal_restrictions_teams)
            required_pull_request_reviews[
                "dismissal_restrictions"
            ] = dismissal_restrictions
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if dismissal_restrictions_apps is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            dismissal_restrictions = required_pull_request_reviews.get(
                "dismissal_restrictions", {}
            )
            dismissal_restrictions["apps"] = list(dismissal_restrictions_apps)
            required_pull_request_reviews[
                "dismissal_restrictions"
            ] = dismissal_restrictions
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if bypass_pull_request_allowances_users is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            bypass_pull_request_allowances = required_pull_request_reviews.get(
                "bypass_pull_request_allowances", {}
            )
            bypass_pull_request_allowances["users"] = list(
                bypass_pull_request_allowances_users
            )
            required_pull_request_reviews[
                "bypass_pull_request_allowances"
            ] = bypass_pull_request_allowances
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if bypass_pull_request_allowances_teams is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            bypass_pull_request_allowances = required_pull_request_reviews.get(
                "bypass_pull_request_allowances", {}
            )
            bypass_pull_request_allowances["teams"] = list(
                bypass_pull_request_allowances_teams
            )
            required_pull_request_reviews[
                "bypass_pull_request_allowances"
            ] = bypass_pull_request_allowances
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if bypass_pull_request_allowances_apps is not None:
            required_pull_request_reviews = (
                data.get("required_pull_request_reviews") or {}
            )
            bypass_pull_request_allowances = required_pull_request_reviews.get(
                "bypass_pull_request_allowances", {}
            )
            bypass_pull_request_allowances["apps"] = list(
                bypass_pull_request_allowances_apps
            )
            required_pull_request_reviews[
                "bypass_pull_request_allowances"
            ] = bypass_pull_request_allowances
            data[
                "required_pull_request_reviews"
            ] = required_pull_request_reviews
        if required_signatures is not None:
            data["required_signatures"] = required_signatures

        response = await self._client.put(api, data=data)
        response.raise_for_status()
        return BranchProtection.from_dict(response.json())

    async def delete_protection_rules(self, repo: str, branch: str) -> None:
        """
        Delete branch protection rules for a specific repository branch

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Delete protection rules for this branch

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def set_enforce_admins(
        self, repo: str, branch: str, *, enforce_admins: bool
    ) -> None:
        """
        Enable/disable enforce admin branch protection rule for a specific
        repository branch.

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Delete protection rules for this branch
            enforce_admins: True to enable. False do disable.

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection/enforce_admins"
        if enforce_admins:
            response = await self._client.post(api)
        else:
            response = await self._client.delete(api)

        response.raise_for_status()

    async def set_required_signatures(
        self, repo: str, branch: str, *, required_signatures: bool
    ) -> None:
        """
        Enable/disable required signed commits for a repository branch.

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Delete protection rules for this branch
            required_signature: True to enable. False do disable.

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection/required_signatures"
        if required_signatures:
            response = await self._client.post(api)
        else:
            response = await self._client.delete(api)

        response.raise_for_status()

    async def update_required_status_checks(
        self,
        repo: str,
        branch: str,
        *,
        required_status_checks: Optional[Iterable[Tuple[str, str]]] = None,
        require_branches_to_be_up_to_date: Optional[bool] = None,
    ) -> None:
        """
        Update required status check branch protection rules of a repository
        branch.

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Delete protection rules for this branch
            required_status_checks: An iterable of status checks to require in
                order to merge into this branch. Contains tuples of the name of
                the required check and the ID of the GitHub App that must
                provide this check. Set this App ID to None to automatically
                select the GitHub App that has recently provided this check
            require_branches_to_be_up_to_date: Require branches to be up to date
                before merging.

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = (
            f"/repos/{repo}/branches/{branch}/protection/required_status_checks"
        )
        data = {}
        if require_branches_to_be_up_to_date is not None:
            data["strict"] = require_branches_to_be_up_to_date
        if required_status_checks is not None:
            checks = []
            for context, app_id in required_status_checks:
                check = {"context": context}
                if app_id:
                    check["app_id"] = app_id
                checks.append(check)
            data["checks"] = checks

        response = await self._client.patch(api, data=data)
        response.raise_for_status()

    async def remove_required_status_checks(
        self,
        repo: str,
        branch: str,
    ) -> None:
        """
        Remove required status check branch protection rules of a repository
        branch.

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Delete protection rules for this branch

        Raises:
            HTTPStatusError if the request was invalid
        """
        api = (
            f"/repos/{repo}/branches/{branch}/protection/required_status_checks"
        )
        response = await self._client.delete(api)
        response.raise_for_status()


class GitHubRESTBranchMixin:
    def branch_exists(self, repo: str, branch: str) -> bool:
        """
        Check if a single branch in a repository exists

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch name to check
        """
        api = f"/repos/{repo}/branches/{branch}"
        response: httpx.Response = self._request(api)
        return response.is_success

    def delete_branch(self, repo: str, branch: str):
        """
        Delete a branch on GitHub

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Branch to be deleted

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/git/refs/{branch}"
        response: httpx.Response = self._request(api, request=httpx.delete)
        response.raise_for_status()

    def branch_protection_rules(self, repo: str, branch: str):
        """
        Get branch protection rules for a specific repository
        branch

        Args:
            repo: GitHub repository (owner/name) to use
            branch: Get protection rules for this branch

        Raises:
            HTTPError if the request was invalid
        """
        api = f"/repos/{repo}/branches/{branch}/protection"
        response: httpx.Response = self._request(api)
        return response.json()
