# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ruff: noqa:E501

import unittest

from pontos.github.models.billing import (
    ActionsBilling,
    PackagesBilling,
    StorageBilling,
)


class ActionsBillingTestCase(unittest.TestCase):
    def test_from_dict(self):
        billing = ActionsBilling.from_dict(
            {
                "total_minutes_used": 305,
                "total_paid_minutes_used": 0,
                "included_minutes": 3000,
                "minutes_used_breakdown": {
                    "UBUNTU": 205,
                    "MACOS": 10,
                    "WINDOWS": 90,
                },
            }
        )

        self.assertEqual(billing.total_minutes_used, 305)
        self.assertEqual(billing.total_paid_minutes_used, 0)
        self.assertEqual(billing.included_minutes, 3000)
        self.assertEqual(billing.minutes_used_breakdown.UBUNTU, 205)
        self.assertEqual(billing.minutes_used_breakdown.MACOS, 10)
        self.assertEqual(billing.minutes_used_breakdown.WINDOWS, 90)
        self.assertIsNone(billing.minutes_used_breakdown.total)


class PackagesBillingTestCase(unittest.TestCase):
    def test_from_dict(self):
        billing = PackagesBilling.from_dict(
            {
                "total_gigabytes_bandwidth_used": 50,
                "total_paid_gigabytes_bandwidth_used": 40,
                "included_gigabytes_bandwidth": 10,
            }
        )

        self.assertEqual(billing.total_gigabytes_bandwidth_used, 50)
        self.assertEqual(billing.total_paid_gigabytes_bandwidth_used, 40)
        self.assertEqual(billing.included_gigabytes_bandwidth, 10)


class StorageBillingTestCase(unittest.TestCase):
    def test_from_dict(self):
        billing = StorageBilling.from_dict(
            {
                "days_left_in_billing_cycle": 20,
                "estimated_paid_storage_for_month": 15,
                "estimated_storage_for_month": 40,
            }
        )
        self.assertEqual(billing.days_left_in_billing_cycle, 20)
        self.assertEqual(billing.estimated_paid_storage_for_month, 15)
        self.assertEqual(billing.estimated_storage_for_month, 40)
