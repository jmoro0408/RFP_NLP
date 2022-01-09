from pathlib import Path
from typing import Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


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


def process_tfidf_similarity(input_text_df, base_document):
    doc_corpus = input_text_df["content"].tolist()
    vectorizer = TfidfVectorizer(lowercase=True, max_df=0.8, stop_words="english")
    # To make uniformed vectors, both documents need to be combined first.
    doc_corpus.insert(0, base_document)
    embeddings = vectorizer.fit_transform(doc_corpus)
    cosine_similarities = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
    highest_score = 0
    highest_score_index = 0
    for i, score in enumerate(cosine_similarities):
        if highest_score < score:
            highest_score = score
            highest_score_index = i

    most_similar_document_content = doc_corpus[highest_score_index]
    most_similar_document_title = str(
        input_text_df[
            input_text_df["content"].str.contains(
                most_similar_document_content, case=False, regex=False
            )
        ]["title"]
    )
    print(
        f"Most similar document by TF-IDF:{most_similar_document_title}, \
        with the score:{round(highest_score,3)}"
    )


## Testing
TEXT_DIR = Path(r"RFP_NLP/data/proposals/text_only")

_test_df = get_txts(TEXT_DIR)

print("done")
