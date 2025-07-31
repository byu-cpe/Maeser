# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module is used to extract figures from a series of pdfs in a directory
It does this by looking for "Figure X.Y" in the text and extracting a screenshot of the page
cropped around this text.
This procedure is *very* rudimentary and could use much improvement.
This module can be executed in the terminal or used within another script.
"""

import sys
import os
import re
import pymupdf

def extract_figures_with_captions(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    figures_extracted = 0

    # Desired size in points (600x400 px @ 300 dpi)
    width_pt = 600  # 600px
    height_pt = 400  # 400px
    padding_pt = 16

    for page_index in range(len(doc)):
        page = doc[page_index]
        text_blocks = page.get_text("dict")["blocks"]

        for block in text_blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"]
                    match = re.match(r"(Figure\s+(\d+\.\d+))", text, re.IGNORECASE)
                    if match:
                        fig_label = match.group(2)
                        caption_rect = pymupdf.Rect(span["bbox"])
                        center_x = (caption_rect.x0 + caption_rect.x1) / 2
                        center_y = (caption_rect.y0 + caption_rect.y1) / 2

                        # Define fixed-size capture rectangle centered on the caption
                        x0 = center_x - (width_pt / 2 + padding_pt)
                        y0 = center_y - (height_pt + padding_pt)
                        x1 = center_x + (width_pt / 2 + padding_pt)
                        y1 = center_y + padding_pt
                        capture_rect = pymupdf.Rect(x0, y0, x1, y1)

                        pix = page.get_pixmap(clip=capture_rect, dpi=300)
                        image_name = f"{fig_label}.png"
                        image_path = os.path.join(output_dir, image_name)
                        pix.save(image_path)
                        print(f"Extracted {image_name}")
                        figures_extracted += 1
    return figures_extracted

# TODO: This system is flawed, since figures from the next pdf in the
# series will overwrite some or all of the figures from the pdf preceding it.
def extract_all_figures(target_dir: str):
    """Identifies all pdfs in **target_dir** and extracts all figures from that pdf.

    Args:
        target_dir (str): The directory containing the pdfs.
    """
    for filename in os.listdir(target_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(target_dir, filename)
            extract_figures_with_captions(pdf_path, target_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_figures.py <directory>")
        sys.exit(1)
    extract_all_figures(sys.argv[1])
