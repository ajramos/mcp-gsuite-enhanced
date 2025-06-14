from . import server
import asyncio
from importlib import metadata

try:
    __version__ = metadata.version("mcp-gsuite-enhanced")
except metadata.PackageNotFoundError:  # pragma: no cover - fallback when package not installed
    __version__ = "0.0.0"


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


# Optionally expose other important items at package level
__all__ = ["main", "server", "__version__"]
