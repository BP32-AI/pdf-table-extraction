# Approach

## Objective

The goal of this project is to extract **only tabular data** from PDF documents while ignoring narrative text, headers, footers, and other non-tabular content.

The solution supports:

* Digital (text-based) PDFs
* Scanned PDFs using OCR
* Multi-page tables
* Export to JSON, CSV, and Excel

---

# Solution Overview

The solution is divided into independent modules, where each module performs a single responsibility.

```text id="abkr2u"
PDF
 │
 ▼
PDF Type Detection
 │
 ├──────────────┐
 │              │
 ▼              ▼
Digital      Scanned
 │              │
 ▼              ▼
Camelot     Tesseract OCR
 │              │
 ▼              ▼
pdfplumber (Fallback)
 │
 ▼
Table Cleaning
 │
 ▼
Multi-page Merge
 │
 ▼
Export Results
```

---

# 1. PDF Type Detection

The first step determines whether the PDF is:

* Digital PDF
* Scanned PDF

The detector checks whether the document contains selectable text.

If text is found, the document is treated as a digital PDF.

Otherwise, the OCR pipeline is executed.

---

# 2. Digital PDF Processing

Digital PDFs are processed using multiple extraction strategies.

## Camelot (Lattice)

Lattice mode is used first because it works well with tables that contain visible borders.

Advantages:

* High accuracy
* Preserves rows and columns
* Handles structured tables efficiently

---

## Camelot (Stream)

If Lattice mode fails, Stream mode is used.

Stream mode is suitable for borderless tables where columns are aligned using whitespace.

---

## pdfplumber Fallback

If Camelot is unable to extract any tables, pdfplumber is used as a fallback.

This improves compatibility across different PDF layouts.

---

# 3. Scanned PDF Processing

Scanned PDFs are processed using OCR.

Pipeline:

```text id="8e0wh8"
PDF

↓

pdf2image

↓

OpenCV preprocessing

↓

Tesseract OCR

↓

Table reconstruction

↓

DataFrame
```

OpenCV preprocessing improves OCR quality by:

* Converting images to grayscale
* Applying Gaussian blur
* Applying binary thresholding

OCR text is extracted using Tesseract and reconstructed into rows based on text coordinates.

---

# 4. Table Cleaning

Some extraction methods may include surrounding page content.

To improve extraction quality, additional cleaning is performed.

The cleaning process removes:

* Document titles
* Narrative paragraphs
* Footer notes
* Empty rows
* Non-tabular content

Only the actual table is preserved before exporting.

---

# 5. Multi-page Table Merging

Some documents contain tables spanning multiple pages.

The merger compares consecutive tables based on:

* Number of columns
* Column names

If both match, the tables are combined into a single logical table.

This prevents duplicate headers and produces a continuous table in the final output.

---

# 6. Export

The extracted tables are exported into three formats.

## JSON

Used for structured machine-readable output.

Contains:

* Document ID
* Table ID
* Column names
* Table rows

---

## CSV

Each table is exported as an individual CSV file.

---

## Excel

Each document is exported as a single Excel workbook.

Each extracted table is written to a separate worksheet.

---

# Design Decisions

The implementation follows a modular architecture.

Each module has a single responsibility.

| Module       | Responsibility                   |
| ------------ | -------------------------------- |
| detector.py  | Detect PDF type                  |
| extractor.py | Extract tables from digital PDFs |
| ocr.py       | Extract tables from scanned PDFs |
| merger.py    | Merge multi-page tables          |
| exporter.py  | Export JSON, CSV, and Excel      |
| utils.py     | Helper functions                 |
| logger.py    | Logging                          |

This structure makes the project easier to maintain and extend.

---

# Challenges

During development, several challenges were encountered.

### Borderless Tables

Camelot Stream sometimes extracted surrounding narrative text along with the table.

This was addressed by adding a cleaning step that removes non-tabular content before exporting.

---

### Multi-page Tables

Tables split across multiple pages required detecting identical column structures before merging.

---

### OCR Accuracy

OCR quality depends on scan quality and image resolution.

Basic preprocessing was added to improve text recognition before table reconstruction.

---

# Assumptions

* Digital PDFs contain selectable text.
* Scanned PDFs are readable by Tesseract OCR.
* Multi-page tables maintain a consistent column structure.
* Tables are rectangular enough to be reconstructed into rows and columns.

---

# Limitations

The current implementation has the following limitations:

* Complex merged cells may not always be reconstructed correctly.
* OCR accuracy depends on image quality.
* Automatic table title detection is not implemented.
* Highly irregular table layouts may require additional tuning.

---

# Future Improvements

Possible future enhancements include:

* Deep learning-based table detection
* Automatic table title extraction
* Cell-level confidence scoring
* Better merged-cell reconstruction
* Parallel processing for large PDF collections
* Improved OCR table reconstruction for complex layouts

---

# Conclusion

The implemented solution satisfies the assignment requirements by:

* Extracting only tables
* Supporting digital and scanned PDFs
* Handling multi-page tables
* Ignoring non-tabular content
* Exporting JSON, CSV, and Excel outputs

The modular design keeps the solution simple, maintainable, and easy to extend.
