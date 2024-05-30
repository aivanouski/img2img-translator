Step-by-Step Execution

## Task 1: Set Up Google Cloud Project and Enable APIs
Open the Google Cloud Console.
Create a new project or select an existing one.
Navigate to APIs & Services > Dashboard and click Enable APIs and Services.
Enable the following APIs:
Cloud Vision API
Cloud Translation API

## Task 2: Download Service Account Key
Go to APIs & Services > Credentials.
Click Create Credentials, and then select Service Account.
Fill in the details as needed and click Create.
In the Role field, select Project > Owner (or the least privilege necessary for your app).
Continue and click Done.
Click on the newly created service account, then Keys > Add Key > Create new key.
Choose JSON and click Create. This will download a JSON file with your credentials.


## Task 3: Set Environment Variable for Authentication
Store the path to your service account key JSON file in an environment variable:
```
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-service.json"
```