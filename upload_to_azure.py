from pathlib import Path
from azure.identity import AzureCliCredential
from azure.storage.blob import ContainerClient

ACCOUNT_URL = "https://stpowermarketfm.blob.core.windows.net"
CONTAINER = "raw"
LOCAL_FOLDER = Path("data/raw")

credential = AzureCliCredential()
container = ContainerClient(ACCOUNT_URL, CONTAINER, credential=credential)

files = (
    sorted(LOCAL_FOLDER.glob("prices_*.json"))
    + sorted(LOCAL_FOLDER.glob("consumption_*.json"))
    + sorted(LOCAL_FOLDER.glob("weather_*.json"))
)

for file in files:
    kind, day = file.stem.split("_")[:2]
    blob_name = f"{kind}/{day}/{file.name}"
    container.upload_blob(blob_name, file.read_bytes(), overwrite=True)
    print("Uploaded", blob_name)

print(f"Done: {len(files)} files")
