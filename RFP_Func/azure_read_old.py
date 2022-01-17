import os
from dotenv import load_dotenv
import os
from azure.storage.blob import (
    BlobServiceClient,
    __version__,
)

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from array import array
from PIL import Image
import sys
import time

load_dotenv()  # take environment variables from .env.

blob_key = os.getenv('BLOB_KEY')
blob_sas_token = os.getenv('BLOB_SAS_TOKEN')
blob_connect_str = os.getenv('BLOB_CONNECT_STR')
vision_key = os.getenv('COMPUTER_VISION_KEY')
vision_endpoint = os.getenv('COMPUTER_VISION_ENDPOINT')

# Create the BlobServiceClient object which will be used to get the container_client
blob_service_client = BlobServiceClient.from_connection_string(blob_connect_str)
print(type(blob_service_client))
# Container client for raw container.
raw_container_client = blob_service_client.get_container_client("raw-proposal")
rfp_raw_container_client = blob_service_client.get_container_client("raw-rfp")
# Container client for processed container
processed_container_client = blob_service_client.get_container_client("processed-proposal")
# Get base url for container.
proposal_raw_UrlBase = raw_container_client.primary_endpoint
rfp_raw_Urlbase = rfp_raw_container_client.primary_endpoint
print(proposal_raw_UrlBase)
print("\nProcessing blobs...")
blob_list = rfp_raw_container_client.list_blobs()

computervision_client = ComputerVisionClient(vision_endpoint, CognitiveServicesCredentials(vision_key))

#Download blobs
for idx, blob in enumerate(blob_list):
    if idx ==0: #just try the one for now
        print(blob.name)
        blob_filename = str(blob.name).replace(".pdf", "")
        blob_url = rfp_raw_Urlbase + "/" + blob.name + "?" + blob_sas_token
        '''
        OCR: Read File using the Read API, extract text - remote
        This example will extract text in an image, then print results, line by line.
        This API call can also extract handwriting style text (not shown).
        '''
        print("===== Read File - remote =====")
        # Get an image with text

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

        # Print the detected text, line by line
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                with open(f'{blob_filename}.txt', 'w') as f:
                   for line in text_result.lines:
                       f.write(f'{line.text}\n')
