# src/extractor.py

"""
extractor.py

Extract tables from digital (text-based) PDF documents.

Extraction Strategy
-------------------
1. Camelot (Lattice)
2. Camelot (Stream)
3. pdfplumber (Fallback)

Only tabular content is returned.
Narrative text, page titles and footer notes are removed.
"""

from pathlib import Path
from typing import List

import camelot
import pandas as pd
import pdfplumber

from logger import get_logger
from utils import clean_dataframe

logger = get_logger(__name__)


class TableExtractor:
    """
    Extract tables from digital PDF documents.
    """

    def __init__(self) -> None:
        pass

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def extract(
        self,
        pdf_path: Path,
    ) -> List[pd.DataFrame]:
        """
        Extract tables from PDF.
        """

        logger.info(
            "Starting table extraction: %s",
            pdf_path.name,
        )

        tables = self._extract_with_camelot_lattice(
            pdf_path
        )

        if tables:

            logger.info(
                "Extracted %d table(s) using Camelot (Lattice).",
                len(tables),
            )

            return tables

        tables = self._extract_with_camelot_stream(
            pdf_path
        )

        if tables:

            logger.info(
                "Extracted %d table(s) using Camelot (Stream).",
                len(tables),
            )

            return tables

        tables = self._extract_with_pdfplumber(
            pdf_path
        )

        logger.info(
            "Extracted %d table(s) using pdfplumber.",
            len(tables),
        )

        return tables

    # ---------------------------------------------------------
    # Camelot Lattice
    # ---------------------------------------------------------

    def _extract_with_camelot_lattice(
        self,
        pdf_path: Path,
    ) -> List[pd.DataFrame]:

        try:

            camelot_tables = camelot.read_pdf(
                str(pdf_path),
                pages="all",
                flavor="lattice",
            )

            return self._camelot_to_dataframe(
                camelot_tables
            )

        except Exception as exc:

            logger.warning(
                "Camelot Lattice failed: %s",
                exc,
            )

            return []

    # ---------------------------------------------------------
    # Camelot Stream
    # ---------------------------------------------------------

    def _extract_with_camelot_stream(
        self,
        pdf_path: Path,
    ) -> List[pd.DataFrame]:

        try:

            camelot_tables = camelot.read_pdf(
                str(pdf_path),
                pages="all",
                flavor="stream",
            )

            return self._camelot_to_dataframe(
                camelot_tables
            )

        except Exception as exc:

            logger.warning(
                "Camelot Stream failed: %s",
                exc,
            )

            return []

    # ---------------------------------------------------------
    # pdfplumber Fallback
    # ---------------------------------------------------------

    def _extract_with_pdfplumber(
        self,
        pdf_path: Path,
    ) -> List[pd.DataFrame]:

        extracted_tables = []

        try:

            with pdfplumber.open(pdf_path) as pdf:

                for page in pdf.pages:

                    page_tables = page.extract_tables()

                    for table in page_tables:

                        if not table:
                            continue

                        df = pd.DataFrame(table)

                        if df.empty:
                            continue

                        df.columns = df.iloc[0]

                        df = df.iloc[1:].reset_index(
                            drop=True
                        )

                        df = clean_dataframe(df)

                        df = self._trim_table(df)

                        if df.empty:
                            continue

                        extracted_tables.append(df)

        except Exception as exc:

            logger.warning(
                "pdfplumber extraction failed: %s",
                exc,
            )

        return extracted_tables
    
        # ---------------------------------------------------------
    # Camelot Helper
    # ---------------------------------------------------------

    def _camelot_to_dataframe(
        self,
        camelot_tables,
    ) -> List[pd.DataFrame]:
        """
        Convert Camelot tables into cleaned DataFrames.
        """

        extracted_tables = []

        for table in camelot_tables:

            try:

                df = table.df

                if df.empty:
                    continue

                # First row becomes header
                df.columns = df.iloc[0]

                df = df.iloc[1:].reset_index(drop=True)

                df = clean_dataframe(df)

                # Remove surrounding non-tabular content
                df = self._trim_table(df)

                if df.empty:
                    continue

                extracted_tables.append(df)

            except Exception as exc:

                logger.warning(
                    "Skipping invalid table: %s",
                    exc,
                )

        return extracted_tables

    # ---------------------------------------------------------
    # Table Cleanup
    # ---------------------------------------------------------

    def _trim_table(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Remove page titles, narrative text and footer text.

        This improves Camelot Stream extraction for
        borderless tables (e.g. doc_02).
        """

        if df.empty:
            return df

        df = df.reset_index(drop=True)

        # --------------------------------------------
        # Find the actual table header
        # --------------------------------------------

        header_keywords = {
            "vendor",
            "invoice",
            "date",
            "amount",
            "status",
        }

        header_index = None

        for idx in range(len(df)):

            values = [
                str(v).strip().lower()
                for v in df.iloc[idx].tolist()
                if str(v).strip()
            ]

            matches = sum(
                keyword in values
                for keyword in header_keywords
            )

            if matches >= 3:

                header_index = idx

                break

        # --------------------------------------------
        # Trim everything above the table
        # --------------------------------------------

        if header_index is not None:

            df.columns = df.iloc[header_index]

            df = (
                df.iloc[header_index + 1 :]
                .reset_index(drop=True)
            )

        # --------------------------------------------
        # Remove footer rows
        # --------------------------------------------

        footer_keywords = [

            "footer",

            "note",

            "ignore",

            "reconciliation",

            "narrative",

        ]

        keep_rows = []

        for _, row in df.iterrows():

            text = " ".join(
                str(value).lower()
                for value in row.tolist()
            )

            if any(
                keyword in text
                for keyword in footer_keywords
            ):
                break

            keep_rows.append(row)

        if keep_rows:

            df = pd.DataFrame(
                keep_rows,
                columns=df.columns,
            )

        df = clean_dataframe(df)

        return df