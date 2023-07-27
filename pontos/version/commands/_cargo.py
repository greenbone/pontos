from pathlib import Path
from typing import Iterator, Literal, Tuple, Union

import tomlkit

from ..errors import VersionError
from ..version import Version, VersionUpdate
from ._command import VersionCommand


class CargoVersionCommand(VersionCommand):
    project_file_name = "Cargo.toml"

    def __as_project_document(
        self, origin: Path
    ) -> Iterator[Tuple[Path, tomlkit.TOMLDocument],]:
        """
        Parse the given origin and yields a tuple of path to a
        cargo toml that contains a version

        If the origin is invalid toml than it will raise a VersionError.
        """
        content = origin.read_text(encoding="utf-8")
        content = tomlkit.parse(content)
        package = content.get("package")
        if package:
            version = package.get("version")
            if version:
                yield (origin, content)
        else:
            workspace = content.get("workspace")
            if workspace:
                members = workspace.get("members")
                for member in members:
                    yield from self.__as_project_document(
                        origin.parent / member / self.project_file_name
                    )
        return None

    def update_version(
        self, new_version: Version, *, force: bool = False
    ) -> VersionUpdate:
        try:
            previous_version = self.get_current_version()

            if not force and new_version == previous_version:
                return VersionUpdate(previous=previous_version, new=new_version)
        except VersionError:
            # just ignore current version and override it
            previous_version = None

        changed_files = []
        for project_path, project in self.__as_project_document(
            self.project_file_path
        ):
            project["package"]["version"] = str(new_version)  # type: ignore[index] # noqa: E501
            project_path.write_text(tomlkit.dumps(project))
            changed_files.append(project_path)
        return VersionUpdate(
            previous=previous_version,
            new=new_version,
            changed_files=changed_files,
        )

    def get_current_version(self) -> Version:
        (_, document) = next(self.__as_project_document(self.project_file_path))
        current_version = self.versioning_scheme.parse_version(
            document["package"]["version"]  # type: ignore[index, arg-type]
        )
        return self.versioning_scheme.from_version(current_version)

    def verify_version(
        self, version: Union[Literal["current"], Version, None]
    ) -> None:
        current_version = self.get_current_version()

        if not version or version == "current":
            return

        if current_version != version:
            raise VersionError(
                f"Provided version {version} does not match the "
                f"current version {current_version}."
            )
