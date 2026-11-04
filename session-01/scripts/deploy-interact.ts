import "dotenv/config";
import fs from "node:fs";
import solc from "solc";
import {
    JsonRpcProvider,
    Wallet,
    ContractFactory,
    formatEther
} from "ethers";

// 1. Load environment variables
const rpcUrl = process.env.SEPOLIA_RPC_URL;
const privateKey = process.env.DEPLOYER_PRIVATE_KEY;

if (!rpcUrl || !privateKey) {
    throw new Error(
        "Missing SEPOLIA_RPC_URL or DEPLOYER_PRIVATE_KEY in .env"
    );
}

// 2. Connect to Sepolia
const provider = new JsonRpcProvider(rpcUrl);
const network = await provider.getNetwork();

if (network.chainId !== 11155111n) {
    throw new Error("Wrong network. Please connect to Sepolia.");
}

console.log("Connected to Ethereum Sepolia");
console.log("Chain ID:", network.chainId.toString());

// 3. Create the deployer wallet
const wallet = new Wallet(privateKey, provider);
const balance = await provider.getBalance(wallet.address);

console.log("Deployer address:", wallet.address);
console.log("Balance:", formatEther(balance), "Sepolia ETH");

// 4. Read the Solidity source code
const source = fs.readFileSync(
    "contracts/Storage.sol",
    "utf8"
);

// 5. Compile the Solidity contract
const input = {
    language: "Solidity",
    sources: {
        "Storage.sol": {
            content: source
        }
    },
    settings: {
        outputSelection: {
            "*": {
                "*": [
                    "abi",
                    "evm.bytecode.object"
                ]
            }
        }
    }
};

const compiled = JSON.parse(
    solc.compile(JSON.stringify(input))
);

if (compiled.errors) {
    for (const error of compiled.errors) {
        console.log(error.formattedMessage);
    }

    if (
        compiled.errors.some(
            (error: { severity: string }) =>
                error.severity === "error"
        )
    ) {
        throw new Error("Solidity compilation failed");
    }
}

const artifact = compiled.contracts?.["Storage.sol"]?.["Storage"];

if (!artifact || !artifact.evm.bytecode.object) {
    throw new Error("Contract ABI or bytecode is missing");
}

console.log("Contract compiled successfully");

// 6. Deploy the contract
const factory = new ContractFactory(
    artifact.abi,
    "0x" + artifact.evm.bytecode.object,
    wallet
);

console.log("Deploying contract...");

const contract = await factory.deploy();

await contract.waitForDeployment();

const contractAddress = await contract.getAddress();

console.log("Contract deployed at:", contractAddress);
console.log(
    "Deployment transaction:",
    contract.deploymentTransaction()?.hash
);

// 7. Read the initial state
const initialValue = await contract.retrieve();

console.log("Initial stored value:", initialValue.toString());

// 8. Send a transaction to update the state
console.log("Updating stored value to 25...");

const tx = await contract.store(25n);

console.log("Transaction hash:", tx.hash);

// 9. Wait for transaction confirmation
const receipt = await tx.wait();

if (!receipt || receipt.status !== 1) {
    throw new Error("State update transaction failed");
}

console.log("Transaction confirmed");

// 10. Read the updated state
const updatedValue = await contract.retrieve();

console.log("Updated stored value:", updatedValue.toString());
console.log("Assignment completed successfully");