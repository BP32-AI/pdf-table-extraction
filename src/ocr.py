"""
ocr.py

OCR-based table extraction for scanned PDF documents.

Pipeline
--------
PDF
    ↓
Convert PDF pages to images
    ↓
Image preprocessing
    ↓
Tesseract OCR
    ↓
Reconstruct table
    ↓
Return List[pandas.DataFrame]
"""

from pathlib import Path
from typing import List

import cv2
import numpy as np
import pandas as pd
import pytesseract
from pdf2image import convert_from_path

from logger import get_logger
from utils import clean_dataframe

logger = get_logger(__name__)


class OCRTableExtractor:
    """
    Extract tables from scanned PDF documents using
    Tesseract OCR.
    """

    def __init__(self) -> None:

        logger.info("Initializing Tesseract OCR...")

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def extract(
        self,
        pdf_path: Path,
    ) -> List[pd.DataFrame]:
        """
        Extract tables from scanned PDF.

        Parameters
        ----------
        pdf_path : Path

        Returns
        -------
        List[pandas.DataFrame]
        """

        logger.info(
            "Processing scanned PDF: %s",
            pdf_path.name,
        )

        images = convert_from_path(pdf_path)

        extracted_tables = []

        for page_number, image in enumerate(images, start=1):

            logger.info(
                "OCR Processing Page %d",
                page_number,
            )

            image = cv2.cvtColor(
                np.array(image),
                cv2.COLOR_RGB2BGR,
            )

            image = self._preprocess(image)

            page_tables = self._extract_from_image(
                image
            )

            extracted_tables.extend(
                page_tables
            )

        logger.info(
            "OCR extracted %d table(s).",
            len(extracted_tables),
        )

        return extracted_tables

    # --------------------------------------------------
    # Image Preprocessing
    # --------------------------------------------------

    def _preprocess(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Improve OCR quality.
        """

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0,
        )

        binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]

        return binary

    # --------------------------------------------------
    # OCR
    # --------------------------------------------------

    def _extract_from_image(
        self,
        image: np.ndarray,
    ) -> List[pd.DataFrame]:
        """
        Run OCR using Tesseract.

        Returns
        -------
        List[pandas.DataFrame]
        """

        ocr_data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            config="--psm 6",
        )

        words = []

        total = len(
            ocr_data["text"]
        )

        for i in range(total):

            text = ocr_data["text"][i].strip()

            if not text:
                continue

            confidence = float(
                ocr_data["conf"][i]
            )

            if confidence < 20:
                continue

            words.append(
                {
                    "text": text,
                    "x": ocr_data["left"][i],
                    "y": ocr_data["top"][i],
                }
            )

        if not words:
            return []

        table = self._build_table(
            words
        )

        if table.empty:
            return []

        return [table]
    
        # --------------------------------------------------
    # Build Table
    # --------------------------------------------------

    def _build_table(
        self,
        words: list,
    ) -> pd.DataFrame:
        """
        Reconstruct a table from OCR words.

        Strategy
        --------
        1. Sort words by (y, x)
        2. Group words into rows using Y coordinate
        3. Sort each row by X coordinate
        4. Normalize row length
        5. Return DataFrame
        """

        tolerance = 15

        words = sorted(
            words,
            key=lambda item: (
                item["y"],
                item["x"],
            ),
        )

        rows = []

        current_row = []

        current_y = None

        for word in words:

            if current_y is None:

                current_y = word["y"]

            if abs(word["y"] - current_y) <= tolerance:

                current_row.append(word)

            else:

                current_row = sorted(
                    current_row,
                    key=lambda item: item["x"],
                )

                rows.append(
                    [
                        cell["text"]
                        for cell in current_row
                    ]
                )

                current_row = [word]

                current_y = word["y"]

        if current_row:

            current_row = sorted(
                current_row,
                key=lambda item: item["x"],
            )

            rows.append(
                [
                    cell["text"]
                    for cell in current_row
                ]
            )

        if len(rows) < 2:

            logger.warning(
                "OCR could not reconstruct a valid table."
            )

            return pd.DataFrame()

        max_columns = max(
            len(row)
            for row in rows
        )

        normalized_rows = []

        for row in rows:

            row = row + [""] * (
                max_columns - len(row)
            )

            normalized_rows.append(row)

        df = pd.DataFrame(normalized_rows)

        if df.empty:
            return df

        try:

            # First row becomes header
            df.columns = df.iloc[0]

            df = df.iloc[1:].reset_index(drop=True)

        except Exception:

            pass

        df = clean_dataframe(df)

        logger.info(
            "OCR reconstructed table with %d rows and %d columns.",
            len(df),
            len(df.columns),
        )

        return df