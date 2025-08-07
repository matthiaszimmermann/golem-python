import json
import os
from logging import (
    Filter,
    Logger,
    LogRecord,
    config,
    getLogger,
    getLoggerClass,
    root,
    setLoggerClass,
)
from pathlib import Path

LOGGER_CONFIG_FILE = Path("logging_config.json")

logger_config_loaded = False


class RelativePathLogRecord(LogRecord):
    """Extended LogRecord that adds a relpath attribute for relative paths."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: D107 ANN002 ANN003
        super().__init__(*args, **kwargs)
        workspace_path = os.getcwd()  # noqa: PTH109
        try:
            # Convert pathname to a relative path from workspace root
            if hasattr(self, "pathname") and self.pathname.startswith(workspace_path):
                self.relpath = os.path.relpath(self.pathname, workspace_path)
            else:
                self.relpath = self.pathname
        except (AttributeError, ValueError):
            self.relpath = self.pathname


class RelativePathFilter(Filter):
    """Filter that ensures the relpath attribute is available."""

    def filter(self, record) -> bool:  # noqa: D102 ARG002 ANN001
        return True


class RelativePathLoggerFactory(getLoggerClass()):
    """Custom logger class that uses RelativePathLogRecord."""

    # ruff: noqa
    def makeRecord(
        self,
        name,
        level,
        fn,
        lno,
        msg,
        args,
        exc_info,
        func=None,
        extra=None,
        sinfo=None,
    ) -> RelativePathLogRecord:
        """Create a RelativePathLogRecord."""
        return RelativePathLogRecord(
            name, level, fn, lno, msg, args, exc_info, func, sinfo
        )

    # ruff: enable


def setup_logging() -> None:  # noqa: D103
    global logger_config_loaded  # noqa: PLW0603

    if logger_config_loaded:
        return

    # Set the custom logger class
    setLoggerClass(RelativePathLoggerFactory)

    with LOGGER_CONFIG_FILE.open() as f:
        config_from_json = json.load(f)

    config.dictConfig(config_from_json)

    # Add filter to all handlers to ensure relpath is available
    for handler in root.handlers:
        handler.addFilter(RelativePathFilter())

    logger_config_loaded = True


def get_logger(name: str) -> Logger:  # noqa: D103
    setup_logging()
    return getLogger(name)
