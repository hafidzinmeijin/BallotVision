"""Small helpers used by several pages."""

from datetime import datetime
from pathlib import Path


def format_number(value: int) -> str:
    return f"{int(value):,}"


def format_percent(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}%"


def format_timestamp(value: datetime, time_format: str = "24-hour") -> str:
    if time_format == "12-hour":
        return value.strftime("%d %b %Y, %I:%M %p")
    return value.strftime("%d %b %Y, %H:%M:%S")


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    folder = project_root() / "data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def settings_path() -> Path:
    return data_dir() / "settings.json"
