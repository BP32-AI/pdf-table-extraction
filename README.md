# PDF Table Extraction

## Overview

This project extracts **only tabular data** from PDF documents while ignoring narrative text, headers, footers, and other non-tabular content.

The solution supports:

* Digital (text-based) PDFs
* Scanned PDFs using OCR (Tesseract)
* Multi-page table merging
* Export to JSON, CSV, and Excel

The implementation follows a modular architecture where each component has a single responsibility, making the solution easy to maintain and extend.

---

## Features

* Extract tables from digital PDFs using Camelot
* Fallback extraction using pdfplumber
* OCR support for scanned PDFs using Tesseract
* Automatic PDF type detection
* Merge multi-page tables into a single logical table
* Export extracted tables to:

  * JSON
  * CSV
  * Excel (.xlsx)
* Structured logging
* Modular and maintainable codebase

---

## Project Structure

```text
pdf-table-extraction/
│
├── input/
│   ├── doc_01.pdf
│   ├── doc_02.pdf
│   └── doc_03.pdf
│
├── output/
│   ├── json/
│   ├── csv/
│   └── excel/
│
├── src/
│   ├── __init__.py
│   ├── detector.py
│   ├── exporter.py
│   ├── extractor.py
│   ├── logger.py
│   ├── main.py
│   ├── merger.py
│   ├── ocr.py
│   └── utils.py
│
├── README.md
├── approach.md
├── requirements.txt
└── .gitignore
```

---

## Installation

### Clone Repository

```bash
git clone <repository_url>
cd pdf-table-extraction
```

### Create Virtual Environment

```bash
python3 -m venv venv
```

### Activate Virtual Environment

macOS / Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## System Requirements

The following tools must be installed.

### Tesseract OCR

macOS

```bash
brew install tesseract
```

Ubuntu

```bash
sudo apt install tesseract-ocr
```

### Ghostscript

Required by Camelot.

macOS

```bash
brew install ghostscript
```

Ubuntu

```bash
sudo apt install ghostscript
```

### Poppler

Required by pdf2image.

macOS

```bash
brew install poppler
```

Ubuntu

```bash
sudo apt install poppler-utils
```

---

## Running the Project

Place the input PDF files inside the `input` directory.

Execute:

```bash
python src/main.py --input ./input --output ./output
```

---

## Output

The generated files are stored inside:

```text
output/

├── json/
├── csv/
└── excel/
```

Each processed document produces:

* One JSON file
* One or more CSV files
* One Excel workbook

---

## Extraction Workflow

```
PDF
 │
 ▼
PDF Type Detection
 │
 ├───────────────┐
 │               │
 ▼               ▼
Digital      Scanned
 │               │
 ▼               ▼
Camelot      Tesseract OCR
 │               │
 ▼               ▼
pdfplumber (Fallback)
 │
 ▼
Table Cleaning
 │
 ▼
Multi-page Merge
 │
 ▼
JSON / CSV / Excel
```

---

## Technologies Used

* Python3
* Camelot
* pdfplumber
* OpenCV
* Tesseract OCR
* pdf2image
* Pandas
* OpenPyXL

---

## Assumptions

* Digital PDFs contain selectable text.
* Scanned PDFs are readable by Tesseract OCR.
* Multi-page tables have consistent column structures.
* Tables are represented in a structured format suitable for Camelot or pdfplumber.

---

## Limitations

* OCR accuracy depends on scan quality.
* Complex merged cells may not always be reconstructed perfectly.
* Highly irregular table layouts may require additional tuning.
* Automatic table title extraction is not implemented.

---

## Future Improvements

* Deep-learning-based table detection
* Cell-level confidence scoring
* Automatic table title extraction
* Better handling of merged cells
* Improved OCR table reconstruction
* Parallel processing for large PDF collections

---

## Deliverables

This repository contains:

* Source code
* README
* requirements.txt
* approach.md
* JSON outputs
* CSV outputs
* Excel outputs

---

## Author

**Brajendra Pateriya**
