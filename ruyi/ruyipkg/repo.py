import glob
import json
import os.path
import sys
from typing import Iterable, TypedDict

from git import Repo
from rich import print

from ruyi import is_debug
from .pkg_manifest import PackageManifestType
from .profile import ArchProfilesDeclType


class RepoConfigType(TypedDict):
    dist: str


class MetadataRepo:
    def __init__(self, path: str, remote: str, branch: str) -> None:
        self.root = path
        self.remote = remote
        self.branch = branch
        self.repo: Repo | None = None

    def ensure_git_repo(self) -> Repo:
        if self.repo is not None:
            return self.repo

        if os.path.exists(self.root):
            self.repo = Repo(self.root)
            return self.repo

        if is_debug():
            print(
                f"[cyan]debug:[/cyan] {self.root} does not exist, cloning from {self.remote}",
                file=sys.stderr,
            )

        # TODO: progress bar
        self.repo = Repo.clone_from(self.remote, self.root, branch=self.branch)
        return self.repo

    def sync(self) -> None:
        repo = self.ensure_git_repo()
        remote = repo.remote()
        if remote.url != self.remote:
            remote.set_url(self.remote, remote.url)
        remote.fetch()
        # cosmetic touch-up: sync the local head reference to the remote HEAD too
        main_branch = repo.heads[self.branch]
        main_branch.commit = remote.refs[self.branch].commit
        main_branch.checkout()

    def get_config(self) -> RepoConfigType:
        # we can read the config file directly because we're operating from a
        # working tree (as opposed to a bare repo)
        path = os.path.join(self.root, "config.json")
        with open(path, "rb") as fp:
            return json.load(fp)

    def iter_pkg_manifests(self) -> Iterable[PackageManifestType]:
        manifests_dir = os.path.join(self.root, "manifests")
        for f in glob.iglob("*.json", root_dir=manifests_dir):
            with open(os.path.join(manifests_dir, f), "rb") as fp:
                yield json.load(fp)

    def iter_arch_profiles(self) -> Iterable[ArchProfilesDeclType]:
        profiles_dir = os.path.join(self.root, "profiles")
        for f in glob.iglob("*.json", root_dir=profiles_dir):
            with open(os.path.join(profiles_dir, f), "rb") as fp:
                yield json.load(fp)