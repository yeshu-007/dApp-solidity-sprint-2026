
"use client";

import { useEffect, useState } from "react";
import { BrowserProvider, Contract } from "ethers";
import { contractABI } from "@/lib/contract";

type EthereumProvider = {
    request: (args: {
        method: string;
        params?: unknown[];
    }) => Promise<any>;
    on?: (
        event: string,
        handler: (...args: any[]) => void
    ) => void;
    removeListener?: (
        event: string,
        handler: (...args: any[]) => void
    ) => void;
};

declare global {
    interface Window {
        ethereum?: EthereumProvider;
    }
}

type TransactionStatus =
    | "idle"
    | "pending"
    | "confirmed"
    | "failed";

const SEPOLIA_CHAIN_ID = 11155111n;

export default function Home() {
    const [address, setAddress] = useState("");
    const [chainId, setChainId] = useState("");
    const [message, setMessage] = useState("");
    const [newMessage, setNewMessage] =
        useState("Hello From the Browser");
    const [error, setError] = useState("");
    const [txHash, setTxHash] = useState("");
    const [txStatus, setTxStatus] =
        useState<TransactionStatus>("idle");

    const contractAddress =
        process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";

    async function connectWallet() {
        setError("");

        try {
            if (!window.ethereum) {
                throw new Error("Please install MetaMask.");
            }

            const accounts = await window.ethereum.request({
                method: "eth_requestAccounts"
            }) as string[];

            if (!accounts.length) {
                throw new Error("No wallet account was selected.");
            }

            const provider = new BrowserProvider(
                window.ethereum as any
            );

            const network = await provider.getNetwork();

            setAddress(accounts[0]);
            setChainId(network.chainId.toString());
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Wallet connection failed."
            );
        }
    }

    async function getMessage() {
        setError("");

        try {
            if (!window.ethereum) {
                throw new Error("Please install MetaMask.");
            }

            if (!contractAddress) {
                throw new Error(
                    "Set NEXT_PUBLIC_CONTRACT_ADDRESS in your environment."
                );
            }

            const provider = new BrowserProvider(
                window.ethereum as any
            );

            const contract = new Contract(
                contractAddress,
                contractABI,
                provider
            );

            const result: string =
                await contract.getMessage();

            setMessage(result);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Could not read the contract."
            );
        }
    }

    async function updateMessage() {
        setError("");
        setTxHash("");
        setTxStatus("pending");

        try {
            if (!window.ethereum) {
                throw new Error("Please install MetaMask.");
            }

            if (!contractAddress) {
                throw new Error(
                    "Set NEXT_PUBLIC_CONTRACT_ADDRESS in your environment."
                );
            }

            if (!newMessage.trim()) {
                throw new Error("Enter a message first.");
            }

            const provider = new BrowserProvider(
                window.ethereum as any
            );

            const network = await provider.getNetwork();
            setChainId(network.chainId.toString());

            if (network.chainId !== SEPOLIA_CHAIN_ID) {
                throw new Error(
                    "Switch MetaMask to Ethereum Sepolia."
                );
            }

            const signer = await provider.getSigner();

            const contract = new Contract(
                contractAddress,
                contractABI,
                signer
            );

            // Ask MetaMask to approve the transaction.
            const tx = await contract.setMessage(newMessage);

            setTxHash(tx.hash);

            // Wait for the transaction to be mined.
            const receipt = await tx.wait();

            if (!receipt || receipt.status !== 1) {
                throw new Error("Transaction failed.");
            }

            // Read the updated state after confirmation.
            const readContract = new Contract(
                contractAddress,
                contractABI,
                provider
            );

            const updatedMessage: string =
                await readContract.getMessage();

            setMessage(updatedMessage);
            setTxStatus("confirmed");
        } catch (err) {
            setTxStatus("failed");

            setError(
                err instanceof Error
                    ? err.message
                    : "Transaction failed."
            );
        }
    }

    // React to account or network changes in MetaMask.
    useEffect(() => {
        const ethereum = window.ethereum;

        if (!ethereum?.on) {
            return;
        }

        function handleAccountsChanged(accounts: string[]) {
            setAddress(accounts[0] ?? "");
            setTxHash("");
            setTxStatus("idle");
            setError("");

            if (!accounts.length) {
                setMessage("");
            }
        }

        function handleChainChanged(hexChainId: string) {
            setChainId(
                BigInt(hexChainId).toString()
            );

            setMessage("");
            setTxHash("");
            setTxStatus("idle");
            setError("");
        }

        ethereum.on(
            "accountsChanged",
            handleAccountsChanged
        );

        ethereum.on(
            "chainChanged",
            handleChainChanged
        );

        return () => {
            ethereum.removeListener?.(
                "accountsChanged",
                handleAccountsChanged
            );

            ethereum.removeListener?.(
                "chainChanged",
                handleChainChanged
            );
        };
    }, []);

    return (
        <main style={{ padding: 24, maxWidth: 700 }}>
            <h1>MessageBoard dApp</h1>

            <section>
                <h2>1. Wallet Connection</h2>

                <button onClick={connectWallet}>
                    Connect Wallet
                </button>

                <p>
                    Address: {address || "Not connected"}
                </p>

                <p>
                    Chain ID: {chainId || "Unknown"}
                </p>

                {chainId &&
                    BigInt(chainId) !== SEPOLIA_CHAIN_ID && (
                        <p>
                            Switch MetaMask to Sepolia before writing.
                        </p>
                    )}
            </section>

            <section style={{ marginTop: 24 }}>
                <h2>2. Read Contract State</h2>

                <button onClick={getMessage}>
                    Get Message
                </button>

                <p>
                    Contract message: {message || "Not loaded"}
                </p>
            </section>

            <section style={{ marginTop: 24 }}>
                <h2>3. Update Contract State</h2>

                <input
                    value={newMessage}
                    onChange={(event) =>
                        setNewMessage(event.target.value)
                    }
                    placeholder="Enter a new message"
                />

                <button
                    onClick={updateMessage}
                    disabled={txStatus === "pending"}
                    style={{ marginLeft: 8 }}
                >
                    {txStatus === "pending"
                        ? "Transaction Pending..."
                        : "Update Message"}
                </button>

                <p>Transaction status: {txStatus}</p>

                {txHash && (
                    <p>
                        Transaction hash:{" "}
                        <a
                            href={`https://sepolia.etherscan.io/tx/${txHash}`}
                            target="_blank"
                            rel="noreferrer"
                        >
                            View on Sepolia Etherscan
                        </a>
                    </p>
                )}

                {txStatus === "confirmed" && (
                    <p>Transaction confirmed successfully.</p>
                )}

                {error && (
                    <p style={{ color: "red" }}>
                        Error: {error}
                    </p>
                )}
            </section>
        </main>
    );
}
