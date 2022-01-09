from tf_idf import get_txts, get_base_document_content, process_tfidf_similarity
from prepare_base_doc import prepare_base_doc, BASE_DOC_DIR
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
    if new_txts_analysed == 0:
        print("No new PDFs found")
    else:
        print(f"{new_txts_analysed} new text files added")


## Import document to be checked
# prepare_base_doc()


def tf_idf():
    """Creates document simililarity between base doc (to be compared) and corpus of existing texts.
    1. Import base doc txt file
    2. Concatenate with existing corpus of documents
    3. Output highest scoring documents through tf-idf algorith.
    """
    base_doc_txt = get_base_document_content(BASE_DOC_DIR)
    txt_df = get_txts(TEXT_DIR)
    process_tfidf_similarity(input_text_df=txt_df, base_document=base_doc_txt)


if __name__ == "__main__":
    check_missing_txts()
    prepare_base_doc()
    tf_idf()