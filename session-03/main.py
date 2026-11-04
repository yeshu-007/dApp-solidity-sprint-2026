import os
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contract import CONTRACT_ABI



load_dotenv(Path(__file__).with_name(".env"))

RPC_URL = os.getenv("SEPOLIA_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

if not RPC_URL or not CONTRACT_ADDRESS:
    raise ValueError("Missing RPC URL or contract address in .env file")

w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs = {"timeout":15}))

if not w3.is_connected():
    raise ConnectionError("Failed to connect to the Ethereum network")
if w3.eth.chain_id != 11155111:
    raise ValueError("Connected to the wrong network. Please connect to the Sepolia testnet.")

print("Connected to Ethereum Sepolia")
print("Chain ID:", w3.eth.chain_id)
print("Latest block:", w3.eth.block_number)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=CONTRACT_ABI
)


# 5. Create FastAPI application
app = FastAPI(title="Message Board API")


# 6. Define response model
class StatusResponse(BaseModel):
    chain_id: int
    latest_block: int


# 7. Create status endpoint
@app.get("/status", response_model=StatusResponse)
def get_status():
    try:
        if not w3.is_connected():
            raise HTTPException(
                status_code=503,
                detail="Blockchain node unavailable"
            )

        return {
            "chain_id": w3.eth.chain_id,
            "latest_block": w3.eth.block_number
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Status endpoint error:", error)
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve blockchain status"
        )


@app.get("/message")
def get_message():
    try:
        return {"message": contract.functions.getMessage().call()}
    except Exception as error:
        print("Message endpoint error:", error)
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve contract message"
        )


@app.get("/balance/{address}")
def get_balance(address: str):
    try:
        checksum_address = Web3.to_checksum_address(address)
        balance_wei = w3.eth.get_balance(checksum_address)
        return {
            "address": checksum_address,
            "balance_wei": balance_wei,
            "balance_eth": float(Web3.from_wei(balance_wei, "ether"))
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Ethereum address"
        )
    except Exception as error:
        print("Balance endpoint error:", error)
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve account balance"
        )
