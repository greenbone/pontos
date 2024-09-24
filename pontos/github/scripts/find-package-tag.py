# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
This script checks wether a package has a specific tag
"""

from argparse import ArgumentParser, Namespace

from pontos.github.api import GitHubAsyncRESTApi
from pontos.github.models.packages import PackageType


def package_type(value: str) -> PackageType:
    if isinstance(value, PackageType):
        return value
    return PackageType(value.lower())


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("organization", help="organization name")
    parser.add_argument("package", help="package name")
    parser.add_argument("tag", help="tag to check")
    parser.add_argument(
        "--package-type",
        type=package_type,
        help="package type",
        default=PackageType.CONTAINER,
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    if not await api.packages.exists(
        organization=args.organization,
        package_name=args.package,
        package_type=args.package_type,
    ):
        print(
            f"Package {args.package} does not exist in organization {args.organization}"
        )
        return 1
    print(f"Found package {args.package} in organization {args.organization}")

    async for package in api.packages.package_versions(
        organization=args.organization,
        package_name=args.package,
        package_type=args.package_type,
    ):
        print(f"Checking package {args.package} with id {package.id}")
        if package.metadata.container.tags:
            if args.tag in package.metadata.container.tags:
                print(
                    f"Package {args.package} with id {package.id} has tag {args.tag}"
                )
                tags = await api.packages.package_version_tags(
                    args.organization,
                    args.package_type,
                    args.package,
                    package.id,
                )
                print(f"Tags: {tags}")

                await api.packages.delete_package_version(
                    args.organization,
                    args.package_type,
                    args.package,
                    package.id,
                )
                return 0

    print(f"Package {args.package} does not have tag {args.tag}")
    return 0
