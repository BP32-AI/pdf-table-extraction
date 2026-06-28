# src/merger.py
"""
merger.py

Merge tables that continue across multiple pages.

Two tables are merged when:

1. Column names match
2. Number of columns match

The merged output becomes a single logical table.
"""

from typing import List

import pandas as pd

from logger import get_logger

logger = get_logger(__name__)


class TableMerger:
    """
    Merge tables extracted from multiple pages.
    """

    def __init__(self):
        pass

    def merge(
        self,
        tables: List[pd.DataFrame]
    ) -> List[pd.DataFrame]:
        """
        Merge consecutive tables having the same structure.

        Parameters
        ----------
        tables : List[pandas.DataFrame]

        Returns
        -------
        List[pandas.DataFrame]
        """

        if not tables:
            return []

        logger.info(
            "Checking for multi-page tables..."
        )

        merged_tables = []

        current = tables[0].copy()

        for next_table in tables[1:]:

            if self._should_merge(
                current,
                next_table
            ):

                logger.info(
                    "Merged table with %d rows.",
                    len(next_table)
                )

                current = pd.concat(
                    [
                        current,
                        next_table
                    ],
                    ignore_index=True
                )

            else:

                merged_tables.append(current)

                current = next_table.copy()

        merged_tables.append(current)

        logger.info(
            "Total logical tables: %d",
            len(merged_tables)
        )

        return merged_tables

    # ----------------------------------------------------

    def _should_merge(
        self,
        table1: pd.DataFrame,
        table2: pd.DataFrame
    ) -> bool:
        """
        Decide whether two tables belong together.

        Conditions

        1. Same number of columns

        2. Same column names
        """

        if len(table1.columns) != len(table2.columns):

            return False

        columns1 = [
            str(col).strip().lower()
            for col in table1.columns
        ]

        columns2 = [
            str(col).strip().lower()
            for col in table2.columns
        ]

        return columns1 == columns2