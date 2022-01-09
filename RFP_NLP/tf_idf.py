"""Module to house main tf-idf (term frequency inverse document frequency) algorithm
"""

from pathlib import Path
from typing import Union
import itertools
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_txts(path: Union[Path, str]) -> dict:
    """Function to read in all text files in a given directory and return a dict of their
    title and content, stripped of newlines.

    Args:
        path (Union[Path, str]): Directory of txt files.

    Returns:
        dict: Dictionary housing the txt file title and content as key-value pairs.
    """
    path = Path(path)
    file_token_dict = {}
    txt_list = [
        p for p in path.rglob("*") if p.is_file() and p.match("*.txt")
    ]  # list of all txt documents in dir, in PosixPath format.
    txt_titles = [
        Path(text).stem for text in txt_list
    ]  # grab the titles, with no parent path or file extension
    # iterate through list of txts, read the file and grab the content,
    # and attach the conen twith the title to a dict
    for txt_file, title in zip(txt_list, txt_titles):
        if title not in file_token_dict:  # only reads items that haven't been added
            with open(txt_file, "r", encoding="utf-8") as file:
                content = file.read().replace("\n", "")
                file_token_dict[title] = content
    return file_token_dict


def get_base_document_content(base_doc_dir: Union[Path, str]) -> str:
    """Retrives the text content of the base document to be compared.

    Args:
        base_doc_dir (Union[Path, str]): Directory containing the base document text file.

    Returns:
        str: txt content of the base document.
    """
    base_doc_dir = Path(base_doc_dir)
    txt_list = [p for p in base_doc_dir.rglob("*") if p.is_file() and p.match("*.txt")]
    assert (
        len(txt_list) == 1
    ), "Please ensure only one file is being provided for comparison"
    txt_file = txt_list[0]
    with open(txt_file, encoding="utf-8") as file:
        data = file.read().replace("\n", "")
    return data


def take(num, iterable):
    "Return first n items of the iterable as a list"
    return list(itertools.islice(iterable, num))


def process_tfidf_similarity(
    input_text_dict: dict, base_document: str, top_n_docs: int = 10
) -> dict:
    """Function to undertake the tf-idf similirity processing.
    This function takes in a dictionary of documents to be compared against, with the format:
    {doc_title : doc_content}. It compares this to the base document content to be compared.
    The function uses the sci-kit learn implementation of tf-idf:
    (https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

    The function return a dictionary of the most similar documents, complete with their scores.
    The top N (currently set at 10) most similar documents are then printed, however the entire
    ditionary with all documents and scores are returned.

    Args:
        input_text_dict (dict): Dict with titles and content of documents to be compared against
        base_document str: text content of base document to be compared

    Returns:
        dict: dict of most sorted document similarity with format title : score
    """
    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")

    # input_txt_dict should be a dictionary containing documents to be compared against.
    # keys: inidividual document titles, values: individual document content
    doc_corpus = list(
        input_text_dict.values()
    )  # list of input_text_dict_values. Same length as input dict.
    # To make uniformed vectors, both documents need to be combined first.
    doc_corpus.insert(0, base_document)
    doc_corpus_title_slices = list(
        input_text_dict.keys()
    )  # Have to be able to slice in order to grab the title with the highest scoring index
    embeddings = vectorizer.fit_transform(doc_corpus)
    cosine_similarities = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
    score_df_dict = {}
    for i, score in enumerate(cosine_similarities):
        score_title = doc_corpus_title_slices[i]
        score_df_dict[score_title] = round(score, 5)

    sorted_score_dict = dict(
        sorted(score_df_dict.items(), key=lambda item: item[1], reverse=True)
    )
    top_n_scores = {
        k: sorted_score_dict[k] for k in list(sorted_score_dict)[:top_n_docs]
    }

    pprint(f"Highest scoring documents are score are: {top_n_scores}")
    return sorted_score_dict
