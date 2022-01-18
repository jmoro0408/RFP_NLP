import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure_read import (start_storage_service_client,
                        start_container_client,
                        get_blob_url)


def prepare_processed_proposals(container_client, sas_token):
    processed_proposals_urls = get_blob_url(container_client, sas_token)
    return processed_proposals_urls



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
    print(prepare_processed_proposals(processed_proposal_container_client, storage_sas_token))

main()