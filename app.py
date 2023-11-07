from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from flask import Flask, request, render_template
import os

app = Flask(__name__)

def get_blob_service_client_account_key(self):
    # TODO: Replace <storage-account-name> with your actual storage account name
    account_url = "https://training-tr.blob.core.windows.net"
    shared_access_key = os.getenv("Ejuv1L7PhgAzydfcDietIOv8dBejza1kuXqprTp/wycOeZcHnJlXCZNWOmPA/JCxFoqGiblRag6x+ASttCA8aw==")
    credential = shared_access_key

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=credential)

    return blob_service_client

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        file.save(filename)
        blob_client = blob_service_client.get_blob_client(container = container, blob = filename)
        with open(filename, "rb") as data:
            blob_client.upload_blob(data=data, overwrite=True)
        return 'File successfully uploaded'
