# Imports
import os
from dotenv import load_dotenv
from PIL import Image
from pathlib import Path
from azure.storage.blob import (
    BlobServiceClient,
    __version__,
)

load_dotenv()  # take environment variables from .env.

blob_key = os.getenv('BLOB_KEY')
blob_sas_token = os.getenv('BLOB_SAS_TOKEN')
blob_connect_str = os.getenv('BLOB_CONNECT_STR')

# Create the BlobServiceClient object which will be used to get the container_client
blob_service_client = BlobServiceClient.from_connection_string(blob_connect_str)
# Container client for raw container.
raw_container_client = blob_service_client.get_container_client("raw-proposal")
# Container client for processed container
processed_container_client = blob_service_client.get_container_client("processed-proposal")
# Get base url for container.
proposal_raw_UrlBase = raw_container_client.primary_endpoint

print(proposal_raw_UrlBase)

print("\nProcessing blobs...")

blob_list = raw_container_client.list_blobs()

#Download blobs
for idx, blob in enumerate(blob_list):
    if idx ==0: #just try the one for now
        blob_url = proposal_raw_UrlBase + "/" + blob.name + "?" + blob_sas_token
