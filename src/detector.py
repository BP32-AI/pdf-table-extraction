# src/detector.py

"""
detector.py

Detect whether a PDF is a digital (text-based) document
or a scanned (image-based) document.

This module avoids unnecessary OCR by first checking whether
the PDF contains extractable text.
"""

from enum import Enum
from pathlib import Path

import pdfplumber

from logger import get_logger

logger = get_logger(__name__)


class PDFType(Enum):
    """
    Supported PDF document types.
    """

    DIGITAL = "digital"
    SCANNED = "scanned"


class PDFDetector:
    """
    Detect the type of a PDF document.

    Methods
    -------
    detect(pdf_path)
        Returns PDFType.DIGITAL or PDFType.SCANNED.
    """

    def __init__(self) -> None:
        pass

    def detect(self, pdf_path: Path) -> PDFType:
        """
        Detect whether the given PDF is digital or scanned.

        Parameters
        ----------
        pdf_path : Path

        Returns
        -------
        PDFType
        """

        logger.info("Checking PDF type: %s", pdf_path.name)

        try:

            with pdfplumber.open(pdf_path) as pdf:

                for page_number, page in enumerate(pdf.pages, start=1):

                    text = page.extract_text()

                    if text and text.strip():

                        logger.info(
                            "Digital PDF detected (text found on page %d).",
                            page_number,
                        )

                        return PDFType.DIGITAL

            logger.info("Scanned PDF detected (no extractable text found).")

            return PDFType.SCANNED

        except Exception as exc:

            logger.exception(
                "Failed while detecting PDF type: %s",
                exc,
            )

            raise