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
        content = content.read().replace("\n", "")
        proposal_content_dict[fname] = content

    return proposal_content_dict


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

    #start container client to hold raw rfps
    processed_proposals_dict = prepare_processed_proposals(processed_proposal_container_client, storage_sas_token)


main()