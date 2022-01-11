"""Main file to undertake term frequency - inverse document frequency on
a number of PDFs and a base document to compare.
"""

from pathlib import Path
from tf_idf import get_txts, get_base_document_content, process_tfidf_similarity
from prepare_base_doc import prepare_base_doc
from doc_locations import DOC_TO_COMPARE_DIR, PDF_DIR, TEXT_DIR
from text_extract import (
    get_pdfs,
    extract_text_from_pdf,
    save_txt_file,
    remove_breaks_and_dedent,
)
#Azure function libraries
import logging
import azure.functions as func

## Check analysed PDFs for any missing
#   -> Analyse any missing


def check_missing_txts():
    """Compares the PDF files current analysed against any new files
    that may have been added since last run.
    If a new PDF has been added, this will extract the text and save a new .txt file.
    """
    list_of_pdfs = get_pdfs(PDF_DIR)  # Get a list of all PDFS to be compared against
    list_of_txts = list(
        get_txts(TEXT_DIR).keys()
    )  # Get list of PDFs that have already been analysed
    new_txts_analysed = 0
    for pdf in list_of_pdfs:
        pdf_no_suffix = Path(pdf).stem
        if pdf_no_suffix not in list_of_txts:
            new_txt_file = extract_text_from_pdf(pdf)
            new_txt_file = remove_breaks_and_dedent(new_txt_file)
            save_txt_file(new_txt_file, Path(pdf).stem, TEXT_DIR)
            new_txts_analysed += 1
    if new_txts_analysed == 0:
        print("No new PDFs found.")
    else:
        print(f"{new_txts_analysed} new text files added.")


## Import document to be checked
# prepare_base_doc()


def tf_idf():
    """Creates document simililarity between base doc (to be compared)
    and corpus of existing texts.
    1. Import base doc txt file
    2. Concatenate with existing corpus of documents
    3. Output highest scoring documents through tf-idf algorith.
    """
    base_doc_txt = get_base_document_content(DOC_TO_COMPARE_DIR)
    comparison_txt_dict = get_txts(TEXT_DIR)
    document_similarity = process_tfidf_similarity(
        input_text_dict=comparison_txt_dict, base_document=base_doc_txt
    )
    return document_similarity


def main(req: func.HttpRequest) -> func.HttpResponse:
    # logging.info('Python HTTP trigger function processed a request.')

    # name = req.params.get('name')
    # if not name:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         name = req_body.get('name')

    # if name:
    #     return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    # else:
    #     return func.HttpResponse(
    #          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #          status_code=200
    #     )

    check_missing_txts()
    prepare_base_doc()
    tf_idf()
