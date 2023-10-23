# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

from pontos.github.api.billing import GitHubAsyncRESTBilling
from tests.github.api import GitHubAsyncRESTTestCase, create_response


class GitHubAsyncRESTBillingTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTBilling

    async def test_actions(self):
        response = create_response()
        response.json.return_value = {
            "total_minutes_used": 305,
            "total_paid_minutes_used": 0,
            "included_minutes": 3000,
            "minutes_used_breakdown": {
                "UBUNTU": 205,
                "MACOS": 10,
                "WINDOWS": 90,
            },
        }
        self.client.get.return_value = response

        billing = await self.api.actions("foo")

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/settings/billing/actions",
        )

        self.assertEqual(billing.total_minutes_used, 305)

    async def test_packages(self):
        response = create_response()
        response.json.return_value = {
            "total_gigabytes_bandwidth_used": 50,
            "total_paid_gigabytes_bandwidth_used": 40,
            "included_gigabytes_bandwidth": 10,
        }
        self.client.get.return_value = response

        billing = await self.api.packages("foo")

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/settings/billing/packages",
        )

        self.assertEqual(billing.total_gigabytes_bandwidth_used, 50)

    async def test_storage(self):
        response = create_response()
        response.json.return_value = {
            "days_left_in_billing_cycle": 20,
            "estimated_paid_storage_for_month": 15,
            "estimated_storage_for_month": 40,
        }
        self.client.get.return_value = response

        billing = await self.api.storage("foo")

        self.client.get.assert_awaited_once_with(
            "/orgs/foo/settings/billing/shared-storage",
        )

        self.assertEqual(billing.days_left_in_billing_cycle, 20)
