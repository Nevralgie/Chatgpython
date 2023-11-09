import hvac
#from azure.identity import DefaultAzureCredential
#from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from flask import Flask, request, render_template
import os

app = Flask(__name__)
    
def get_secret_from_vault(vault_url, vault_secret_path, service_principal_id, service_principal_secret, role):
    client = hvac.Client(url=vault_url)

    # Authenticate using service principal credentials and role
    client.auth.azure.login(
        url="https://login.microsoftonline.com/common",
        tenant_id="7349d3b2-951f-41be-877e-d8ccd9f3e73c",
        service_principal_id=service_principal_id,
        service_principal_secret=service_principal_secret,
        role=role
    )

    # Retrieve the secret from Vault
    secret_data = client.read(vault_secret_path)

    if secret_data and "data" in secret_data:
        return secret_data["data"]
    else:
        return None


# Replace with your actual service principal credentials and role
service_principal_id = "ScF6ITDLLHe5bOYScpTfyBMCiG0XkPva"
service_principal_secret = "qdACtzLojKO9gYCzfc6oc3VBtshKSOoJEQVLUUk6W6gL9bhvz7uhbQP9BEfP7US-"
role = "Viewer"

vault_url = "https://api.hashicorp.cloud"
vault_secret_path = "/secrets/2023-06-13/organizations/92e300b2-dc96-41e1-af99-488fd920bf48/projects/3716cc7c-ed99-4279-a820-7dc4d78d7b54/apps/webapppy/open"

secret_value = get_secret_from_vault(vault_url, vault_secret_path, service_principal_id, service_principal_secret, role)

if secret_value:
    connection_string = secret_value["connection_string"]

    # Define your Azure Blob Storage account and container information
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = "test104"
    
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
# Enable debugging mode
if __name__ == '__main__':
    app.run(debug=True)
