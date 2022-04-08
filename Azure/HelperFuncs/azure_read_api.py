"""
Module to utilise the azure computer vision OCR function for PDFs.
Also contains general functions used to access blob storage and generally interact with Azure.
Within the RFP_NLP project this module handles the text extraction form the base doc (rfp) and
saving to a seperate blob.


Note, several clients are started through this func and their naming can be somewhat confusing.
The storage service client refers to the most upper level storage, in which individual
containers are housed.
The container client refers to individual containers which house individual files (blobs).
The blob client refers to individial files within containers.

I'm not sure if this naming is consistent with Microsoft, but it has worked for me.
"""
import time
import sys
import os
from typing import Dict
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


def start_storage_service_client(connection_str: str) -> BlobServiceClient:
    """Start a client assosciated with a blob storage account.

    Args:
        connection_str (str): Connection string assosciated with the account.
        Obtained from Azure Portal.

    Returns:
        BlobServiceClient: Started blob service client.
    """
    return BlobServiceClient.from_connection_string(connection_str)


def start_container_client(
    blob_name: str, blobserviceclient: BlobServiceClient
) -> ContainerClient:
    """Start a client assosciated with an individual storage account container.

    Args:
        blob_name (str): Name of blob to start client for
        blobserviceclient (BlobServiceClient): Blob storage account client (started).

    Returns:
        ContainerClient: Container client (started)
    """
    return blobserviceclient.get_container_client(blob_name)


def get_blob_url(
    container_client: ContainerClient, blob_sas_token: str
) -> Dict[str, str]:
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


def start_computervision_client(
    computer_vision_key: str, computer_vision_endpoint: str
) -> ComputerVisionClient:
    """Start a computer vision client instance

    Args:
        computer_vision_key (str): Computer vision key. Obtained from Azure Portal
        computer_vision_endpoint (str): Computer vision endpoint. Obtained from Azure Portal.

    Returns:
        ComputerVisionClient: Instance of computer vision client (started)
    """
    return ComputerVisionClient(
        computer_vision_endpoint, CognitiveServicesCredentials(computer_vision_key)
    )


def call_read_api(blob_url: str, computervision_client: ComputerVisionClient):
    """Callcs the computer vision API on an uploaded PDF.
    This func takes a url of  apdf located in blob storage as an arument. It then processes
    this using optical character recognition and returns the text.

    Args:
        blob_url (str): direct URL of PDF to be analysed. Will likely need the SAS token appended
        depending on your auth settings
        computervision_client (ComputervisionClient): Computer vision client instance (started)

    Returns:
        str: Text extracted from PDF at blob_url
    """
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
    read_result: str,
    save_filename: str,
    local: bool = True,
    upload_container_client=None,
):
    """Saves a read result either locally on uploads to a blob container.

    Args:
        read_result (str): Tex tto be saved.
        save_filename (str): Name of file to be saved
        local (bool, optional): Save to local folder or not. If True, read_result
        is saved to the same folder as this .py file. Defaults to True.

        upload_container_client (ContainerClient, optional):
        Required if local=False. Container Client instance assosciated with the contianer the
        read result is to be saved to. Defaults to None.
    """
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
                f"File {save_filename} successfully saved to \
                    {upload_container_client.container_name}"
            )


def upload_to_container(container_client: ContainerClient, filename: str):
    """Uploads a file to a given container

    Args:
        container_client (ContainerClient): ContainerClient Instance assosciated with the container
        the file is to be saved to.
        filename (str): file name of file to be uploaded.
    """

    print(f"======= Uploading to {container_client.container_name} container =======")
    with open(filename, "rb") as upload_data:
        container_client.upload_blob(name=filename, data=upload_data)
    print(f"File {filename} successfully saved to {container_client.container_name}")


def prepare_rfp_file(container_client: ContainerClient, sas_token: str):
    """Func is specific to this RFP application.
    Get the direct url to the rfp to be analysed

    Args:
        container_client (ContainerClient): ContainerClient Instance assosciated with the container
        housing the rfp to be analysed.
        sas_token (str): sas token of the PDF file. Obtained from Azure Portal.

    Returns:
        tuple: (rfp direct url, rfp filename)
    """
    raw_rfp_url = list(get_blob_url(container_client, sas_token).values())[0]
    raw_rfp_filename = list(get_blob_url(container_client, sas_token).keys())[0]
    raw_rfp_filename = os.path.splitext(raw_rfp_filename)[0] + ".txt"
    return raw_rfp_url, raw_rfp_filename


def delete_blob(container_client: ContainerClient, blob_name: str):
    """Delete a blob.

    Args:
        container_client (ContainerClient): ContainerClient Instance assosciated with the container
        housing the blob to be deleted.
        blob_name (str): blob name to be deleted.
    """
    if os.path.splitext(blob_name)[1] != ".pdf":
        blob_name = os.path.splitext(blob_name)[0] + ".pdf"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()
    print(f"{blob_name} deleted from {container_client.container_name}")


def read_main(delete_after_process: bool = True):
    """Main function. Loads secret keys and endpoints from environment variable and called
    the above functions to process an uploaded RFP.
    The func takes an uploaded RFP, extracts the text, saves the text in a new container,
    and, depending on the delete_after_process argument, deletes the original RFP PDF.

    ** Arguments **
    delete_after_process (bool): Deletes the uploaded RFP from the raw_rfp folder after procesing.
    Typically True to avoid the container filling up with old RFPs.

    """
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
    if delete_after_process:
        delete_blob(raw_rfp_container_client, raw_rfp_filename)


if __name__ == "__main__":
    read_main(delete_after_process=True)
