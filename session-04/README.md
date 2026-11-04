# Session 04 — Events & Live Updates

**Course:** Introduction to Smart Contracts with Solidity
**University:** Atria University
**Name:** Yeshwanth R
**Enrolment ID:** AU24UG-028

## 1. What this project does

`MessageBoard.sol` emits `MessageUpdated(address indexed editor, string newMessage)` whenever the message changes. The backend contains a historical scanner (`main.py`) that queries events over block ranges in chunks, and a WebSocket subscriber (`subscribe.py`) that prints new event notifications without refreshing.

## 2. Design decisions

The contract uses an indexed editor address for filtering. Python, Web3.py, FastAPI dependencies, and `python-dotenv` support the scripts. Historical scanning uses ten-block chunks, retry handling for RPC rate limits, and a short delay between requests. The subscriber uses `AsyncWeb3`, `WebSocketProvider`, a topic filter, and `process_log` to decode live events. The source does not contain a recovery checkpoint implementation or a browser client.

## 3. Deployment

- **Network:** Ethereum Sepolia
- **Chain ID:** 11155111
- **Contract address:** Not recorded
- **Transaction hashes:** Not recorded
- **Method:** Configure `CONTRACT_ADDRESS`, `START_BLOCK`, and HTTP/WebSocket RPC URLs, then run the scanner or subscriber.
- **Environment:** Backend `.env` requires `SEPOLIA_RPC_URL`, `SEPOLIA_WSS_URL`, `CONTRACT_ADDRESS`, and `START_BLOCK` as applicable.

No deployment or transaction was broadcast during this documentation task.

## 4. How to test it

```powershell
cd session-04\\backend
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

The scanner should report each scanned range and decoded event. In a second terminal, run `python subscribe.py`; after an on-chain message update, it should print the new message and editor. Negative test: set `START_BLOCK` higher than the latest block; `main.py` must stop with its validation error instead of scanning an invalid range.

## 5. What I found difficult

Event work requires matching the deployed ABI, selecting safe block ranges, handling provider rate limits, and using a WebSocket endpoint for live delivery. The source includes retry logic for HTTP historical scans, but deployment and recovery checkpoint values are not recorded.

## 6. Acknowledgements

This work uses Solidity events, Python, Web3.py, WebSocket subscriptions, and Ethereum Sepolia documentation. ChatGPT and GitHub Copilot may be used for learning, debugging assistance, and documentation.
