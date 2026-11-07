import os
from dotenv import load_dotenv
from web3 import Web3

from contract import METADATA_REGISTRY_ABI

load_dotenv()

w3 = Web3(
    Web3.HTTPProvider(os.environ["SEPOLIA_RPC_URL"])
)

registry_address = Web3.to_checksum_address(
    os.environ["METADATA_REGISTRY_ADDRESS"]
)

registry = w3.eth.contract(
    address=registry_address,
    abi=METADATA_REGISTRY_ABI
)


def record_metadata(metadata_cid: str):
    private_key = os.environ["PRIVATE_KEY"]

    account = w3.eth.account.from_key(private_key)

    # Confirm the wallet is the contract owner
    owner = registry.functions.owner().call()

    if account.address.lower() != owner.lower():
        raise ValueError(
            "The configured wallet is not the MetadataRegistry owner."
        )

    if w3.eth.chain_id != 11155111:
        raise ValueError("Connected network is not Sepolia.")

    metadata_uri = f"ipfs://{metadata_cid}"

    transaction = registry.functions.setMetadataURI(
        metadata_uri
    ).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "chainId": w3.eth.chain_id,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    })

    signed_tx = w3.eth.account.sign_transaction(
        transaction,
        private_key
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed_tx.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError("Metadata transaction failed.")

    return {
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
        "metadata_uri": registry.functions.metadataURI().call()
    }