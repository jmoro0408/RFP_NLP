from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from pathlib import Path
from text_extract import TEXT_DIR
from typing import Union
import pandas as pd
from scipy.sparse import hstack, vstack, csr_matrix

file_token_dict = {}


def get_txts(path: Union[Path, str]) -> list:
    txt_list = [p for p in path.rglob("*") if p.is_file() and p.match("*.txt")]
    txt_list = [str(file) for file in txt_list]
    text_titles = [Path(text).stem for text in txt_list]
    return txt_list, text_titles


def tokenize(txt_file):
    tfidf_vectorizer = TfidfVectorizer(input="filename", stop_words="english")
    if not isinstance(txt_file, list):
        txt_file = [txt_file]
    tfidf_vector = tfidf_vectorizer.fit_transform(txt_file)
    df_tfidf_sklearn = pd.DataFrame(
        tfidf_vector.toarray(), columns=tfidf_vectorizer.get_feature_names_out()
    )
    df_tfidf_sklearn = df_tfidf_sklearn.T
    return tfidf_vector, df_tfidf_sklearn


def add_to_tokens_dict(title, tfidf_vector):
    file_token_dict[title] = tfidf_vector
    return file_token_dict


def calculate_cosine_sim(matrix1, matrix2):
    return linear_kernel(matrix1, matrix2)


def compare_cosine(matrix1, matrix2):
    mising_length = abs(matrix1.shape[1] - matrix2.shape[1])
    if matrix1.shape[1] < matrix2.shape[1]:
        matrix1 = vstack((matrix2, csr_matrix((mising_length, matrix2.shape[1]))))
    elif matrix1.shape[1] < matrix2.shape[1]:
        matrix2 = vstack((matrix1, csr_matrix((mising_length, matrix1.shape[1]))))
    cosine_sim = calculate_cosine_sim(matrix1, matrix2)
    print(type(matrix1))
    return cosine_sim


if __name__ == "__main__":
    txts, titles = get_txts(TEXT_DIR)
    for txt, title in zip(txts, titles):
        if title in file_token_dict.keys():
            continue
        tfidf, tfidf_df = tokenize(txt)
        add_to_tokens_dict(title, tfidf)

temp_list = list(file_token_dict.keys())
# print(
#     calculate_cosine_sim(file_token_dict[temp_list[0]], file_token_dict[temp_list[1]])
# )
doc1 = file_token_dict[temp_list[0]]
doc2 = file_token_dict[temp_list[1]]
print(type(compare_cosine(doc1, doc2)))
