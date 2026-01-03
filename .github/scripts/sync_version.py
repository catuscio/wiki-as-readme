import re
import tomllib
from pathlib import Path


def get_version():
    """Read version from pyproject.toml"""
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def update_server_py(version):
    """Update version in src/server.py"""
    path = Path("src/server.py")
    content = path.read_text(encoding="utf-8")

    # Replace version="x.y.z" inside FastAPI app instantiation
    # Pattern looks for: version="0.0.0" (handling potential spaces around =)
    pattern = r'(version\s*=\s*")([^"]+)(")'

    def replacement(match):
        return f"{match.group(1)}{version}{match.group(3)}"

    new_content = re.sub(pattern, replacement, content)

    if content != new_content:
        path.write_text(new_content, encoding="utf-8")
        print(f"Updated {path} to version {version}")
    else:
        print(f"No changes needed for {path}")


def update_dockerfile(path_str, version):
    """Update version label in Dockerfile"""
    path = Path(path_str)
    if not path.exists():
        print(f"Warning: {path} not found")
        return

    content = path.read_text(encoding="utf-8")

    # Replace LABEL org.opencontainers.image.version="x.y.z"
    pattern = r'(LABEL org\.opencontainers\.image\.version=")([^"]+)(")'

    def replacement(match):
        return f"{match.group(1)}{version}{match.group(3)}"

    new_content = re.sub(pattern, replacement, content)

    if content != new_content:
        path.write_text(new_content, encoding="utf-8")
        print(f"Updated {path} to version {version}")
    else:
        print(f"No changes needed for {path}")


def main():
    try:
        version = get_version()
        print(f"Syncing version: {version}")

        update_server_py(version)
        update_dockerfile("Dockerfile", version)
        update_dockerfile("Dockerfile.action", version)
        update_dockerfile("Dockerfile.server", version)

    except Exception as e:
        print(f"Error during version sync: {e}")
        exit(1)


if __name__ == "__main__":
    main()
