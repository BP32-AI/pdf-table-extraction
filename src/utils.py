# src/utils.py


"""
utils.py

Utility functions used across the PDF Table Extraction project.
"""

from pathlib import Path
from typing import List

import pandas as pd
import pdfplumber

from logger import get_logger

logger = get_logger(__name__)


def create_output_directories(output_dir: Path) -> None:
    """
    Create required output directories if they do not exist.

    Structure:
        output/
            ├── json/
            ├── csv/
            └── excel/
    """

    (output_dir / "json").mkdir(parents=True, exist_ok=True)
    (output_dir / "csv").mkdir(parents=True, exist_ok=True)
    (output_dir / "excel").mkdir(parents=True, exist_ok=True)


def get_pdf_files(input_dir: Path) -> List[Path]:
    """
    Return all PDF files from the input directory.

    Parameters
    ----------
    input_dir : Path

    Returns
    -------
    List[Path]
    """

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    pdf_files = sorted(input_dir.glob("*.pdf"))

    logger.info("Found %d PDF file(s).", len(pdf_files))

    return pdf_files


def is_digital_pdf(pdf_path: Path) -> bool:
    """
    Determine whether a PDF is digital or scanned.

    Returns
    -------
    True
        If extractable text exists.

    False
        Otherwise (likely scanned).
    """

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:

                text = page.extract_text()

                if text and text.strip():
                    return True

    except Exception as e:
        logger.error("Failed checking PDF type: %s", e)

    return False


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean extracted table.

    Operations:
        - Replace NaN
        - Remove empty rows
        - Strip whitespace
    """

    df = df.fillna("")

    df = df.apply(
        lambda col: col.map(
            lambda value: str(value).strip()
            if value is not None
            else ""
        )
    )

    df = df.loc[
        ~(df == "").all(axis=1)
    ]

    df.reset_index(drop=True, inplace=True)

    return df


def sanitize_filename(filename: str) -> str:
    """
    Remove unsupported filename characters.
    """

    invalid = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    for char in invalid:
        filename = filename.replace(char, "_")

    return filename


def dataframe_to_rows(df: pd.DataFrame) -> List[List[str]]:
    """
    Convert DataFrame into JSON row format.

    Returns
    -------
    [
        ["A","B","C"],
        ["1","2","3"]
    ]
    """

    return df.astype(str).values.tolist()


def dataframe_columns(df: pd.DataFrame) -> List[str]:
    """
    Return DataFrame column names.
    """

    return [str(column) for column in df.columns]


def document_id(pdf_path: Path) -> str:
    """
    Extract document id.

    Example
    -------
    doc_01.pdf

    becomes

    doc_01
    """

    return pdf_path.stem