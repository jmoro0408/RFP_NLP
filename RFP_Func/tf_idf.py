import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure_read import (start_storage_service_client,
                        start_container_client,
                        get_blob_url)


def prepare_processed_proposals(container_client, sas_token):
    processed_proposals_urls = get_blob_url(container_client, sas_token)
    _urls = [str(x) for x in processed_proposals_urls.values()]
    # create new dict with filename and text content rather than url
    _filenames_with_extension = [str(x) for x in processed_proposals_urls.keys()] #filenames of existing proposals with .txt extension
    _filenames = [os.path.splitext(x)[0] for x in _filenames_with_extension]
    proposal_content_dict = {}
    blob_list = container_client.list_blobs()
    print('===== Downloading processed proposal text =====')
    for fname, blob in zip(_filenames, blob_list):
        download_stream = container_client.download_blob(blob)
        content = download_stream.readall()
        content = str(content).replace("\n", "")
        proposal_content_dict[fname] = content

    return proposal_content_dict

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

def prepare_processed_rfp(container_client):
    pass


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


main()