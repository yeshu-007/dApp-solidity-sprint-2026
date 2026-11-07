# Session 5 - Decentralised Storage & IPFS

**Course:** Introduction to Smart Contracts with Solidity
**Student:** Yeshwanth R
**Student ID:** AU24UG-28
**Network:** Ethereum Sepolia Testnet

## 1. Project Overview

This project demonstrates a decentralised-storage workflow for image assets:

1. The backend accepts a supported image and pins it to Pinata's public IPFS
   network.
2. The backend creates JSON metadata containing the asset's IPFS CID and pins
   that metadata to IPFS.
3. The metadata URI can be recorded in the `MetadataRegistry` smart contract on
   Sepolia by using the separate transaction helper.

The FastAPI application exposes the asset and metadata upload operations. The
on-chain operation is currently implemented as a Python helper function, not as
an HTTP endpoint.

## 2. Objectives

- Upload supported image files to IPFS through Pinata.
- Enforce file-type and 1 MB size validation before upload.
- Create metadata that refers to the uploaded asset with an `ipfs://` URI.
- Store the metadata URI in a Solidity contract on Ethereum Sepolia.
- Demonstrate the relationship between off-chain IPFS content and on-chain
  metadata registration.

## 3. Technology Stack

- **Python**
- **FastAPI** and **Uvicorn**
- **Pydantic** request validation
- **httpx** for Pinata HTTP requests
- **python-dotenv** for local environment configuration
- **web3.py** for Sepolia contract interaction
- **Solidity 0.8.20**
- **Pinata public IPFS network**
- **Ethereum Sepolia Testnet**

## 4. Project Structure

```text
session-05/
├── backend/
│   ├── .env.example
│   ├── contract.py
│   ├── main.py
│   ├── metadata_transaction.py
│   └── requirements.txt
├── contracts/
│   └── MetadataRegistry.sol
├── .gitignore
└── README.md
```

- `backend/main.py` defines the FastAPI application and upload routes.
- `backend/contract.py` contains the ABI used by the transaction helper.
- `backend/metadata_transaction.py` connects to Sepolia and records a metadata
  URI after checking ownership.
- `contracts/MetadataRegistry.sol` defines the on-chain registry.
- `backend/.env.example` lists the local configuration variables.

## 5. System Architecture and Upload Workflow

```text
Client
  │
  ├─ POST /upload (image)
  │       │
  │       └─ FastAPI validation ──> Pinata ──> asset CID
  │
  ├─ POST /metadata (name, description, asset CID)
  │       │
  │       └─ JSON metadata ───────> Pinata ──> metadata CID
  │
  └─ separate Python helper
          │
          └─ ipfs://<metadata CID> ──> MetadataRegistry.setMetadataURI()
```

For an asset upload, `main.py` accepts only `image/png`, `image/jpeg`,
`image/gif`, and `image/webp`. Empty files are rejected and files larger than
1 MB are rejected. The returned asset CID is then supplied to `/metadata`.

The metadata request creates JSON in this form:

```json
{
  "name": "Example name",
  "description": "Example description",
  "image": "ipfs://<asset-cid>"
}
```

## 6. Backend Setup and Installation

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file from the example, fill in the required values, and
start the API:

```powershell
uvicorn main:app --reload
```

The interactive API documentation is available at
`http://127.0.0.1:8000/docs` while the server is running.

## 7. Environment Variables

Never commit `.env` or any secret values to Git. The repository's `.gitignore`
excludes `.env`. Use placeholders locally:

```dotenv
PINATA_JWT=<pinata-jwt>
PINATA_GATEWAY=<pinata-gateway-host>
SEPOLIA_RPC_URL=<sepolia-rpc-url>
METADATA_REGISTRY_ADDRESS=<deployed-contract-address>
PRIVATE_KEY=<wallet-private-key>
```

`main.py` requires `PINATA_JWT` and `PINATA_GATEWAY`. The transaction helper
requires `SEPOLIA_RPC_URL`, `METADATA_REGISTRY_ADDRESS`, and `PRIVATE_KEY`.
`PRIVATE_KEY` must belong to the contract owner.

The supplied `backend/.env.example` currently names the contract variable
`CONTRACT_ADDRESS`, while `metadata_transaction.py` reads
`METADATA_REGISTRY_ADDRESS`. This must be reconciled in the local environment
before running the transaction helper; the private key, JWT, and RPC URL must
remain secret.

## 8. API Endpoints

### `POST /upload` - File upload

Accepts a multipart form upload with a `file` field.

- Allowed MIME types: PNG, JPEG, GIF, and WebP.
- Maximum size: 1 MB.
- Empty files return HTTP 400.
- Unsupported types return HTTP 400.
- Files over the limit return HTTP 413.

Successful response shape:

```json
{
  "asset_cid": "<asset-cid>",
  "url": "<configured-gateway>/ipfs/<asset-cid>"
}
```

### `POST /metadata` - Metadata upload

Accepts a JSON request body:

```json
{
  "name": "Asset name",
  "description": "Asset description",
  "asset_cid": "<asset-cid>"
}
```

The route creates and pins `metadata.json`. Its response includes the metadata
CID, the generated metadata object, and a gateway URL:

```json
{
  "metadata_cid": "<metadata-cid>",
  "metadata": {
    "name": "Asset name",
    "description": "Asset description",
    "image": "ipfs://<asset-cid>"
  },
  "url": "<configured-gateway>/ipfs/<metadata-cid>"
}
```

### On-chain metadata recording

There is no HTTP endpoint for this operation. The function
`record_metadata(metadata_cid)` in `metadata_transaction.py`:

1. Loads the configured Sepolia contract.
2. Checks that the configured wallet is the contract owner.
3. Checks that the connected chain ID is `11155111` (Sepolia).
4. Calls `setMetadataURI("ipfs://<metadata-cid>")`.
5. Waits for the receipt and returns the transaction hash, block number, and
   stored URI when successful.

### Retrieval and status endpoints

No asset retrieval, metadata retrieval, transaction-status, or health-check
endpoint is implemented in `main.py`. IPFS content can be viewed through the
configured gateway using the returned CID or URL.

## 9. Smart Contract Details

### `MetadataRegistry.sol`

The contract stores one metadata URI and restricts updates to its owner:

- `owner()` - public view getter returning the owner address.
- `metadataURI()` - public view getter returning the current metadata URI.
- `setMetadataURI(string newMetadataURI)` - owner-only update function; rejects
  an empty URI and emits `MetadataUpdated`.

The contract address present in the project's local configuration is:

```text
0xd9145CCE52D386f254917e481eB44e9943F39138
```

No deployment transaction or deployment script is included in the inspected
project files.

The transaction hash and confirmation status are **pending/not recorded**.
The project files do not provide evidence that the metadata-recording
transaction has been submitted successfully.

## 10. IPFS Storage

An **asset CID** identifies the uploaded binary image. It is returned by
`POST /upload` and is inserted into the metadata as:

```text
ipfs://<asset-cid>
```

A **metadata CID** identifies the JSON document created by `POST /metadata`.
The metadata document references the asset CID in its `image` field; therefore,
the metadata points to the image without storing the image bytes on-chain.

The supplied metadata information for this submission is:

- **Metadata CID:** `bafybeidwty7h4kj2sqhk4rxrg57qj3jsaxx6jb3vqdsfxflkvduhjzi3ce`
- **Metadata URI:** `ipfs://bafybeidwty7h4kj2sqhk4rxrg57qj3jsaxx6jb3vqdsfxflkvduhjzi3ce`
- **Asset CID:** not recorded in the project files; it is generated when an
  image is uploaded.

## 11. Running the Application

1. Configure the local `backend/.env` without committing it.
2. Install the dependencies listed in `backend/requirements.txt`.
3. Start the API from `backend`:

   ```powershell
   uvicorn main:app --reload
   ```

4. Call `POST /upload` with a supported image.
5. Pass the returned `asset_cid` to `POST /metadata`.
6. If on-chain recording is required, call `record_metadata()` from a
   controlled Python session after verifying the owner wallet, RPC URL, and
   contract-address variable.

## 12. Testing and Verification

The inspected project contains no automated test files and no recorded test
results. Manual verification can use the generated FastAPI documentation:

- Confirm valid image uploads return an asset CID.
- Confirm empty, unsupported, and over-1 MB files are rejected.
- Confirm `/metadata` returns JSON containing the asset's `ipfs://` reference.
- Confirm the supplied metadata CID resolves to the expected metadata when
  checked through an IPFS gateway.
- Before claiming on-chain success, verify the Sepolia receipt, transaction
  hash, block number, and `metadataURI()` value.

## 13. Security Considerations

- Keep Pinata JWTs, private keys, and RPC credentials out of source control.
- Keep `.env` excluded from Git and commit only placeholder configuration.
- Use a dedicated test wallet with limited Sepolia funds.
- The contract owner check prevents a non-owner wallet from updating the URI.
- The helper also checks the Sepolia chain ID before sending a transaction.
- Upload validation limits accepted image types and file size, but does not
  replace malware scanning or content moderation.
- Treat the configured Pinata gateway and external IPFS services as
  dependencies; handle upload failures and verify returned CIDs.

## 14. Expected Output and Screenshots

Expected output after a successful file upload:

```text
asset_cid: <CID returned by Pinata>
url: <gateway URL for the asset>
```

Expected output after a successful metadata upload:

```text
metadata_cid: <CID returned by Pinata>
metadata.image: ipfs://<asset CID>
url: <gateway URL for the metadata>
```

On-chain output is not claimed yet:

```text
transaction_hash: PENDING
confirmation status: PENDING / NOT RECORDED
```


## 15. Student Details

- **Student:** Yeshwanth R
- **Student ID:** AU24UG-28
- **Session:** 5 - Decentralised Storage & IPFS
- **Network:** Ethereum Sepolia Testnet
- **Metadata CID:** `bafybeidwty7h4kj2sqhk4rxrg57qj3jsaxx6jb3vqdsfxflkvduhjzi3ce`
- **Metadata URI:** `ipfs://bafybeidwty7h4kj2sqhk4rxrg57qj3jsaxx6jb3vqdsfxflkvduhjzi3ce`

## Files Inspected and Remaining Information

Inspected:

- `README.md`
- `backend/main.py`
- `backend/metadata_transaction.py`
- `backend/contract.py`
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/.env` (configuration key used only to verify the contract address;
  secrets were not reproduced)
- `contracts/MetadataRegistry.sol`
- `.gitignore`

Still required for a fully evidenced submission:

- The asset CID produced by the actual image upload.
- The submitted Sepolia transaction hash, receipt/confirmation status, and
  resulting block number, if on-chain recording has been performed.