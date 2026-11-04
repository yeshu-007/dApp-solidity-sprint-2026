# Session 07 — Custodial Keys & Transaction Services

**Course:** Introduction to Smart Contracts with Solidity
**University:** Atria University
**Name:** Yeshwanth R
**Enrolment ID:** AU24UG-028

## 1. What this project does

This FastAPI service controls a backend account and updates a MessageBoard contract on behalf of API callers. It reports service status, ABI-encodes `setMessage(string)`, prepares an EIP-1559 transaction, or signs, broadcasts, and waits for a confirmed transaction.

## 2. Design decisions

The backend uses Python, FastAPI, Web3.py, eth-account, Pydantic, and `python-dotenv`. `contract.py` defines the ABI. `main.py` loads a private key from environment configuration, uses the pending nonce, estimates gas with a 20% margin, computes `maxFeePerGas` and `maxPriorityFeePerGas`, signs locally, and returns the hash, nonce, status, and block number. Endpoints are `GET /status`, `POST /encode`, `POST /prepare`, and `POST /send`, all using a `{ "message": "..." }` body where applicable.

## 3. Deployment

- **Network:** Read from the configured RPC; the course topic targets Ethereum Sepolia
- **Chain ID:** Read at runtime
- **Contract address:** Not recorded
- **Transaction hashes:** Not recorded
- **Method:** Run the FastAPI service with a backend-controlled account.
- **Environment:** `SEPOLIA_RPC_URL`, `PRIVATE_KEY`, and `CONTRACT_ADDRESS`

No transaction was broadcast during this documentation task.

## 4. How to test it

```powershell
cd session-07\\backend
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

Use Swagger UI at `http://127.0.0.1:8000/docs`:

1. `GET /status` returns the service account, balance, chain ID, and current message.
2. `POST /encode` returns the target, calldata, and function selector.
3. `POST /prepare` returns an estimated transaction.
4. `POST /send` signs, broadcasts, waits up to 120 seconds, and returns receipt details.

Negative test: submit an invalid message transaction or use a key without sufficient funds; gas simulation or node submission must return an explicit HTTP error rather than a success-shaped response.

## 5. What I found difficult

Custodial signing makes private-key protection, nonce coordination, gas estimation, fee selection, node rejection, and receipt timeouts important. The service logs the account address but keeps the key in environment configuration. Deployment values and audit-log storage are not recorded in the source.

## 6. Acknowledgements

This work uses Python, FastAPI, Web3.py, eth-account, EIP-1559 transaction concepts, and Ethereum documentation. ChatGPT and GitHub Copilot may be used for learning, debugging assistance, and documentation.
