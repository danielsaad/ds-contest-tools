try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .ds_contest_tools import main
