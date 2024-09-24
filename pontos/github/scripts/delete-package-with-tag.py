"""
This script delete a package from a repository, if it contains the specified tag.
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
    parser.add_argument(
        "--package-type",
        type=package_type,
        help="package type",
        default=PackageType.CONTAINER,
    )
    parser.add_argument("tag", help="The tag to be deleted.")


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

    await api.packages.delete_package_with_tag(
        organization=args.organization,
        package_name=args.package,
        package_type=args.package_type,
        tag=args.tag,
    )
    print(
        f"Deleted tag {args.tag} from package {args.package} in organization {args.organization}"
    )
    return 0
