# src/exporter.py

"""
exporter.py

Export extracted tables into:

1. JSON
2. CSV
3. Excel

Output Structure

output/
    ├── json/
    ├── csv/
    └── excel/
"""

import json
from pathlib import Path
from typing import List

import pandas as pd

from logger import get_logger
from utils import (
    dataframe_columns,
    dataframe_to_rows,
    document_id,
    sanitize_filename,
)

logger = get_logger(__name__)


class TableExporter:
    """
    Export extracted tables.
    """

    def __init__(self, output_dir: Path):

        self.output_dir = output_dir

        self.json_dir = output_dir / "json"
        self.csv_dir = output_dir / "csv"
        self.excel_dir = output_dir / "excel"

    # ---------------------------------------------------------

    def export(
        self,
        pdf_path: Path,
        tables: List[pd.DataFrame],
    ) -> None:
        """
        Export all formats.

        Parameters
        ----------
        pdf_path : Path

        tables : List[pandas.DataFrame]
        """

        self.export_json(pdf_path, tables)

        self.export_csv(pdf_path, tables)

        self.export_excel(pdf_path, tables)

    # ---------------------------------------------------------

    def export_json(
        self,
        pdf_path: Path,
        tables: List[pd.DataFrame],
    ) -> None:
        """
        Export JSON according to assignment schema.
        """

        doc_id = document_id(pdf_path)

        output = {
            "document_id": doc_id,
            "tables": [],
        }

        for idx, df in enumerate(tables, start=1):

            table = {
                "table_id": idx,
                "page_start": 1,
                "page_end": 1,
                "title": "",
                "columns": dataframe_columns(df),
                "rows": dataframe_to_rows(df),
            }

            output["tables"].append(table)

        json_file = self.json_dir / f"{doc_id}_tables.json"

        with open(
            json_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                output,
                f,
                indent=4,
                ensure_ascii=False,
            )

        logger.info(
            "JSON exported: %s",
            json_file.name,
        )

    # ---------------------------------------------------------

    def export_csv(
        self,
        pdf_path: Path,
        tables: List[pd.DataFrame],
    ) -> None:
        """
        Export one CSV per table.
        """

        doc_id = document_id(pdf_path)

        for idx, df in enumerate(tables, start=1):

            filename = sanitize_filename(
                f"{doc_id}_table_{idx}.csv"
            )

            csv_file = self.csv_dir / filename

            df.to_csv(
                csv_file,
                index=False,
                encoding="utf-8",
            )

        logger.info(
            "%d CSV file(s) exported.",
            len(tables),
        )

    # ---------------------------------------------------------

    def export_excel(
        self,
        pdf_path: Path,
        tables: List[pd.DataFrame],
    ) -> None:
        """
        Export one Excel workbook.

        Each table becomes a separate worksheet.
        """

        doc_id = document_id(pdf_path)

        excel_file = (
            self.excel_dir /
            f"{doc_id}.xlsx"
        )

        with pd.ExcelWriter(
            excel_file,
            engine="openpyxl",
        ) as writer:

            for idx, df in enumerate(
                tables,
                start=1,
            ):

                sheet_name = f"Table_{idx}"

                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )

        logger.info(
            "Excel exported: %s",
            excel_file.name,
        )