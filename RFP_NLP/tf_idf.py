from pathlib import Path
from typing import Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import itertools
from pprint import pprint


def get_txts(path: Union[Path, str]) -> list:
    path = Path(path)
    file_token_dict = {}
    txt_list = [
        p for p in path.rglob("*") if p.is_file() and p.match("*.txt")
    ]  # list of all txt documents in dir, in PosixPath format.
    txt_titles = [
        Path(text).stem for text in txt_list
    ]  # grab the titles, with no parent path or file extension
    # iterate through list of txts, read the file and grab the content, and attach the conen twith the title to a dict
    for txt_file, title in zip(txt_list, txt_titles):
        if (
            title not in file_token_dict.keys()
        ):  # only reads items that haven't been added
            with open(txt_file, "r") as file:
                content = file.read().replace("\n", "")
                file_token_dict[title] = content
    return file_token_dict


def get_base_document_content(base_doc_dir):
    base_doc_dir = Path(base_doc_dir)
    txt_list = [p for p in base_doc_dir.rglob("*") if p.is_file() and p.match("*.txt")]
    assert (
        len(txt_list) == 1
    ), "Please ensure only one file is being provided for comparison"
    txt_file = txt_list[0]
    with open(txt_file) as f:
        data = f.read().replace("\n", "")
    return data


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(itertools.islice(iterable, n))


def process_tfidf_similarity(input_text_dict, base_document):
    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")

    # input_txt_dict should be a dictionary containing documents to be compared against. keys: inidividual document titles, values: individual document content
    doc_corpus = list(
        input_text_dict.values()
    )  # list of input_text_dict_values. Same length as input dict.
    doc_corpus_combined = list(
        itertools.chain.from_iterable(doc_corpus)
    )  # flattening list
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
    n_scores = 10
    top_n_scores = {k: sorted_score_dict[k] for k in list(sorted_score_dict)[:n_scores]}

    pprint(f"Highest scoring documents are score are: {top_n_scores}")
    return sorted_score_dict
