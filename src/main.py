"""
main.py

Entry point for the PDF Table Extraction application.

Usage:
    python src/main.py --input ./input --output ./output
"""

import argparse
from pathlib import Path

from detector import PDFDetector, PDFType
from exporter import TableExporter
from extractor import TableExtractor
from logger import get_logger
from merger import TableMerger
from ocr import OCRTableExtractor
from utils import (
    create_output_directories,
    get_pdf_files,
)

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Extract tables from PDF documents."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input directory containing PDF files.",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output directory.",
    )

    return parser.parse_args()


def process_document(
    pdf_path: Path,
    detector: PDFDetector,
    extractor: TableExtractor,
    ocr_extractor: OCRTableExtractor,
    merger: TableMerger,
    exporter: TableExporter,
) -> None:
    """
    Process a single PDF document.
    """

    logger.info("=" * 80)
    logger.info("Processing document: %s", pdf_path.name)

    pdf_type = detector.detect(pdf_path)

    logger.info("Detected PDF Type: %s", pdf_type.value)

    # -----------------------------
    # Extract Tables
    # -----------------------------

    if pdf_type == PDFType.DIGITAL:

        tables = extractor.extract(pdf_path)

    else:

        tables = ocr_extractor.extract(pdf_path)

    logger.info(
        "Extracted %d table(s).",
        len(tables),
    )

    # -----------------------------
    # Merge Multi-page Tables
    # -----------------------------

    tables = merger.merge(tables)

    logger.info(
        "Final logical tables: %d",
        len(tables),
    )

    # -----------------------------
    # Export Results
    # -----------------------------

    exporter.export(
        pdf_path,
        tables,
    )

    logger.info(
        "Completed: %s",
        pdf_path.name,
    )


def main() -> None:
    """
    Application entry point.
    """

    args = parse_arguments()

    create_output_directories(
        args.output,
    )

    pdf_files = get_pdf_files(
        args.input,
    )

    if not pdf_files:

        logger.warning(
            "No PDF files found in %s",
            args.input,
        )

        return

    detector = PDFDetector()

    extractor = TableExtractor()

    ocr_extractor = OCRTableExtractor()

    merger = TableMerger()

    exporter = TableExporter(
        args.output,
    )

    logger.info("=" * 80)
    logger.info("PDF Table Extraction Started")
    logger.info("Input Directory : %s", args.input)
    logger.info("Output Directory: %s", args.output)
    logger.info("Documents Found : %d", len(pdf_files))
    logger.info("=" * 80)

    success = 0
    failed = 0

    for pdf_path in pdf_files:

        try:

            process_document(
                pdf_path=pdf_path,
                detector=detector,
                extractor=extractor,
                ocr_extractor=ocr_extractor,
                merger=merger,
                exporter=exporter,
            )

            success += 1

        except Exception as exc:

            logger.exception(
                "Failed processing %s: %s",
                pdf_path.name,
                exc,
            )

            failed += 1

    logger.info("=" * 80)
    logger.info("Processing Complete")
    logger.info("Successful Documents : %d", success)
    logger.info("Failed Documents     : %d", failed)
    logger.info("=" * 80)


if __name__ == "__main__":
    main()