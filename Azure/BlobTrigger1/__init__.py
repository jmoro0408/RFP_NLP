import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import logging
import azure.functions as func
from ..HelperFuncs.tf_idf import tf_idf_main
from ..HelperFuncs.azure_read_api import read_main

def main(req: func.HttpRequest) -> func.HttpResponse: #pass pdf name to http
    logging.info('Python HTTP trigger function processed a request.')

    read_main(delete_after_process=False)
    results_json = tf_idf_main()
    logging.info("Processed results json")

    return results_json
