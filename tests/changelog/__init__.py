# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def use_cwd(path: Path) -> None:
    """
    Context Manager to change the current working directory temporaryly
    """
    current_cwd = Path.cwd()

    os.chdir(str(path))

    yield

    os.chdir(str(current_cwd))
