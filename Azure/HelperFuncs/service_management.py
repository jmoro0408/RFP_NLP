"""Module to hold all the starter services.
Allows for creation of blob service, container, computer vision clients
and authentication of the microsoft OCR credentials
"""

from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

class ServiceManagement:
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
