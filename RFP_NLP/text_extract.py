from pathlib import Path
from tika import parser
from typing import Union
import inspect

PDF_DIR = Path(r"/Users/jamesmoro/Documents/Python/RFP_NLP/RFP_NLP/data/proposals/raw")
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


def save_txt_file(
    extracted_text: str, fname: Union[Path, str], save_path: Union[Path, str]
):
    """output text as .txt file

    Args:
        extracted_text (str): text to write, extracted from target pdf
        fname (Union[Path, str]): target save path
    """
    fname = fname + ".txt"
    save_path = Path(save_path, fname)
    with open(str(save_path), "w") as f:
        f.write(extracted_text)
    print(f"Text saved as {fname}")


def remove_breaks_and_dedent(input_text: str) -> str:
    """removes newlines and trailing newlines from text, and removes indentation

    Args:
        input_text (str): raw string to have lines removed

    Returns:
        str: input text with lines removed
    """
    output_text = input_text.replace("\n", " ").replace("\r", "")
    output_text = inspect.cleandoc(output_text)  # removing indentation
    return output_text


def preprocess():
    pdf_list = get_pdfs(PDF_DIR)
    for file in pdf_list:
        if Path(file).exists():  # don't duplicate files that are already processed
            continue
        pdf_text = extract_text(file)
        pdf_text = remove_breaks_and_dedent(pdf_text)
        save_txt_file(pdf_text, Path(file).stem, TEXT_DIR)


if __name__ == "__main__":
    preprocess()
