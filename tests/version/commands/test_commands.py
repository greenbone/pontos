# SPDX-FileCopyrightText: 2023-2025 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from pontos.version.commands import _COMMANDS, ProjectType, get_commands


class GetCommandsTestCase(unittest.TestCase):
    def test_get_all_commands(self):
        commands = get_commands()
        self.assertEqual(set(commands), set(_COMMANDS.values()))

    def test_get_specific_commands(self):
        selected_types = [ProjectType.CMAKE, ProjectType.JAVA]
        commands = get_commands(selected_types)
        self.assertEqual(
            set(commands),
            {_COMMANDS[ProjectType.CMAKE], _COMMANDS[ProjectType.JAVA]},
        )

    def test_get_no_commands(self):
        from pontos.version.commands import get_commands

        commands = get_commands([])
        self.assertEqual(set(commands), set(_COMMANDS.values()))
