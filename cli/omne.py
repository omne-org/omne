"""omne CLI — kernel command dispatch.

Usage:
    python cli/omne.py init <distro> [--mounted]
    python cli/omne.py upgrade
    python cli/omne.py validate
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
    sub.add_parser("upgrade", help="Upgrade distro image to latest")

    # validate
    sub.add_parser("validate", help="Check volume integrity")

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


if __name__ == "__main__":
    main()
