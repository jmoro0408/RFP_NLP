import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import logging
import azure.functions as func
from ..HelperFuncs.tf_idf import tf_idf_main
from ..HelperFuncs.azure_read_api import read_main


def main(myblob: func.InputStream, outputblob: func.Out[str]):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    read_main()
    results_json = tf_idf_main()
    outputblob.set(results_json)
    logging.info("Processed results json")



