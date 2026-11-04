import os
from dotenv  import load_dotenv
from eth_account import Account
from fastapi import FastAPI, HTTPException
from web3 import Web3
from pydantic import BaseModel

from contract import CONTRACT_ABI

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ["SEPOLIA_RPC_URL"]))
account = Account.from_key(os.environ["PRIVATE_KEY"])
contract = w3.eth.contract(
    address=Web3.to_checksum_address(os.environ["CONTRACT_ADDRESS"]),
    abi=CONTRACT_ABI
)
print("Service account:", account.address)

app = FastAPI(title="Custodial Transaction Service")

@app.get("/status")
def get_status():
    return {
        "service_account": account.address,
        "balance_eth": str(Web3.from_wei(w3.eth.get_balance(account.address), "ether")),
        "chain_id": w3.eth.chain_id,
        "current_message": contract.functions.getMessage().call(),
    }

class MessageRequest(BaseModel):
    message: str

@app.post("/encode")
def encode_call(request: MessageRequest):
    call_data = contract.encode_abi("setMessage", args=[request.message])
    return {
        "to": contract.address,
        "data":call_data,
        "selector": call_data[:10],
        "selector_from_signature": Web3.keccak(text="setMessage(string)")[:4].to_0x_hex(),
    }

def build_transaction(message: str, nonce: int) -> dict:
    tx = {
        "from": account.address,
        "to": contract.address,
        "data": contract.encode_abi("setMessage", args=[message]),
        "value": 0,
        "chainId": w3.eth.chain_id,
        "nonce": nonce
    }
    try:
        tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.2)
    except Exception as error:
        raise HTTPException(400, f"Simulation failed {error}")
    priority_fee = w3.eth.max_priority_fee
    base_fee = w3.eth.get_block("latest")["baseFeePerGas"]
    tx["maxPriorityFeePerGas"] = priority_fee
    tx["maxFeePerGas"] = 2 * base_fee + priority_fee
    return tx

@app.post("/prepare")
def prepare_transaction(request: MessageRequest):
    nonce = w3.eth.get_transaction_count(account.address, "pending")
    return build_transaction(request.message, nonce)

def send_set_message(message: str) -> dict:
    nonce = w3.eth.get_transaction_count(account.address, "pending")
    tx = build_transaction(message, nonce)
    signed = account.sign_transaction(tx)

    try:
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction).to_0x_hex()
    except Exception as error:
        raise HTTPException(502, f"The node rejected the transaction nonce {nonce} {error}")
    print("Submitted :", tx_hash)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    status = "confirmed" if receipt["status"] == 1 else "reverted"

    return {
        "transaction_hash": tx_hash,
        "nonce": nonce,
        "status": status,
        "block_number": receipt["blockNumber"]
    }

@app.post("/send")
def send_transaction(request: MessageRequest):
    return send_set_message(request.message)