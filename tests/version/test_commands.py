# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest

from pontos.version.commands import (
    PoetryVersionCommand,
    ProjectType,
    UvVersionCommand,
    get_commands,
)


class GetCommandsTestCase(unittest.TestCase):
    def test_available_commands(self):
        self.assertEqual(len(get_commands()), 7)

    def test_poetry_project_type(self):
        self.assertEqual(
            get_commands([ProjectType.POETRY]), [PoetryVersionCommand]
        )

    def test_uv_project_type(self):
        self.assertEqual(get_commands([ProjectType.UV]), [UvVersionCommand])

    def test_pyproject_project_type(self):
        self.assertEqual(
            get_commands([ProjectType.PYPROJECT]), [PoetryVersionCommand]
        )
