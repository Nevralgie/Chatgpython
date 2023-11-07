from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__, static_folder='static', static_url_path='')

app.config.from_pyfile('config.py')
account = app.config['ACCOUNT_NAME']   # Azure account name
key = app.config['ACCOUNT_KEY']      # Azure Storage account access key  
connect_str = app.config['CONNECTION_STRING']
container = app.config['CONTAINER'] # Container name
allowed_ext = app.config['ALLOWED_EXTENSIONS'] # List of accepted extensions
max_length = app.config['MAX_CONTENT_LENGTH'] # Maximum size of the uploaded file

blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in allowed_ext

@app.route('/upload',methods=['POST'])
def upload():
    if request.method == 'POST':
        img = request.files['file']
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            img.save(filename)
            blob_client = blob_service_client.get_blob_client(container = container, blob = filename)
            with open(filename, "rb") as data:
                try:
                    blob_client.upload_blob(data, overwrite=True)
                    msg = "Upload Done ! "
                except:
                    pass
            os.remove(filename)
    return render_template("index.html", msg=msg)

if __name__ == "__main__":
    app.run()
