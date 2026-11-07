import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
import json
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="IPFS Storage API")

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_SIZE = 1_000_000 # 1 MB

PINATA_JWT= os.environ["PINATA_JWT"]
GATEWAY = os.environ["PINATA_GATEWAY"]
PINATA_UPLOAD_URL= "https://uploads.pinata.cloud/v3/files"

async def pin_file(data: bytes, filename: str, content_type: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            PINATA_UPLOAD_URL,
            headers={"Authorization": f"Bearer {PINATA_JWT}"},
            files={"file": (filename, data, content_type)},
            data={"network": "public"},
        )
    if response.status_code != 200:
        raise HTTPException(502, f"Pinata upload failed: {response.text}")
    return response.json()["data"]["cid"]

@app.post("/upload")
async def upload_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "File type not allowed.")

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(400, "The file is  empty")
    if len(data) > MAX_SIZE:
        raise HTTPException(413, "File too large, The limit is 1 MB")

    asset_cid = await pin_file(data, file.filename, file.content_type)
    return {"asset_cid": asset_cid, "url": f"{GATEWAY}/ipfs/{asset_cid}"}

class MetadataRequest(BaseModel):
    name: str
    description: str
    asset_cid: str


@app.post("/metadata")
async def upload_metadata(metadata: MetadataRequest):
    metadata_json = {
        "name": metadata.name,
        "description": metadata.description,
        "image": f"ipfs://{metadata.asset_cid}"
    }

    data = json.dumps(metadata_json, indent=2).encode("utf-8")

    metadata_cid = await pin_file(
        data,
        "metadata.json",
        "application/json"
    )

    return {
        "metadata_cid": metadata_cid,
        "metadata": metadata_json,
        "url": f"{GATEWAY}/ipfs/{metadata_cid}"
    }