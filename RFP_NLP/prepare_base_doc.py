from pathlib import Path
from typing import Union
from text_extract import extract_text, save_txt_file, remove_breaks_and_dedent

BASE_DOC_DIR = Path(
    r"RFP_NLP/data/proposals/doc_to_compare/20_Jacobs Bissell Point Fine Screen Project 12548.pdf"
)

if __name__ == "__main__":
    extracted_text = extract_text(BASE_DOC_DIR)
    extracted_text = remove_breaks_and_dedent(extracted_text)
    save_txt_file(extracted_text, Path(BASE_DOC_DIR).stem, Path(BASE_DOC_DIR.parent))
