
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

from contract import CONTRACT_ABI

# 1. Load environment variables
load_dotenv(Path(__file__).with_name(".env"))

RPC_URL = os.getenv("SEPOLIA_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
START_BLOCK = os.getenv("START_BLOCK")

if not RPC_URL or not CONTRACT_ADDRESS or not START_BLOCK:
    raise ValueError("Missing required variables in .env")

# 2. Connect to Ethereum Sepolia
w3 = Web3(
    Web3.HTTPProvider(
        RPC_URL,
        request_kwargs={"timeout": 30}
    )
)

if not w3.is_connected():
    raise ConnectionError("Could not connect to Sepolia")

if w3.eth.chain_id != 11155111:
    raise ConnectionError("Connected to the wrong network")

print("Connected to Ethereum Sepolia")
print("Chain ID:", w3.eth.chain_id)

# 3. Create the contract instance
contract_address = Web3.to_checksum_address(
    CONTRACT_ADDRESS
)

contract_code = w3.eth.get_code(contract_address)

if not contract_code:
    raise ValueError("No contract found at this address on Sepolia")

contract = w3.eth.contract(
    address=contract_address,
    abi=CONTRACT_ABI
)

# 4. Define the historical scanning range
start_block = int(START_BLOCK)
latest_block = w3.eth.block_number

CHUNK = 10

print("Latest block:", latest_block)
print(
    f"Scanning events from block {start_block} "
    f"through {latest_block}..."
)

if start_block > latest_block:
    raise ValueError("START_BLOCK is greater than the latest block")

# 5. Retrieve events with retry handling
def get_events_with_retry(from_block, to_block, retries=5):

    for attempt in range(retries):
        try:
            return contract.events.MessageUpdated().get_logs(
                from_block=from_block,
                to_block=to_block
            )

        except Exception as error:
            error_message = str(error).lower()

            if "429" not in error_message and "too many requests" not in error_message:
                raise

            if attempt == retries - 1:
                raise

            wait_time = min(30, 2 ** (attempt + 1))

            print(
                f"RPC rate limited. Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

# 6. Scan blocks in chunks
total_events = 0

for from_block in range(
    start_block,
    latest_block + 1,
    CHUNK
):

    to_block = min(
        from_block + CHUNK - 1,
        latest_block
    )

    print(f"Scanning blocks {from_block} to {to_block}")

    events = get_events_with_retry(
        from_block,
        to_block
    )

    # 7. Decode and display events
    for event in events:

        print("\nMessageUpdated Event")
        print("Block number:", event["blockNumber"])
        print("Editor:", event["args"]["editor"])
        print("New message:", event["args"]["newMessage"])
        print("Transaction hash:", event["transactionHash"].hex())

        total_events += 1

    time.sleep(0.25)

# 8. Display summary
print("\nHistorical scan completed.")
print("Total events found:", total_events)
