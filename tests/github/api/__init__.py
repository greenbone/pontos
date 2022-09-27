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

from pontos.github.api.helper import DEFAULT_TIMEOUT_CONFIG


def default_request(*args, **kwargs):
    default_kwargs = {
        "follow_redirects": True,
        "headers": {
            "Authorization": "token 12345",
            "Accept": "application/vnd.github.v3+json",
        },
        "params": None,
        "timeout": DEFAULT_TIMEOUT_CONFIG,
    }
    default_kwargs.update(kwargs)
    return args, default_kwargs
