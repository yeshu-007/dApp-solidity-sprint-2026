# Session 03 — Build a Blockchain API

**Course:** Introduction to Smart Contracts with Solidity
**University:** Atria University
**Name:** Yeshwanth R
**Enrolment ID:** AU24UG-028

## 1. What this project does

This Python service exposes read-only FastAPI endpoints backed by Web3.py and an Ethereum Sepolia RPC. It reports chain status, reads the configured MessageBoard message, and returns an address balance in wei and ETH. The ABI in `contract.py` describes `getMessage()` and `setMessage(string)`, although the current API exposes only read operations.

## 2. Design decisions

The service uses Python, FastAPI, Pydantic response modeling, Web3.py, and `python-dotenv`. Startup validates the RPC connection and requires Sepolia chain ID `11155111`; the contract address is converted to checksum form. Endpoint-level exceptions are translated into HTTP errors: unavailable blockchain status returns `503`, an invalid address returns `400`, and message/balance failures return `503`.

## 3. Deployment

- **Network:** Ethereum Sepolia
- **Chain ID:** 11155111
- **Contract address:** Not recorded
- **Transaction hash:** Not applicable to this read-only API
- **Method:** Run Uvicorn locally with environment variables.
- **Environment:** `SEPOLIA_RPC_URL` and `CONTRACT_ADDRESS`

## 4. How to test it

```powershell
cd session-03
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs` and test `GET /status`, `GET /message`, and `GET /balance/{address}`. Expected responses contain the Sepolia chain ID, latest block, contract message, or checksum address and balances. Negative test: call `/balance/not-an-address`; the expected response is HTTP `400` with `Invalid Ethereum address`.

## 5. What I found difficult

Startup depends on a reachable RPC and a deployed contract with an ABI matching the configured address. Timeout and connection failures must be distinguished from invalid user input. Deployment values are not recorded in the source.

## 6. Acknowledgements

This work uses Python, FastAPI, Pydantic, Web3.py, Uvicorn, and Ethereum Sepolia documentation. ChatGPT and GitHub Copilot may be used for learning, debugging assistance, and documentation.
