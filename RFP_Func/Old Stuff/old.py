
response = requests.get(url)
my_raw_data = response.content
with BytesIO(my_raw_data) as data:
    read_pdf = PyPDF2.PdfFileReader(data)
    for page in range(read_pdf.getNumPages()):
        output  = (read_pdf.getPage(page).extractText())
        with open("Output.txt", "w") as text_file:
            text_file.write(output)



     response = requests.get(blob_url)
        my_raw_data = response.content
        with BytesIO(my_raw_data) as data:
            filepath = open(data,'r')
            # Async SDK call that "reads" the image
            response = computervision_client.read_in_stream(filepath, raw=True)
            # Don't forget to close the file
            filepath.close()

#         # Get ID from returned headers
#         operation_location = response.headers["Operation-Location"]
#         operation_id = operation_location.split("/")[-1]

#         # SDK call that gets what is read
#         while True:
#             result = computervision_client.get_read_result(operation_id)
#             if result.status.lower () not in ['notstarted', 'running']:
#                 break
#             print ('Waiting for result...')
#             time.sleep(10)
#         print(result)

#         # read_operation_location = read_response.headers["Operation-Location"]
#         # # Grab the ID from the URL
#         # operation_id = read_operation_location.split("/")[-1]

#         # # Call the "GET" API and wait for it to retrieve the results
#         # while True:
#         #     read_result = computervision_client.get_read_result(operation_id)
#         #     if read_result.status not in ['notStarted', 'running']:
#         #         break
#         #     time.sleep(1)

#         # # Print the detected text, line by line
#         # if read_result.status == OperationStatusCodes.succeeded:
#         #     for text_result in read_result.analyze_result.read_results:
#         #         for line in text_result.lines:
#         #             print(line.text)
#         #             print(line.bounding_box)
#         # print()

# # #Download blobs
# # for idx, blob in enumerate(blob_list):
# #     file_name = f'{blob.name}.pdf'
# #     filepath = Path("/Users/jamesmoro/Documents/Python/RFP_NLP/RFP_Func",file_name)
#     if idx == 0:
#         with open(filepath, "wb") as download_file:
#             download_file.write(raw_container_client.download_blob(blob).readall())