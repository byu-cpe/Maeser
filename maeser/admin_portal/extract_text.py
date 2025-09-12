# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module is used to extract text from pdfs in markdown format.
The resultant markdown is saved to the same directory where the pdfs are located.
This module can be executed in the terminal or used within another script.
"""

import sys
import os
import pathlib
import pymupdf4llm

def extract_pdf_text(dir: str, pdf: str):
    """Extracts pdf text in markdown format and saves the output to the pdf's directory.

    Args:
        dir (str): The directory where the pdf file is located.
        pdf (str): The name of the pdf, inlcuding the extension.
    """
    filename = os.path.splitext(pdf)[0]+".md"
    md_text = pymupdf4llm.to_markdown(
        doc=os.path.join(dir, pdf),
        show_progress=True,
    )
    pathlib.Path(os.path.join(dir, filename)).write_bytes(md_text.encode())

def extract_all_pdf_texts(dir: str):
    """Extracts text from all pdfs located in **dir**.

    Args:
        dir (str): The directory where the pdf files are located.
    """
    pdf_files = sorted([f for f in os.listdir(dir) if f.lower().endswith(".pdf")])
    for pdf in pdf_files:
        extract_pdf_text(dir, pdf)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_text.py <directory>")
        sys.exit(1)
    extract_all_pdf_texts(sys.argv[1])
