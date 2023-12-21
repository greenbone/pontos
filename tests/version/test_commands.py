# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest

from pontos.version.commands import get_commands


class GetCommandsTestCase(unittest.TestCase):
    def test_available_commands(self):
        self.assertEqual(len(get_commands()), 6)
