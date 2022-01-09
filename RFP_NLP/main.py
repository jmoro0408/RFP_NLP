from tf_idf import get_txts, get_base_document_content, process_tfidf_similarity
from prepare_base_doc import *
from pathlib import Path
from text_extract import (
    get_pdfs,
    PDF_DIR,
    TEXT_DIR,
    extract_text,
    save_txt_file,
    remove_breaks_and_dedent,
)


## Check analysed PDFs for any missing
#   -> Analyse any missing


def check_missing_txts():
    """Compares the PDF files current analysed against any new files that may have been added since last run.
    If a new PDF has been added, this will extract the text and save a new .txt file.
    """
    list_of_pdfs = get_pdfs(PDF_DIR)  # Get a list of all PDFS to be compared against
    list_of_txts = get_txts(TEXT_DIR)[
        "title"
    ].to_list()  # Get list of PDFs that have already been analysed
    new_txts_analysed = 0
    for pdf in list_of_pdfs:
        pdf_no_suffix = Path(pdf).stem
        if pdf_no_suffix not in list_of_txts:
            new_txt_file = extract_text(pdf)
            new_txt_file = remove_breaks_and_dedent(new_txt_file)
            save_txt_file(new_txt_file, Path(pdf).stem, TEXT_DIR)
            new_txts_analysed += 1
    print(f"{new_txts_analysed} new text file(s) added")


## Import document to be checked
#   -> Import PDF and output .txt

## Import new .txt file

## Concatenate document to be checked with corpus of documents

## Process similarity with existing corpus


if __name__ == "__main__":
    check_missing_txts()
