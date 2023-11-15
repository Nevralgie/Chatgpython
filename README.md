# Python app in an Azure Web App service : 

------------------------------------------------------------------------------------------------------------------------------

In this project, we'll learn to deploy an app using the Web App service provided by Microsoft Azure. This app allows users to upload files, and we'll couple it with other Azure services.
Using Azure Python SDK, the files will be uploaded to a blob storage whose credentials are stored in a Vault (Hashicorp Vault Secrets). The app will retrieve these credentials, and generate an ephemeral download link for the user.
The Web app will enable github Actions for continuous deployment. We'll finally use Logic Apps to periodically clean up expired files from Azure Blob Storage.

------------------------------------------------------------------------------------------------------------------------------

Requirements : 

- An Azure subscription
- Basic knowledge of Azure portal and services
- Github account
- [Hashicorp Cloud](https://portal.cloud.hashicorp.com/) account for storing secrets in Vault

Steps : 
   
- Create a resource group if you don't have one already. Set up an Azure storage account and create a container to store the files. Make sure you enable "storage account key access" in the settings.
An SAS key will be used to generate a temporary link for the user after uploading a file. Make sure you enable encryption at rest. In "Access keys", copy the connection string somewhere. We'll need it latter.

- Create an account on the Hashicorp cloud platform. Once signed in, choose 'Vault Secrets' on the left tab menu. After creating your organization and your first project, create a new application and enter the newly created app.
   - Then add a new secret. The secret will be the connection string retrieved after the storage account was created. 
   - Lastly, you'll need to create a service principal at the project level so the Web app can authentify to Vault and read secrets.
   - Head back to the project dashboard page, and choose 'Access control (IAM)' > 'Service principals' > 'Create service principal'. the role 'Viewer' should be enough just to read secrets.
   - Create a service principal key. Make sure to copy the client secret, as you won't be able to access it in the future.

- Modify the following values in app.py : $container_name, $hcpapi_client_id , $hcpapi_client_secret, $vault_secret_path (found on the Hcp website on the 'Secrets' page at the bottom)

- Create a Web App :
   - Make sure to select "Python 3.9" as runtime stack.
   - The free or Basic pricing plan is enough to test everything ( you can either create a new one or use an already-created one). Disable zone redundancy.
   - In the 'Deployment' tab, enable Github Actions settings and authorize your Github account if it's not the case already. Select the appropriate repo.
   - Review and create.
   - Once created, I highly recommend enabling "Application logging" so you can access the container logs. Easier for debugging.

- Create a Logic App :
  - Consumption plan is enough for our use. Make sure to select the same region as your storage account. Review and create.
  - Select 'Logic App designer' on the left menu and choose 'Blank logic App'.
  - We'll now build the logic :
      - First, search for 'Recurrence' (schedule). Once it's done, set up the interval to your liking, a Time zone and the start time. Insert a new step once you're done.
      - Search for Lists blobs (Azure Blob Storage) in action. You'll now have to create a connection between Logic App and the storage account. Name this connection and choose 'Access key' in 'Authentication type'. Enter your
        Azure Storage account name and the access key associated (same page as the connection string). If the connection is valid, you'll be able to select it in the list. You'll then be invited to specify the folder. Choose the path of the Blob container. insert a new step.
      - Search for Filter array (Data Operations). In the 'From' line, select 'value' from the dynamic content pop-up. Click on 'Edit in advanced mode' and copy this : @less(item()?['LastModified'], addHours(utcNow(), -1))
        Alternatively, in basic mode: 'Choose a value' > 'Last Modified' , 'is less than' , 'addHours' (for example) in the 'Expression' tab.
      - Search for For each (Control) : Select 'Body' in the dynamic content tab. Then add an action. Search for 'Delete blob' (Azure Blob Storage). Use the connection you set up earlier and choose 'Path' from the dynamic content tab for the 'Blob' line.
      - Save your Logic design
    You can now test it by clicking on 'Run trigger'. Keep in mind that, depending on the time-frame you chose when setting up the Filter array operation, it may not affect the files in the container.

- Go to the Web App resource. Select 'Browse' to verify that the app is functioning correctly. Modify the app.py file (add a comment, for example) to verify that the Github workflow is functionnal.
- Don't forget to clean up your resources when you're done. 
