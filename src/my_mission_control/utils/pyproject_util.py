from pathlib import Path
from typing import Optional

import structlog
import tomli as toml

logger = structlog.get_logger(__name__)

PYPROJECT_TOML = "pyproject.toml"


def _find_pyproject_toml(start_path: Path) -> Optional[Path]:
    """
    Traverse folder tree from starting path to find pyproject.toml.

    Args:
            start_path: The folder from where to start the search from.

    Returns:
            Path to pyproject.toml if found, otherwise None.
    """
    current_path = start_path.resolve()
    while current_path != current_path.parent:
        if (current_path / PYPROJECT_TOML).is_file():
            return current_path / PYPROJECT_TOML
        current_path = current_path.parent
    return None


def get_pyproject_metadata():
    """
    Reads project metadata from pyproject.toml.
    """
    try:
        pyproject_path = _find_pyproject_toml(Path(__file__).parent)

        if pyproject_path:
            with open(pyproject_path, "rb") as f:
                metadata = toml.load(f)

            project = metadata["project"]

            return project["name"], project["version"]
    except FileNotFoundError:
        logger.error("pyproject.toml not found.")
    except KeyError:
        logger.error("name or version not found in [project] section.")

    return None, None
