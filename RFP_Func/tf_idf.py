import os
import json
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure_read import (start_storage_service_client,
                        start_container_client,
                        get_blob_url)


def prepare_content_dict(container_client):
    content_dict = {}
    blob_list = container_client.list_blobs()
    print(f'===== Downloading {container_client.container_name} text =====')
    for blob in blob_list:
        download_stream = container_client.download_blob(blob)
        content = download_stream.readall()
        content = str(content).replace("\n", "")
        fname = os.path.splitext(blob.name)[0]
        content_dict[fname] = content
    return content_dict

def read_stopwords(stopwords_dir):
    with open(stopwords_dir) as f:
        lines = f.read().splitlines()
    return lines

def process_tfidf_similarity(
    input_text_dict: dict, base_document_dict: dict, stopwords:list, top_n_docs: int = 10,
) -> dict:
    """Function to undertake the tf-idf similirity processing.
    This function takes in a dictionary of documents to be compared against, with the format:
    {doc_title : doc_content}. It compares this to the base document content to be compared.
    The function uses the sci-kit learn implementation of tf-idf:
    (https://bit.ly/3nchURz)

    The function return a dictionary of the most similar documents, complete with their scores.
    The top N (currently set at 10) most similar documents are then printed, however the entire
    ditionary with all documents and scores are returned.

    Args:
        input_text_dict (dict): Dict with titles and content of documents to be compared against
        base_document (dict): dictionary containig filename and content of base document to be compared

    Returns:
        json: json of most sorted document similarity with format title : score
    """
    # Using the nltk stopwords corpus instead of the sklearn built in stopwords,
    # see https://bit.ly/3tdqsLQ for reasoning behind this

    vectorizer = TfidfVectorizer(stop_words=stopwords)

    # input_txt_dict should be a dictionary containing documents to be compared against.
    # keys: inidividual document titles, values: individual document content
    doc_corpus = list(
        input_text_dict.values()
    )  # list of input_text_dict_values. Same length as input dict.
    # To make uniformed vectors, both documents need to be combined first.
    base_document_content = list(base_document_dict.values())[0] #discarding filename of base doc
    doc_corpus.insert(0, base_document_content)
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

    top_scores_json = json.dumps(top_n_scores, indent = 4)
    pprint(
        f"Highest scoring documents are score are: {top_n_scores}"
    )
    return top_scores_json

def main():
    load_dotenv()
    storage_sas_token = os.getenv('STORAGE_SAS_TOKEN')
    storage_connect_str = os.getenv('STORAGE_CONNECT_STR')

    # Start service container for entie storage
    storage_service_client = start_storage_service_client(storage_connect_str)
    #start container client to hold processed rfps
    processed_rfp_container_client = start_container_client('processed-rfp', storage_service_client)
    #start container client to hold processed rfps
    processed_proposal_container_client = start_container_client('processed-proposal', storage_service_client)
    #create dict of processed proposals and their content
    processed_proposals_dict = prepare_content_dict(processed_proposal_container_client)
    #create dict of filename and content for processed rfp
    processed_rfp_dict = prepare_content_dict(processed_rfp_container_client)
    #Get stopwords for english
    nltk_stopwords = read_stopwords(os.path.join(os.getcwd(), 'english.txt'))
    #conduct tf_idf comparison
    documnet_similarity_json = process_tfidf_similarity(input_text_dict = processed_proposals_dict,
                            base_document_dict = processed_rfp_dict,
                            stopwords = nltk_stopwords)

if __name__ == "__main__":
    main()