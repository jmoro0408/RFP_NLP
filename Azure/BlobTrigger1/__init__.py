import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import logging
import azure.functions as func
from ..HelperFuncs.tf_idf import tf_idf_main
from ..HelperFuncs.azure_read_api import read_main


def main(req: func.HttpRequest) -> func.HttpResponse: #pass pdf name to http
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')
    logging.info(f'name : {name} passed for processing')

    read_main()
    results_json = tf_idf_main()
    logging.info("Processed results json")
    return results_json
