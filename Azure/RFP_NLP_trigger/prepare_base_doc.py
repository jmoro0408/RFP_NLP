"""Module to prepare the base document for comparison.
In this context the base document is the documne that is being used for comparison.
This file identifies the pdf to be compared (from the directory specified in doc_locations.py) and
extracts the text, cleans the text, and saves it in the same directory.
"""


from pathlib import Path
from text_extract import extract_text_from_pdf, save_txt_file, remove_breaks_and_dedent
from doc_locations import DOC_TO_COMPARE_DIR


def prepare_base_doc():
    """See module docstring."""
    pdf_list = [
        p for p in DOC_TO_COMPARE_DIR.rglob("*") if p.is_file() and p.match("*.pdf")
    ]
    doc_to_compare = pdf_list[0]
    print(f"File to be compared: {Path(doc_to_compare).stem}.")
    extracted_text = extract_text_from_pdf(doc_to_compare)
    extracted_text = remove_breaks_and_dedent(extracted_text)
    save_txt_file(
        extracted_text, Path(doc_to_compare).stem, Path(doc_to_compare.parent)
    )
