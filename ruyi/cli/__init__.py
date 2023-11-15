import argparse
import os
import platform
from typing import List

import ruyi
from .. import log
from ..mux.runtime import mux_main
from ..mux.venv import cli_venv
from ..ruyipkg.pkg_cli import cli_install, cli_list
from ..ruyipkg.profile_cli import cli_list_profiles
from ..ruyipkg.update import cli_update
from .nuitka import get_nuitka_self_exe

RUYI_ENTRYPOINT_NAME = "ruyi"


def is_called_as_ruyi(argv0: str) -> bool:
    return os.path.basename(argv0) in {RUYI_ENTRYPOINT_NAME, "__main__.py"}


def init_debug_status() -> None:
    debug_env = os.environ.get("RUYI_DEBUG", "")
    ruyi.set_debug(debug_env.lower() in {"1", "true", "x", "y", "yes"})


def init_argparse() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog=RUYI_ENTRYPOINT_NAME,
        description="RuyiSDK Package Manager",
    )
    sp = root.add_subparsers(required=True)

    install = sp.add_parser(
        "install", aliases=["i"], help="Install package from configured repository"
    )
    install.add_argument(
        "atom",
        type=str,
        nargs="+",
        help="Specifier (atom) of the package to install",
    )
    install.add_argument(
        "-f",
        "--fetch-only",
        action="store_true",
        help="Fetch distribution files only without installing",
    )
    install.add_argument(
        "--host",
        type=str,
        default=platform.machine(),
        help="Override the host architecture (normally not needed)",
    )
    install.add_argument(
        "--prerelease",
        action="store_true",
        help="Do not ignore pre-release package versions",
    )
    install.add_argument(
        "--reinstall",
        action="store_true",
        help="Force re-installation of already installed packages",
    )
    install.set_defaults(func=cli_install)

    list = sp.add_parser(
        "list", help="List available packages in configured repository"
    )
    list.set_defaults(func=cli_list)
    list.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Also show details for every package",
    )

    listsp = list.add_subparsers(required=False)
    list_profiles = listsp.add_parser("profiles", help="List all available profiles")
    list_profiles.set_defaults(func=cli_list_profiles)

    up = sp.add_parser("update", help="Update RuyiSDK repo and packages")
    up.set_defaults(func=cli_update)

    venv = sp.add_parser(
        "venv",
        help="Generate a virtual environment adapted to the chosen toolchain and profile",
    )
    venv.add_argument("profile", type=str, help="Profile to use for the environment")
    venv.add_argument("dest", type=str, help="Path to the new virtual environment")
    venv.add_argument(
        "--name",
        "-n",
        type=str,
        default=None,
        help="Override the venv's name",
    )
    venv.add_argument(
        "--toolchain",
        "-t",
        type=str,
        help="Slug of the toolchain to use",
    )
    venv.set_defaults(func=cli_venv)

    return root


def main(argv: List[str]) -> int:
    init_debug_status()

    if not argv:
        log.F("no argv?")
        return 1

    # note down our own executable path, for identity-checking in mux, if not
    # we're not already Nuitka-compiled
    #
    # we assume the one-file build if Nuitka is detected; sys.argv[0] does NOT
    # work if it's just `ruyi` so we have to check our parent process in that case
    if hasattr(ruyi, "__compiled__"):
        self_exe = get_nuitka_self_exe()
    else:
        self_exe = __file__

    log.D(f"argv[0] = {argv[0]}, self_exe = {self_exe}")
    ruyi.record_self_exe(self_exe)

    if not is_called_as_ruyi(argv[0]):
        return mux_main(argv)

    p = init_argparse()
    args = p.parse_args(argv[1:])
    log.D(f"args={args}")

    try:
        return args.func(args)
    except Exception as e:
        # print(f"[bold red]fatal error:[/bold red] no command specified {e}")
        # return 1
        raise

    return 0
