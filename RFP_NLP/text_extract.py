from pathlib import Path
from tika import parser
from typing import Union

PROPOSAL_DIR = Path(
    r"/Users/jamesmoro/Documents/Python/RFP_NLP/RFP_NLP/data/proposals/raw"
)
TEXT_DIR = Path(r"RFP_NLP/data/proposals/text_only")


def get_pdfs(path: Path) -> list:
    """generated a list of all pdf files in given directory (recursive)

    Args:
        path (Path): pathlib.Path object of the folder directory

    Returns:
        list: list of pathlib.Path objects for all pdf files in given directory
    """

    pdf_list = [p for p in path.rglob("*") if p.is_file() and p.match("*.pdf")]
    return pdf_list


def extract_text(pdf_file: Union[Path, str]) -> str:
    """extract text from pdf using an apache tika python wrapper

    Args:
        pdf_file (Union[Path, str]): given pdf file location as either pathlib.Path object or raw string

    Returns:
        str: raw text from supplied pdf
    """
    parsedPDF = parser.from_file(str(pdf_file))
    pdf_content = parsedPDF["content"]
    return pdf_content


def save_txt_file(extracted_text):
    pass


if __name__ == "__main__":
    pdf_list = get_pdfs(PROPOSAL_DIR)
    extract_text(pdf_list[1])
