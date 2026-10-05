"""Shared helper functions for the project."""

from pathlib import Path

import pandas as pd


def ensure_project_directories(*directories: Path) -> None:
    """Create each folder if it does not already exist."""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def save_table(dataframe: pd.DataFrame, path: Path) -> None:
    """Save a summary table as a CSV file."""
    dataframe.to_csv(
        path,
        index=True,
        encoding="utf-8",
        float_format="%.2f",
    )


def format_number(value: object, digits: int = 2) -> str:
    """Format a number for readable report text."""
    if pd.isna(value):
        return "Not available"

    return f"{value:,.{digits}f}"