# Session 10 --- Unattended Oracle Service

**Student:** Yeshwanth R  
**Student ID:** AU24UG-28  
**Assignment:** Session 10 - Unattended Oracle Service  
**Network:** Ethereum Sepolia Testnet  
**Chain ID:** `11155111`

## 1. What This Project Does

This project demonstrates an unattended Python oracle service that obtains ETH/USD
price data from external APIs and publishes an authorised update to a Solidity
contract on Sepolia.

An **oracle** is a service that supplies off-chain information to an on-chain
application. A smart contract cannot directly make HTTP requests because
Ethereum execution must be deterministic and independently reproducible by every
node. The oracle is therefore the bridge between external APIs and blockchain
state.

The current workflow is:

1. [`oracle.py`](./oracle/oracle.py) requests the ETH/USD spot price from both
   CoinGecko and Coinbase.
2. Each response is checked for an HTTP error and for a configured range of
   `$100` to `$10,000`.
3. The two valid values are averaged and converted to an integer with 8 decimal
   places.
4. The service reads the stored value and its on-chain age. It submits an
   update only when the stored value has moved by at least `0.1%` or the
   heartbeat is at least 60 seconds old.
5. [`PriceFeed.sol`](./contracts/PriceFeed.sol) stores the latest value, update
   timestamp, updater address, and round ID.
6. [`PriceConsumer.sol`](./contracts/PriceConsumer.sol) reads the feed and
   returns the price and its age. It rejects the value when no timestamp exists
   or when the value is older than its constructor-configured `maxAge`.

The service polls every 20 seconds. An API error, invalid response, validation
failure, or transaction failure is printed and does not produce a successful
update.

## 2. Project Structure

```text
session-10/
|-- contracts/
|   |-- PriceConsumer.sol
|   `-- PriceFeed.sol
|-- oracle/
|   |-- .env                  # Local secrets; ignored by Git
|   |-- contract.py           # ABI used by the Python service
|   `-- oracle.py             # Unattended fetch, validation, and update loop
|-- .env.example              # Safe configuration template
|-- README.md
`-- requirements.txt
```

Generated local folders such as `.venv/` and `oracle/__pycache__/` are not part
of the submitted source structure.

### Important files

- **`contracts/PriceFeed.sol`** --- Stores the oracle address, signed integer
  price, `updatedAt`, updater, and round ID. Its `update` function accepts calls
  only from the address supplied to the constructor.
- **`contracts/PriceConsumer.sol`** --- Reads the feed through an
  `AggregatorV3Interface`-compatible interface. `getPrice()` returns the value
  and age, subject to `maxAge`; `usdToWei()` converts a positive price into a
  wei amount.
- **`oracle/oracle.py`** --- Loads configuration, connects to Sepolia, fetches
  prices from CoinGecko and Coinbase, validates and averages them, applies the
  update policy, signs the transaction, and waits for its receipt.
- **`oracle/contract.py`** --- Contains the ABI used by the Python service.
- **`oracle/.env`** --- Local values for `SEPOLIA_RPC_URL`, `PRIVATE_KEY`, and
  `CONTRACT_ADDRESS`. It must never be committed.
- **`requirements.txt`** --- Python dependencies, including Web3.py,
  `eth-account`, `requests`, and `python-dotenv`.
- **Frontend** --- No frontend files are present in this Session 10 folder.

## 3. Design Decisions

### Separate oracle service

The external price APIs are off-chain HTTP services, so they cannot be called
from Solidity. A separate Python process performs that work and sends a signed
transaction to the blockchain.

### Authorised updates

`PriceFeed` stores an `oracle` address at deployment and checks
`msg.sender == oracle` before accepting an update. This prevents arbitrary
wallets from changing the published price.

### Validation before submission

The service requests two independent sources, checks both HTTP responses, parses
the expected response fields, and rejects prices outside the `$100`---`$10,000`
range before constructing a transaction. This avoids spending gas on data that
the service has already identified as unusable.

### Timestamps and maximum age

`PriceFeed` records `block.timestamp` in `updatedAt` for every accepted update.
`PriceConsumer` compares the current block timestamp with that value and rejects
data older than its deployed `maxAge`. The actual `maxAge` value is not recorded
in the repository and must be filled in below.

### Update schedule and meaningful-change policy

The oracle checks for new data every 20 seconds. It submits when either:

- the on-chain data age is at least 60 seconds (`HEARTBEAT`), or
- the absolute price difference reaches `0.1%` of the stored value
  (`CHANGE_PERCENT`).

Otherwise it logs that the change was below the threshold and skips the
transaction. The age calculation uses the latest blockchain timestamp rather
than the laptop's local clock.

### Custody model

The service operator holds the oracle private key in the local environment and
uses it to sign update transactions. The private key is not stored in the
contract or source code. This is a custodial operational model: compromise of
the service environment could allow the authorised oracle account to submit
updates.

## 4. Deployment

The repository does not contain deployment scripts, addresses, transaction
hashes, or a recorded `maxAge` value. Replace the following placeholders after
deployment or verification:

| Item | Value |
|---|---|
| PriceFeed contract address | `[FILL IN: 0x...]` |
| PriceFeed deployment transaction hash | `[FILL IN: 0x...]` |
| PriceConsumer contract address | `[FILL IN: 0x...]` |
| PriceConsumer deployment transaction hash | `[FILL IN: 0x...]` |
| Authorised Oracle wallet address | `[FILL IN: 0x...]` |
| PriceConsumer `maxAge` seconds | `[FILL IN]` |
| Network | Ethereum Sepolia Testnet |
| Chain ID | `11155111` |

After entering real values, the corresponding Etherscan links can be added:

- PriceFeed address: `https://sepolia.etherscan.io/address/[PRICEFEED_ADDRESS]`
- PriceFeed deployment transaction:
  `https://sepolia.etherscan.io/tx/[PRICEFEED_DEPLOYMENT_TX_HASH]`
- PriceConsumer address:
  `https://sepolia.etherscan.io/address/[PRICECONSUMER_ADDRESS]`
- PriceConsumer deployment transaction:
  `https://sepolia.etherscan.io/tx/[PRICECONSUMER_DEPLOYMENT_TX_HASH]`
- Oracle wallet:
  `https://sepolia.etherscan.io/address/[ORACLE_WALLET_ADDRESS]`

These are templates only; no deployment link is claimed until the matching
value has been recorded.

## 5. Environment Setup

From the repository root, enter the Session 10 directory and create a virtual
environment:

```powershell
cd session-10
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy [`.env.example`](./.env.example) to `oracle/.env` and replace its
placeholders:

```powershell
Copy-Item .env.example oracle\.env
```

The variable names must match the source code:

```dotenv
SEPOLIA_RPC_URL=https://your-sepolia-rpc-endpoint
PRIVATE_KEY=0xYOUR_ORACLE_PRIVATE_KEY
CONTRACT_ADDRESS=0xYOUR_DEPLOYED_PRICEFEED_ADDRESS
```

`PRIVATE_KEY` must belong to the wallet authorised in `PriceFeed`. Use a
dedicated test wallet funded only with the Sepolia ETH needed for testing.
Never put private keys, RPC credentials, or populated `.env` files in GitHub.
The repository `.gitignore` already excludes `.env`, `.venv/`,
`__pycache__/`, and Python cache files; confirm before committing:

```powershell
git check-ignore -v oracle\.env .venv oracle\__pycache__
git status --short
```

## 6. How to Run

With the virtual environment active:

```powershell
cd session-10
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd oracle
python oracle.py
```

The script runs continuously, prints the two source prices, and reports whether
an update was submitted or skipped. Stop it with **Ctrl+C** in the terminal.
There is no frontend or separate web server to start.

## 7. How to Test It

No automated test files or recorded test results are included in this folder.
The following status distinguishes behavior implemented in the source from
behavior verified by a reproducible test record:

| Required check | Status | Evidence / next step |
|---|---|---|
| Unauthorised wallet update is rejected | Implemented, not verified here | `PriceFeed.update` requires the configured oracle address. Send an update from a different wallet and record the reverted transaction or call result. |
| API failure does not trigger a transaction | Implemented, not verified here | `get_json()` raises on request/HTTP failure and the loop logs `nothing submitted`. Simulate an unavailable API and confirm no transaction hash is emitted. |
| Invalid data does not trigger a transaction | Implemented, not verified here | Range validation raises before `submit_value()`. Test an out-of-range or malformed response and confirm no transaction is sent. |
| Interface displays stored price and age | Not applicable | No frontend is present in this Session 10 folder. |
| Stopping the oracle produces stale data | Pending manual verification | Stop `oracle.py` and wait longer than the deployed `maxAge`. Record the elapsed time and the feed state. |
| `PriceConsumer` rejects stale data | Implemented, not verified here | `getPrice()` reverts with `Data is stale` when the age exceeds `maxAge`. Call it after the previous step and record the revert. |

For a complete submission, add the actual wallet, deployment, and transaction
evidence to this table without claiming checks that were not run.

## 8. What I Found Difficult

The main learning challenges in this assignment are expected to be:

- coordinating off-chain API responses with on-chain transaction timing;
- handling failures without submitting invalid or incomplete data;
- keeping the oracle private key and RPC endpoint out of the source repository;
- understanding why a feed timestamp and a maximum age are necessary for
  consumers.

**Student reflection:** `[Replace this paragraph with the specific difficulty
encountered and how it was resolved, if applicable.]`

## 9. Acknowledgements

This work follows the Session 10 learning material on unattended oracle
services. Applicable tools and technologies include Solidity, Python, Web3.py,
`eth-account`, `requests`, `python-dotenv`, and Ethereum Sepolia. Remix may be
used for manual contract compilation, deployment, or inspection if that was
the deployment workflow used for this submission.


