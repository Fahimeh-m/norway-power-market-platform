import os
from pathlib import Path
from azure.storage.blob import ContainerClient

ACCOUNT_URL = "https://stpowermarketfm.blob.core.windows.net"
CONTAINER = "raw"
LOCAL_FOLDER = Path("data/raw")

token = "".join(os.environ["AZURE_STORAGE_SAS_TOKEN"].split())
container = ContainerClient(ACCOUNT_URL, CONTAINER, credential=token)

files = sorted(LOCAL_FOLDER.glob("prices_*.json"))

for file in files:
    day = file.name.split("_")[1]
    blob_name = f"prices/{day}/{file.name}"
    container.upload_blob(blob_name, file.read_bytes(), overwrite=True)
    print("Uploaded", blob_name)

print(f"Done: {len(files)} files")
