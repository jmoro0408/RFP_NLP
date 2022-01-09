from pathlib import Path
from text_extract import extract_text_from_pdf, save_txt_file, remove_breaks_and_dedent
from doc_locations import DOC_TO_COMPARE_DIR


def prepare_base_doc():
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
