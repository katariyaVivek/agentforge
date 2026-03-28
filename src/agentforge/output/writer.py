from pathlib import Path
from typing import Union


def write_file(path: Union[str, Path], content: str) -> Path:
    """Write content to a file, creating parent directories as needed.

    Args:
        path: File path (str or Path)
        content: Content to write

    Returns:
        Path to the written file
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path
