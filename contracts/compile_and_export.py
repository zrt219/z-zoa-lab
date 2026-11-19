"""Compile/Export ABI for ResearchNotary.sol."""

import json
from pathlib import Path

CONTRACT_DIR = Path(__file__).resolve().parent

ABI = [
    {
        "inputs": [],
        "name": "EmptyRunId",
        "type": "error"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "runId", "type": "string"},
            {"internalType": "enum ResearchNotary.ResearchStage", "name": "attempted", "type": "uint8"},
            {"internalType": "int8", "name": "currentLatest", "type": "int8"}
        ],
        "name": "InvalidStageProgression",
        "type": "error"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "runId", "type": "string"},
            {"internalType": "enum ResearchNotary.ResearchStage", "name": "stage", "type": "uint8"},
            {"internalType": "bytes32", "name": "existingHash", "type": "bytes32"}
        ],
        "name": "StageAlreadyAnchored",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "ZeroPayloadHash",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "runId", "type": "string"},
            {"indexed": True, "internalType": "enum ResearchNotary.ResearchStage", "name": "stage", "type": "uint8"},
            {"indexed": True, "internalType": "bytes32", "name": "payloadHash", "type": "bytes32"},
            {"indexed": False, "internalType": "bytes32", "name": "previousTxOrHash", "type": "bytes32"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": False, "internalType": "address", "name": "notarizer", "type": "address"}
        ],
        "name": "ResearchStageAnchored",
        "type": "event"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "runId", "type": "string"},
            {"internalType": "enum ResearchNotary.ResearchStage", "name": "stage", "type": "uint8"},
            {"internalType": "bytes32", "name": "payloadHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "previousTxOrHash", "type": "bytes32"}
        ],
        "name": "anchorStage",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "runId", "type": "string"},
            {"internalType": "enum ResearchNotary.ResearchStage", "name": "stage", "type": "uint8"}
        ],
        "name": "getStage",
        "outputs": [
            {"internalType": "bytes32", "name": "payloadHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "previousTxOrHash", "type": "bytes32"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "address", "name": "notarizer", "type": "address"},
            {"internalType": "bool", "name": "exists", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "runId", "type": "string"},
            {"internalType": "enum ResearchNotary.ResearchStage", "name": "stage", "type": "uint8"}
        ],
        "name": "isStageAnchored",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "runId", "type": "string"}
        ],
        "name": "getRunLatestStage",
        "outputs": [{"internalType": "int8", "name": "", "type": "int8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "runId", "type": "string"},
            {"internalType": "enum ResearchNotary.ResearchStage", "name": "stage", "type": "uint8"},
            {"internalType": "bytes32", "name": "payloadHash", "type": "bytes32"}
        ],
        "name": "verifyPayloadHash",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Standard contract definition
CONTRACT_DATA = {
    "contractName": "ResearchNotary",
    "chainId": 1440002,
    "network": "XRPL EVM Sidechain Testnet",
    "rpcUrl": "https://rpc.xrplevm.org",
    "explorerUrl": "https://explorer.xrplevm.org",
    "defaultContractAddress": "0x7a3B05C339F80D1b681997d91799FaA7dE442436",
    "abi": ABI,
}


def export_abi():
    target = CONTRACT_DIR / "ResearchNotary.json"
    with open(target, "w", encoding="utf-8") as f:
        json.dump(CONTRACT_DATA, f, indent=2)
    print(f"Exported contract definition to {target}")


if __name__ == "__main__":
    export_abi()
