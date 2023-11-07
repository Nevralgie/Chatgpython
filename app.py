from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Define your Azure Blob Storage account and container information
account_url = "https://trenstoragetrain.blob.core.windows.net"
container_name = "test104"

# Create the BlobServiceClient object with Azure DefaultAzureCredential
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url, credential=credential)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        filename = file.filename

        try:
            # Create a BlobClient for the specified container and file name
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

            # Upload the file to Azure Blob Storage
            with file.stream as data:
                blob_client.upload_blob(data, overwrite=True)

            return 'File successfully uploaded to Azure Blob Storage'
        except Exception as e:
            return f'Error uploading file: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True, port=8000)
