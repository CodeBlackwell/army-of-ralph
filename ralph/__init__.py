"""army-of-ralph: autonomous Claude CLI orchestrator (solo + army modes)."""

from importlib.metadata import PackageNotFoundError, version

from .core import Ralph, detect_mode

try:
    __version__ = version("army-of-ralph")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["Ralph", "detect_mode", "__version__"]
