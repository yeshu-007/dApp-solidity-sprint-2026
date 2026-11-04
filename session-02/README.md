# Session 02 — Build a Wallet-Connected Page

**Course:** Introduction to Smart Contracts with Solidity
**University:** Atria University
**Name:** Yeshwanth R
**Enrolment ID:** AU24UG-028

## 1. What this project does

This Next.js browser dApp connects to MetaMask, displays the selected account and chain ID, reads `MessageBoard.getMessage()`, and writes a new message through `setMessage(string)`. The page shows idle, pending, confirmed, and failed transaction states and links a confirmed transaction to Sepolia Etherscan.

## 2. Design decisions

The frontend uses Next.js 16, React 19, TypeScript, and ethers.js 6. `app/page.tsx` uses `BrowserProvider` for the injected wallet, `Contract` for reads and signed writes, and event listeners for `accountsChanged` and `chainChanged`. The contract ABI is kept in `lib/contract.ts`; the contract address is supplied through `NEXT_PUBLIC_CONTRACT_ADDRESS`. Writes are restricted to chain ID `11155111` and wait for a successful receipt before refreshing state.

## 3. Deployment

- **Network:** Ethereum Sepolia
- **Chain ID:** 11155111
- **Contract address:** Not recorded
- **Transaction hash:** Not recorded
- **Explorer URL:** Generated from a runtime transaction hash; no hash is recorded
- **Method:** Run the Next.js development server and use MetaMask in the browser.
- **Environment:** `NEXT_PUBLIC_CONTRACT_ADDRESS`

No deployment or transaction was broadcast during this documentation task.

## 4. How to test it

Prerequisite: Node.js, a browser with MetaMask, and a Sepolia account:

```powershell
cd session-02
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`, connect MetaMask, select Sepolia, click **Get Message**, enter a non-empty message, and click **Update Message**. Expected results are a displayed address and chain ID, the contract message, a pending state while MetaMask confirms, and a confirmed state after mining. Negative test: leave the message empty or switch to another chain; the page must show an error and must not submit a write.

## 5. What I found difficult

Injected-wallet availability, account/network changes, contract-address configuration, and asynchronous transaction confirmation all need separate UI handling. The page clears stale state when MetaMask changes accounts or chains. The contract deployment information is not present in the source.

## 6. Acknowledgements

This work uses Next.js, React, TypeScript, ethers.js, MetaMask, and Ethereum Sepolia documentation. ChatGPT and GitHub Copilot may be used for learning, debugging assistance, and documentation.
