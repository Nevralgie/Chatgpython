import requests
import json
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from flask import Flask, request, render_template

app = Flask(__name__)

# Define at the module level
connection_string = None  # Initialize connection_string
blob_service_client = None  # Initialize blob_service_client
container_name = "test104"

# Replace with your actual HCP API token retrieval information
hcpapi_token_url = "https://auth.hashicorp.com/oauth/token"
hcpapi_client_id = "ScF6ITDLLHe5bOYScpTfyBMCiG0XkPva"  # Replace with your actual client ID
hcpapi_client_secret = "qdACtzLojKO9gYCzfc6oc3VBtshKSOoJEQVLUUk6W6gL9bhvz7uhbQP9BEfP7US-"  # Replace with your actual client secret

# Replace with your actual HashiCorp Vault secret path
vault_secret_path = "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/92e300b2-dc96-41e1-af99-488fd920bf48/projects/3716cc7c-ed99-4279-a820-7dc4d78d7b54/apps/webapppy/open"  # Replace with your secret path

def get_secret_from_vault(vault_secret_path, hcpapi_token):
    headers = {"Authorization": f"Bearer {hcpapi_token}"}
    response = requests.get(vault_secret_path, headers=headers)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        secrets = response_data.get("secrets")

        if secrets and len(secrets) > 0:
            connection_string = secrets[0].get("version", {}).get("value")
            if connection_string:
                return connection_string

        raise Exception("Connection string not found in secrets")
    else:
        raise Exception(f"Failed to retrieve secret: {response.status_code} - {response.text}")

def get_hcpapi_token(hcpapi_token_url, hcpapi_client_id, hcpapi_client_secret):
    headers = {'content-type': 'application/json'}
    payload = {
        "audience": "https://api.hashicorp.cloud",
        "grant_type": "client_credentials",
        "client_id": hcpapi_client_id,
        "client_secret": hcpapi_client_secret
    }

    response = requests.post(hcpapi_token_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        hcpapi_token = json.loads(response.text)["access_token"]
        return hcpapi_token
    else:
        raise Exception("Failed to retrieve HCP API token")

@app.route('/')
def index():
    global connection_string  # Declare global connection_string
    global blob_service_client  # Declare global blob_service_client

    # Retrieve the HCP API token
    hcpapi_token = get_hcpapi_token(hcpapi_token_url, hcpapi_client_id, hcpapi_client_secret)

    # Use the HCP API token to get the secret from HashiCorp Vault
    secret_value = get_secret_from_vault(vault_secret_path, hcpapi_token)

    if secret_value:
        connection_string = secret_value

        if connection_string:
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            return render_template('index.html')

    return 'Failed to retrieve secret or connection string'

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
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

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
                expiry=datetime.utcnow() + timedelta(hours=1)
            )

            # Build the temporary download link
            sas_url = f"{blob_client.url}?{sas_token}"

            return f'File successfully uploaded to Azure Blob Storage. Temporary link: <a href="{sas_url}">Download</a>'
        except Exception as e:
            return f'Error uploading file: {str(e)}'

# Enable debugging mode
if __name__ == '__main__':
    app.run(debug=True)
