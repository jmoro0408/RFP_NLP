"""
Module to utilise the azure computer vision OCR function for PDFs.
Also contains general functions used to access blob storage and generally interact with Azure.
Within the RFP_NLP project this module handles the text extraction form the base doc (rfp) and
saving to a seperate blob.
"""

# TODO: Write docstrings
# TODO: The get_blob_url funciton is messy, I thinbk there is a way to generate sas tokens on the fly - should look into that

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


import os
import time
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials


def start_storage_service_client(connection_str: str):
    return BlobServiceClient.from_connection_string(connection_str)


def start_container_client(blob_name: str, blobserviceclient):
    return blobserviceclient.get_container_client(blob_name)


def get_blob_url(container_client, blob_sas_token):
    """
    Returns a dictionary of blob urls for a particular container
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
        if str(blob_sas_token).startswith("?"):
            blob_url = endpoint + "/" + blob.name + blob_sas_token
        else:
            blob_url = endpoint + "/" + blob.name + "?" + blob_sas_token
        blob_url_dict[blob.name] = blob_url
    return blob_url_dict


def start_computervision_client(computer_vision_key, computer_vision_endpoint):
    return ComputerVisionClient(
        computer_vision_endpoint, CognitiveServicesCredentials(computer_vision_key)
    )


def call_read_api(blob_url, computervision_client):
    print("======= Starting Text Extraction =======")
    # Call API with URL and raw response (allows you to get the operation location)
    read_response = computervision_client.read(blob_url, raw=True)
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]
    # Call the "GET" API and wait for it to retrieve the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ["notStarted", "running"]:
            break
        time.sleep(1)
    return read_result


def save_read_result(
    read_result, save_filename, local=True, upload_container_client=None
):
    # save the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        raw_text = []
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                raw_text.append(line.text)
        raw_text = "\n".join(raw_text)
        if local:
            with open(save_filename, "w", encoding="utf-8") as file:
                file.write(raw_text)
            print(f"Extracted text saved as {save_filename}")
        else:
            assert (
                upload_container_client is not None
            ), "If local is False, a suitable upload container client must be provided"
            print(
                f"======= Uploading to {upload_container_client.container_name} container ======="
            )
            upload_container_client.upload_blob(
                name=save_filename, data=raw_text, overwrite=True
            )
            print(
                f"File {save_filename} successfully saved to {upload_container_client.container_name}"
            )


def upload_to_container(container_client, filename):
    print(f"======= Uploading to {container_client.container_name} container =======")
    with open(filename, "rb") as upload_data:
        container_client.upload_blob(name=filename, data=upload_data)
    print(f"File {filename} successfully saved to {container_client.container_name}")


def prepare_rfp_file(container_client, sas_token):
    raw_rfp_url = list(get_blob_url(container_client, sas_token).values())[0]
    raw_rfp_filename = list(get_blob_url(container_client, sas_token).keys())[0]
    raw_rfp_filename = os.path.splitext(raw_rfp_filename)[0] + ".txt"
    return raw_rfp_url, raw_rfp_filename

def delete_blob(container_client, blob_name):
    if os.path.splitext(blob_name)[1] != '.pdf':
        blob_name = os.path.splitext(blob_name)[0] + '.pdf'
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()
    print(f'{blob_name} deleted from {container_client.container_name}')


def read_main():
    load_dotenv()
    storage_sas_token = os.getenv("STORAGE_SAS_TOKEN")
    storage_connect_str = os.getenv("STORAGE_CONNECT_STR")
    vision_key = os.getenv("COMPUTER_VISION_KEY")
    vision_endpoint = os.getenv("COMPUTER_VISION_ENDPOINT")

    # Start service container for entie storage
    storage_service_client = start_storage_service_client(storage_connect_str)

    # start container client to hold processed rfps
    processed_rfp_container_client = start_container_client(
        "processed-rfp", storage_service_client
    )


    # start container client to hold raw rfps
    raw_rfp_container_client = start_container_client("raw-rfp", storage_service_client)

    # start computer vision client instance
    computervision_client = start_computervision_client(vision_key, vision_endpoint)

    # get raw base doc (rfp) input
    raw_rfp_url, raw_rfp_filename = prepare_rfp_file(
        raw_rfp_container_client, storage_sas_token
    )

    # get raw rfp text
    rfp_read_result = call_read_api(raw_rfp_url, computervision_client)

    # save extracted text
    save_read_result(
        rfp_read_result,
        raw_rfp_filename,
        local=False,
        upload_container_client=processed_rfp_container_client,
    )

    delete_blob(raw_rfp_container_client, raw_rfp_filename)


# if __name__ == "__main__":
#     read_main()
