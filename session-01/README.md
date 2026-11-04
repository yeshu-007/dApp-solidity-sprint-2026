# Session 01 — Deploy & Interact from TypeScript

**Course:** Introduction to Smart Contracts with Solidity
**University:** Atria University
**Name:** Yeshwanth R
**Enrolment ID:** AU24UG-028

## 1. What this project does

This session compiles and deploys `contracts/Storage.sol` to Ethereum Sepolia, reads its private `number` state through `retrieve()`, writes a value through `store(uint256)`, waits for confirmation, and reads the updated value. The main workflow is implemented in `scripts/deploy-interact.ts`; smaller scripts check the environment, connect to the RPC, or interact with an already deployed address.

## 2. Design decisions

The contract uses Solidity `^0.8.20` and a minimal single-contract storage architecture. The scripts use TypeScript, Node.js, `ethers` 6, `solc`, and `dotenv`. `deploy-interact.ts` compiles the source at runtime, verifies chain ID `11155111`, creates an ethers `Wallet`, deploys with `ContractFactory`, and calls `store(25)` only after reading the initial state. Explicit confirmation checks prevent a failed receipt from being reported as success.

## 3. Deployment

- **Network:** Ethereum Sepolia
- **Chain ID:** 11155111
- **Contract address:** Not recorded
- **Deployment transaction hash:** Not recorded
- **Explorer URL:** Not recorded
- **Method:** `scripts/deploy-interact.ts` compiles and deploys the contract using the configured deployer key.
- **Environment:** `SEPOLIA_RPC_URL` and `DEPLOYER_PRIVATE_KEY`; `scripts/interact.ts` additionally expects `CONTRACT_ADDRESS`.

No deployment or transaction was broadcast during this documentation task.

## 4. How to test it

Prerequisite: Node.js and a funded Sepolia test account. From PowerShell:

```powershell
cd session-01
Copy-Item .env.example .env
npm install
npx tsx scripts/deploy-interact.ts
```

For the nested script project:

```powershell
cd scripts
npm install
npx tsx check.ts
npx tsx connect.ts
```

Expected deployment output includes Sepolia chain ID, a deployed address, a deployment hash, an initial value, a confirmed update transaction, and updated value `25`. Negative test: set an incorrect `SEPOLIA_RPC_URL` or use a non-Sepolia endpoint; the script must fail with its connection or wrong-network error rather than deploy.

## 5. What I found difficult

The workflow depends on correct RPC credentials, a private key, the exact Sepolia network, and a correct relative path to `contracts/Storage.sol`. Runtime Solidity compilation and waiting for a receipt also make failures visible at different stages. Deployment details were not recorded in the source.

## 6. Acknowledgements

This work uses Solidity, ethers.js, solc, Node.js, and Ethereum Sepolia documentation. ChatGPT and GitHub Copilot may be used for learning, debugging assistance, and documentation; the implementation remains the preserved assignment source.
