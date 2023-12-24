from __future__ import print_function

import os
import cloudmersive_convert_api_client
from cloudmersive_convert_api_client.rest import ApiException
from pprint import pprint
RESULT_FOLDER='backend_func/resulted_files'
UPLOAD_FOLDER='backend_func/uploaded_files'


configuration = cloudmersive_convert_api_client.Configuration()
configuration.api_key['Apikey'] = os.environ.get("APIKEY")

#configuration.api_key_prefix['Apikey'] = 'Bearer'

api_instance = cloudmersive_convert_api_client.ConvertDocumentApi(cloudmersive_convert_api_client.ApiClient(configuration))

def cloudmersive_convert(input_path, output_path):
    try:
        api_response = api_instance.convert_document_autodetect_to_pdf(input_path)
        #pprint(api_response)
        with open(output_path, 'wb') as output_file:
            output_file.write(api_response)
    except ApiException as e:
        print("Exception when calling ConvertDocumentApi->convert_document_autodetect_to_pdf: %s\n" % e)