"""Distro spec parsing."""


def parse_distro(spec: str) -> tuple[str, str]:
    """Parse a distro specifier into (clone_url, distro_name).

    Accepted formats:
      - "omne-faber"                          -> omne-org default
      - "omne-org/omne-faber"                 -> org/repo shorthand
      - "https://github.com/org/repo.git"     -> full HTTPS URL
      - "git@github.com:org/repo.git"         -> full SSH URL
    """
    # Full URL (https, ssh, or file://)
    if spec.startswith("https://") or spec.startswith("git@") or spec.startswith("file://"):
        name = spec.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
        return spec, name

    # org/repo shorthand
    if "/" in spec:
        org, repo = spec.split("/", 1)
        return f"https://github.com/{org}/{repo}.git", repo

    # Bare name — default to omne-org
    return f"https://github.com/omne-org/{spec}.git", spec
