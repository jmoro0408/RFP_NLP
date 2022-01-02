from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from text_extract import TEXT_DIR
from typing import Union
import pandas as pd
from scipy.sparse import hstack, vstack, csr_matrix
from tabulate import tabulate

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


# def tokenize(text_df):
#     txt_content = text_df["content"]
#     # Create TfidfVectorizer object
#     vectorizer = TfidfVectorizer(stop_words="english")
#     # Generate matrix of word vectors
#     tfidf_matrix = vectorizer.fit_transform(txt_content)
#     # Print the shape of tfidf_matrix
#     print(f"tfidf matrix has a shape of {tfidf_matrix.shape}")
#     return tfidf_matrix


# def calculate_cosine_sim(matrix1, matrix2):
#     return linear_kernel(matrix1, matrix2)


# def compare_cosine(matrix1, matrix2):
#     mising_length = abs(matrix1.shape[1] - matrix2.shape[1])
#     if matrix1.shape[1] < matrix2.shape[1]:
#         matrix1 = vstack((matrix2, csr_matrix((mising_length, matrix2.shape[1]))))
#     elif matrix1.shape[1] < matrix2.shape[1]:
#         matrix2 = vstack((matrix1, csr_matrix((mising_length, matrix1.shape[1]))))
#     cosine_sim = calculate_cosine_sim(matrix1, matrix2)
#     print(type(matrix1))
#     return cosine_sim

def read_base_document(document_filepath):
        with open(document_filepath) as f:
            lines = f.readlines()
        return lines




def process_tfidf_similarity(input_text_df, base_document):
    corpus = list(input_text_df['content'])
	vectorizer = TfidfVectorizer()

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


	most_similar_document = corpus[highest_score_index]

	print("Most similar document by TF-IDF with the score:", most_similar_document, highest_score)



if __name__ == "__main__":
    txt_df = get_txts(TEXT_DIR)
    document_to_compare = read_base_document
    process_tfidf_similarity()

