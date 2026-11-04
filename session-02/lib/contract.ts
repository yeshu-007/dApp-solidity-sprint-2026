export const contractABI = [
    {
        type: "function",
        name: "getMessage",
        stateMutability: "view",
        inputs: [],
        outputs: [{ name: "", type: "string" }]
    },
    {
        type: "function",
        name: "setMessage",
        stateMutability: "nonpayable",
        inputs: [{ name: "newMessage", type: "string" }],
        outputs: []
    }
] as const;