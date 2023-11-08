from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Define your Azure Key Vault URL and secret name
keyvault_url = "https://trkvara.vault.azure.net"
secret_name = "webappcs"

# Retrieve the connection string from Azure Key Vault
connection_string = get_connection_string_from_keyvault(keyvault_url, secret_name)

# Define your Azure Blob Storage account and container information
connection_string = "DefaultEndpointsProtocol=https;AccountName=trenstoragetrain;AccountKey=Ejuv1L7PhgAzydfcDietIOv8dBejza1kuXqprTp/wycOeZcHnJlXCZNWOmPA/JCxFoqGiblRag6x+ASttCA8aw==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = "test104"

def get_connection_string_from_keyvault(keyvault_url, secret_name):
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=keyvault_url, credential=credential)
    secret = secret_client.get_secret(secret_name)
    return secret.value
    
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
            # Get a blob client
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)

            # Upload the file to Azure Blob Storage
            with file.stream as data:
                blob_client.upload_blob(data, overwrite=True)

              # Generate a SAS (Shared Access Signature) token for the blob
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=container_name,
                blob_name=filename,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1)  # Adjust the expiration time by replacing the value of hours
            )

            # Build the temporary download link
            sas_url = f"{blob_client.url}?{sas_token}"

            return f'File successfully uploaded to Azure Blob Storage. Temporary link: <a href="{sas_url}">Download</a>'
        except Exception as e:
            return f'Error uploading file: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)
