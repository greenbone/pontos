import argparse
import sys
import subprocess
import os
import json
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Union

import requests
from pontos import version
from pontos import changelog


def build_release_dict(
    release_version: str,
    release_changelog: str,
    name: str = '',
    target_commitish: str = '',  # needed when tag is not there yet
    draft: bool = False,
    prerelease: bool = False,
) -> Dict[str, Union[str, bool]]:
    """
    builds the dict for release post on github, see:
    https://docs.github.com/en/rest/reference/repos#create-a-release
    for more details.
    """
    tag_name = (
        release_version
        if release_version.startswith('v')
        else "v" + release_version
    )
    return {
        'tag_name': tag_name,
        'target_commitish': target_commitish,
        'name': name,
        'body': release_changelog,
        'draft': draft,
        'prerelease': prerelease,
    }


def initialize_default_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Release handling utility.', prog='pontos-release',
    )
    parser.add_argument(
        '--release-version',
        help='Will release changelog as version. Must be PEP 440 compliant',
        required=True,
    )
    parser.add_argument(
        '--next-release-version',
        help='Sets the next PEP 440 compliant version in project definition.',
        required=True,
    )
    parser.add_argument(
        '--project', help='The github project', required=True,
    )
    parser.add_argument(
        '--space', default='greenbone', help='user/team name in github',
    )
    parser.add_argument(
        '--signing-key',
        default='0ED1E580',
        help='The key to sign zip, tarballs of a release',
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest='command',
    )

    subparsers.add_parser('release')
    return parser


def parse(args=None):
    parser = initialize_default_parser()
    commandline_arguments = parser.parse_args(args)
    token = (
        os.environ['GITHUB_TOKEN']
        if not args or not 'testcases' in args
        else 'TOKEN'
    )
    user = (
        os.environ['GITHUB_USER']
        if not args or not 'testcases' in args
        else 'USER'
    )
    return (
        commandline_arguments.command,
        commandline_arguments.release_version,
        commandline_arguments.next_release_version,
        commandline_arguments.project,
        commandline_arguments.space,
        commandline_arguments.signing_key,
        user,
        token,
    )


def run(
    release_version: str,
    nextversion: str,
    project: str,
    space: str,
    signing_key: str,
    username: str,
    token: str,
    git_tag_prefix: str,
    shell_cmd_runner: Callable,
    _path: Path,
    _requests: requests,
    _version: version,
    _changelog: changelog,
):
    print("in release")
    executed, filename = _version.main(
        False, args=["--quiet", "update", nextversion]
    )
    if not executed:
        if filename == "":
            print("No project definition found.")
        else:
            print("Unable to update version {} in {}", nextversion, filename)
        return False
    print("updated version {} to {}".format(filename, nextversion))
    change_log_path = _path.cwd() / 'CHANGELOG.md'
    updated, changelog_text = _changelog.update(
        change_log_path.read_text(),
        release_version,
        project,
        git_tag_prefix=git_tag_prefix,
        git_space=space,
    )
    change_log_path.write_text(updated)
    print("updated CHANGELOG.md")
    git = GithubRelease(
        token,
        username,
        project,
        signing_key,
        space=space,
        tag_prefix=git_tag_prefix,
        run_cmd=shell_cmd_runner,
        path=_path,
        gh_requests=_requests,
    )
    return git.commit(filename, release_version, changelog_text)


class GithubRelease:
    space = None
    project = None
    token = None
    user = None
    tag_prefix = None
    signing_key = None
    __run = None
    __path = None
    __requests = None

    def __init__(
        self,
        token: str,
        user: str,
        project: str,
        signing_key: str,
        space: str = 'greenbone',
        tag_prefix: str = 'v',
        run_cmd=lambda x: subprocess.run(x, shell=True, check=True),
        path: Path = Path,
        gh_requests: requests = requests,
    ):
        self.auth = (user, token)
        self.project = project
        self.space = space
        self.tag_prefix = tag_prefix
        self.signing_key = signing_key
        self.__run = run_cmd
        self.__path = path
        self.__requests = gh_requests

    def commit(
        self, project_filename: str, release_version: str, changelog_text: str,
    ) -> bool:
        """
        commit adds:
        - filename
        - CHANGELOG.md
        commits those changes, creates a tag based on:
        - release_version
        - tag_prefix
        pushes those changes into remote repository and creates a release.
        """
        print("Commiting changes")
        self.__run("git add {}".format(project_filename))
        self.__run("git add *__version__.py || echo 'ignoring __version__'")
        self.__run("git add CHANGELOG.md")
        commit_msg = 'automatic release to {}'.format(release_version)
        self.__run("git commit -S -m '{}'".format(commit_msg),)
        git_version = "{}{}".format(self.tag_prefix, release_version)
        self.__run("git tag -s {} -m '{}'".format(git_version, commit_msg),)
        print("Pushing changes")
        self.__run("git push --follow-tags")
        return self.create_release(git_version, changelog_text)

    def create_release(self, git_version: str, changelog_text: str) -> bool:
        def download(url, filename):
            file_path = self.__path("/tmp/{}".format(filename))
            with self.__requests.get(url, stream=True) as resp:
                with file_path.open(mode='wb') as download_file:
                    shutil.copyfileobj(resp.raw, download_file)
            return file_path

        print("Creating release")
        release_info = build_release_dict(git_version, changelog_text)
        headers = {'Accept': 'application/vnd.github.v3+json'}
        base_url = "https://api.github.com/repos/{}/{}/releases".format(
            self.space, self.project
        )
        response = self.__requests.post(
            base_url, headers=headers, auth=self.auth, json=release_info
        )
        if response.status_code != 201:
            print("Wrong reponse status code: {}".format(response.status_code))
            print(json.dumps(response.text, indent=4, sort_keys=True))
            return False
        github_json = json.loads(response.text)
        zip_path = download(github_json['zipball_url'], git_version + ".zip")
        tar_path = download(github_json['tarball_url'], git_version + ".tar.gz")
        print("Signing {}".format([zip_path, tar_path]))
        gpg_cmd = "gpg --default-key {} --detach-sign --armor {}"
        self.__run(gpg_cmd.format(self.signing_key, zip_path))
        self.__run(gpg_cmd.format(self.signing_key, tar_path))
        return self.upload_assets([zip_path, tar_path], github_json)

    def upload_assets(self, pathnames: List[str], github_json: str) -> bool:
        print("Uploading assets: {}".format(pathnames))
        asset_url = github_json['upload_url'].replace('{?name,label}', '')
        paths = [self.__path('{}.asc'.format(p)) for p in pathnames]
        upload_headers = {
            'Accept': 'application/vnd.github.v3+json',
            'content-type': 'application/octet-stream',
        }
        for path in paths:
            to_upload = path.read_bytes()
            resp = self.__requests.post(
                "{}?name={}".format(asset_url, path.name),
                headers=upload_headers,
                auth=self.auth,
                data=to_upload,
            )
            if resp.status_code != 201:
                print(
                    "Wrong reponse status {} while uploading {}".format(
                        resp.status_code, path.name
                    )
                )
                print(json.dumps(resp.text, indent=4, sort_keys=True))
                return False
            else:
                print("uploaded: {}".format(path.name))
        return True


def main(
    git_tag_prefix: str = "v",
    shell_cmd_runner=lambda x: subprocess.run(x, shell=True, check=True),
    _path: Path = Path,
    _requests: requests = requests,
    _version: version = version,
    _changelog: changelog = changelog,
    leave: bool = True,
    args=None,
):
    def execute(
        command: str,
        release_version: str,
        next_release_version: str,
        project: str,
        space: str,
        signing_key: str,
        user: str,
        token: str,
    ):
        if command == 'release':
            return run(
                release_version,
                next_release_version,
                project,
                space,
                signing_key,
                user,
                token,
                git_tag_prefix,
                shell_cmd_runner,
                _path,
                _requests,
                _version,
                _changelog,
            )
        raise ValueError("Unknown command: {}".format(command))

    values = parse(args)
    if not values:
        return sys.exit(1) if leave else False
    if not execute(*values):
        return sys.exit(1) if leave else False
    return execute(*values)


if __name__ == '__main__':
    main()
