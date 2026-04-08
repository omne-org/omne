"""omne CLI — kernel command dispatch.

Usage:
    python cli/omne.py init <distro> [--mounted]
    python cli/omne.py upgrade
    python cli/omne.py validate
    python cli/omne.py remove
    python cli/omne.py reset
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omne",
        description="Omne kernel CLI — manage volumes and distros",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialize a new omne volume")
    p_init.add_argument("distro", help="Distro specifier (e.g. omne-org/omne-faber)")
    p_init.add_argument("--mounted", action="store_true", help="Use submodule (mounted) mode")

    # upgrade
    sub.add_parser("upgrade", help="Upgrade distro image and kernel to latest")

    # validate
    sub.add_parser("validate", help="Check volume integrity")

    # remove
    sub.add_parser("remove", help="Tear down the omne volume")

    # reset
    sub.add_parser("reset", help="Re-stamp manifest and re-seed cfg/log")

    args = parser.parse_args()

    if args.command is None:
        parser.print_usage(sys.stderr)
        sys.exit(2)

    if args.command == "init":
        from init import init
        init(args.distro, args.mounted)

    elif args.command == "upgrade":
        from upgrade import upgrade
        upgrade()

    elif args.command == "validate":
        from validate import main as validate_main
        validate_main()

    elif args.command == "remove":
        from remove import remove
        remove()

    elif args.command == "reset":
        from reset import reset
        reset()


if __name__ == "__main__":
    main()
