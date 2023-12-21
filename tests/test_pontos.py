# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from unittest.mock import patch

from pontos import main
from pontos.version import __version__


class TestPontos(unittest.TestCase):
    @patch("pontos.pontos.RichTerminal")
    def test_pontos(self, terminal_mock):
        main()

        terminal_mock.return_value.print.assert_called()
        terminal_mock.return_value.indent.assert_called()
        terminal_mock.return_value.bold_info.assert_called()
        terminal_mock.return_value.info.assert_called()
        terminal_mock.return_value.warning.assert_called_once_with(
            'Use the listed commands "help" for more information '
            "and arguments description."
        )

    @patch("pontos.pontos.RichTerminal")
    @patch("sys.argv", ["pontos", "--version"])
    def test_pontos_version(self, terminal_mock):
        main()

        terminal_mock.return_value.print.assert_called_once_with(
            f"pontos version {__version__}"
        )
