# Session 06 — Wallet Basics — Keys, Addresses & Digital Signatures

**Course:** Introduction to Smart Contracts with Solidity
**University:** Atria University
**Name:** Yeshwanth R
**Enrolment ID:** AU24UG-028

## 1. What this project does

The four scripts demonstrate Ethereum account creation, public/private keys and addresses, mnemonic derivation, message signing and recovery, and construction and broadcasting of a raw EIP-1559 transaction. The first three scripts are local demonstrations; `04_raw_transaction.py` uses a configured Sepolia RPC and sends `0.001` ETH to a configured recipient.

## 2. Design decisions

The project uses Python, `eth-account`, `eth-keys`, `mnemonic`, Web3.py, and `python-dotenv`. HD accounts use paths such as `m/44'/60'/0/0/0`. Message verification recovers the signer from an EIP-191-style defunct message. The raw transaction obtains a pending nonce, chain ID, base fee, and priority fee, signs locally, broadcasts, and waits for a receipt.

## 3. Deployment

- **Network:** The raw transaction reads the configured network; the intended network is Ethereum Sepolia.
- **Chain ID:** Read at runtime from the RPC
- **Contract address:** Not applicable
- **Transaction hash:** Not recorded
- **Method:** `04_raw_transaction.py` signs and broadcasts a value transfer.
- **Environment:** `SEPOLIA_RPC_URL`, `PRIVATE_KEY`, and `RECIPIENT_ADDRESS`

Do not run the raw transaction script with a valuable key or recipient without reviewing the amount and network.

## 4. How to test it

```powershell
cd session-06
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python script\\01_make_address.py
python script\\02_seed_phrase.py
python script\\03_sign_verify.py
```

The first scripts print generated addresses, derivations, a signature, and a recovered address. For the network script, copy `.env.example` to `.env`, review every value, and run `python script\\04_raw_transaction.py`; expected output includes signed raw data and a receipt if the transaction is intentionally broadcast. Negative test: alter the message after signing before recovery; the recovered address should no longer match the signer.

## 5. What I found difficult

The main risks are handling secrets safely, using the correct derivation path, distinguishing message signatures from transaction signatures, and selecting compatible EIP-1559 fee and nonce values. The scripts intentionally print sensitive demonstration material, so they should only be used with disposable local/test accounts.

## 6. Acknowledgements

This work uses Python, eth-account, eth-keys, mnemonic, Web3.py, and Ethereum account/signing documentation. ChatGPT and GitHub Copilot may be used for learning, debugging assistance, and documentation.
