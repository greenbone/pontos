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

import logging
from pathlib import Path


class TerminalLogger:
    def __init__(self, log_file: Path, *, level: int = logging.INFO) -> None:
        if log_file:
            logging.basicConfig(
                filename=log_file,
                filemode="a",
                format="%(message)s",
                level=level,
            )
            self._logger = logging.getLogger("TerminalLogger")

    def log(self, message: str):
        self._logger.info(msg=message)

    def debug(self, message: str):
        self._logger.debug(msg=message)
