import os
from dotenv import load_dotenv
from azure.storage.blob import (
    BlobServiceClient,
    __version__,
)

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import time


def start_storage_service_client(connection_str:str):
    return BlobServiceClient.from_connection_string(connection_str)

def start_container_client(blob_name:str, blobserviceclient):
    try:
         return blobserviceclient.get_container_client(blob_name)
    except NameError:
        print("Blob service client not found, \
            please ensure a service client instance is running")

def get_blob_url(container_client, blob_sas_token):
    """Returns a dictionary of blob urls for a particular container
        The url will point directly to the raw pdf

    Args:
        container_client ([type]): Azure container client instance
        blob_sas_token ([type]): sas token for the particular container

    Returns:
        dict: ditionary of blob names and their urls
    """
    endpoint = container_client.primary_endpoint
    blob_list = container_client.list_blobs()
    blob_url_dict = {}
    for blob in blob_list:
        blob_url = endpoint + "/" + blob.name + "?" + blob_sas_token
        blob_url_dict[blob.name] = blob_url
    return blob_url_dict


def start_computervision_client(computer_vision_key, computer_vision_endpoint):
    return ComputerVisionClient(computer_vision_endpoint, CognitiveServicesCredentials(computer_vision_key))

def call_read_api(blob_url, computervision_client):
    print("======= Starting Text Extraction =======")
    # Call API with URL and raw response (allows you to get the operation location)
    read_response = computervision_client.read(blob_url,  raw=True)
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]
    # Call the "GET" API and wait for it to retrieve the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)
    return read_result

def save_read_result(read_result, save_filename):
    # save the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            with open(save_filename, 'w') as f:
                for line in text_result.lines:
                    f.write(f'{line.text}\n')
        print(f'Extracted text saved as {save_filename}.txt')

def upload_to_container(container_client, filename):
    print(f'======= Uploading to {container_client.container_name} container =======')
    with open(filename, "rb") as upload_data:
        container_client.upload_blob(name = filename, data = upload_data)
    print(f'File {filename} successfully saved to {container_client.container_name}')

def main():
    load_dotenv()
    storage_sas_token = os.getenv('STORAGE_SAS_TOKEN')
    storage_connect_str = os.getenv('STORAGE_CONNECT_STR')
    vision_key = os.getenv('COMPUTER_VISION_KEY')
    vision_endpoint = os.getenv('COMPUTER_VISION_ENDPOINT')

    # Start service container for entie storage
    storage_service_client = start_storage_service_client(storage_connect_str)

    #start computer vision client instance
    computervision_client = start_computervision_client(vision_key, vision_endpoint)

    # get raw base doc (rfp) input
    raw_rfp_container_client = start_container_client('raw-rfp', storage_service_client)
    raw_rfp_url = list(get_blob_url(raw_rfp_container_client, storage_sas_token).values())[0]
    raw_rfp_filename = list(get_blob_url(raw_rfp_container_client, storage_sas_token).keys())[0]
    raw_rfp_filename = os.path.splitext(raw_rfp_filename)[0] + '.txt'

    #get raw rfp text
    #rfp_read_result = call_read_api(raw_rfp_url, computervision_client)

    #save extracted text
    #save_read_result(rfp_read_result, raw_rfp_filename)

    #upload to process rfp container
    processed_rfp_container_client = start_container_client('processed-rfp', storage_service_client)
    filepath = r'/Users/jamesmoro/Documents/Python/RFP_NLP/RFP_Func/sample.txt'
    upload_to_container(processed_rfp_container_client, raw_rfp_filename)

main()