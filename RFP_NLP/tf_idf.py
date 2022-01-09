from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from text_extract import TEXT_DIR
from typing import Union
import pandas as pd
from prepare_base_doc import BASE_DOC_DIR


def get_txts(path: Union[Path, str]) -> list:
    file_token_dict = {}
    txt_list = [p for p in path.rglob("*") if p.is_file() and p.match("*.txt")]
    txt_list = [str(file) for file in txt_list]
    text_titles = [Path(text).stem for text in txt_list]
    for text, title in zip(txt_list, text_titles):
        if title not in file_token_dict.keys():
            with open(text) as f:
                lines = f.readlines()
                file_token_dict[title] = lines
    txt_df = pd.DataFrame.from_dict(file_token_dict, orient="index").reset_index()
    txt_df = txt_df.rename(columns={"index": "title", 0: "content"})
    return txt_df


def get_base_document_content(TEXT_DIR):
    TEXT_DIR = Path(TEXT_DIR.parent)
    txt_list = [p for p in TEXT_DIR.rglob("*") if p.is_file() and p.match("*.txt")]
    assert (
        len(txt_list) == 1
    ), "Please ensure only one file is being provided for comparison"
    txt_file = txt_list[0]
    with open(txt_file) as f:
        data = f.read()
    return data


def process_tfidf_similarity(input_text_df, base_document):
    corpus = input_text_df["content"].tolist()
    vectorizer = TfidfVectorizer(stop_words="english")
    # To make uniformed vectors, both documents need to be combined first.
    corpus.insert(0, base_document)
    embeddings = vectorizer.fit_transform(corpus)
    cosine_similarities = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
    highest_score = 0
    highest_score_index = 0
    for i, score in enumerate(cosine_similarities):
        if highest_score < score:
            highest_score = score
            highest_score_index = i

    most_similar_document_content = corpus[highest_score_index]
    most_similar_document_title = str(
        input_text_df[
            input_text_df["content"].str.contains(
                most_similar_document_content, case=False, regex=False
            )
        ]["title"]
    )
    print(
        f"Most similar document by TF-IDF:{most_similar_document_title}, with the score:{round(highest_score,3)}"
    )
