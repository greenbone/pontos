# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import unittest
from contextlib import redirect_stderr
from io import StringIO

from pontos.version._parser import parse_args


class ParserTestCase(unittest.TestCase):
    def test_error_while_parsing(self):
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as cm:
            parse_args(["update", "foo"])

        # exception code in argparse
        self.assertEqual(cm.exception.code, 2)
