"""XRPL Testnet client management, connection, and secret isolation."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union

from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.requests import AccountInfo, ServerInfo
from xrpl.models.response import ResponseStatus


DEFAULT_TESTNET_RPC = "https://s.altnet.rippletest.net:51234"
TESTNET_NETWORK_ID = 1
SECRETS_DIR_NAME = ".secrets"
SECRETS_FILE_NAME = "xrpl_testnet.json"


def get_base_dir() -> Path:
    """Resolve project base directory."""
    return Path(__file__).resolve().parent.parent.parent


def get_xrpl_client(rpc_url: Optional[str] = None) -> JsonRpcClient:
    """Obtain an XRPL JSON-RPC client targeting XRPL Testnet."""
    url = rpc_url or os.getenv("XRPL_TESTNET_RPC_URL") or DEFAULT_TESTNET_RPC
    return JsonRpcClient(url)


def check_testnet_connectivity(client: Optional[JsonRpcClient] = None) -> Dict[str, Any]:
    """Verify connectivity to XRPL Testnet."""
    c = client or get_xrpl_client()
    try:
        resp = c.request(ServerInfo())
        if resp.status == ResponseStatus.SUCCESS:
            info = resp.result.get("info", {})
            return {
                "online": True,
                "network": "XRPL Testnet",
                "server_version": info.get("build_version", "unknown"),
                "complete_ledgers": info.get("complete_ledgers", "unknown"),
                "network_id": TESTNET_NETWORK_ID,
            }
        return {"online": False, "error": f"Server status: {resp.status}"}
    except Exception as e:
        return {"online": False, "error": str(e)}


def load_testnet_credentials(base_dir: Optional[Union[str, Path]] = None) -> Dict[str, Optional[str]]:
    """
    Load testnet signing credentials safely:
    1. Environment variables (XRPL_TESTNET_SECRET, XRPL_TESTNET_ADDRESS)
    2. Gitignored .secrets/xrpl_testnet.json file
    Never returns secrets to untrusted loggers.
    """
    secret = os.getenv("XRPL_TESTNET_SECRET") or os.getenv("XRPL_TESTNET_SEED")
    address = os.getenv("XRPL_TESTNET_ADDRESS")

    if secret:
        if not address:
            try:
                wallet = Wallet.from_seed(secret)
                address = wallet.classic_address
            except Exception:
                pass
        return {"address": address, "secret": secret}

    # Check local gitignored .secrets file
    root = Path(base_dir) if base_dir else get_base_dir()
    secret_path = root / SECRETS_DIR_NAME / SECRETS_FILE_NAME
    if secret_path.exists():
        try:
            with open(secret_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "address": data.get("classic_address") or data.get("address"),
                    "secret": data.get("seed") or data.get("secret"),
                }
        except Exception:
            pass

    return {"address": None, "secret": None}


def get_testnet_wallet(base_dir: Optional[Union[str, Path]] = None) -> Wallet:
    """
    Construct Wallet instance for signing transactions.
    Fails loudly if no signing credential is configured.
    """
    creds = load_testnet_credentials(base_dir=base_dir)
    secret = creds.get("secret")
    if not secret:
        raise RuntimeError(
            "XRPL Testnet signing key not configured.\n"
            "Set environment variable XRPL_TESTNET_SECRET or run:\n"
            "python -m zzoa ledger bootstrap-account"
        )
    return Wallet.from_seed(secret)


def bootstrap_testnet_account(
    client: Optional[JsonRpcClient] = None,
    base_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Bootstrap a dedicated Testnet research account using the official XRPL Testnet faucet.
    Saves credentials into gitignored .secrets/xrpl_testnet.json.
    Returns only the public address and status (never exposes secret in logs).
    """
    c = client or get_xrpl_client()
    root = Path(base_dir) if base_dir else get_base_dir()
    secrets_dir = root / SECRETS_DIR_NAME
    secrets_dir.mkdir(parents=True, exist_ok=True)
    secrets_file = secrets_dir / SECRETS_FILE_NAME

    # Request funded wallet from official faucet
    wallet = generate_faucet_wallet(c)

    # Save to local gitignored secrets file
    secret_payload = {
        "network": "XRPL Testnet",
        "classic_address": wallet.classic_address,
        "seed": wallet.seed,
    }
    with open(secrets_file, "w", encoding="utf-8") as f:
        json.dump(secret_payload, f, indent=2)

    return {
        "status": "BOOTSTRAP_SUCCESS",
        "network": "XRPL Testnet",
        "classic_address": wallet.classic_address,
        "funded": True,
        "saved_to": str(secrets_file),
    }


def get_account_status(
    address: Optional[str] = None,
    client: Optional[JsonRpcClient] = None,
    base_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Fetch live account info (balance, sequence) from XRPL Testnet."""
    c = client or get_xrpl_client()
    if not address:
        creds = load_testnet_credentials(base_dir=base_dir)
        address = creds.get("address")

    if not address:
        return {
            "configured": False,
            "error": "No account address configured."
        }

    try:
        req = AccountInfo(account=address, ledger_index="validated")
        resp = c.request(req)
        if resp.status == ResponseStatus.SUCCESS:
            data = resp.result.get("account_data", {})
            return {
                "configured": True,
                "address": address,
                "balance_drops": data.get("Balance"),
                "sequence": data.get("Sequence"),
                "ledger_index": resp.result.get("ledger_index"),
                "validated": True,
            }
        else:
            return {
                "configured": True,
                "address": address,
                "error": str(resp.result.get("error_message") or resp.result.get("error")),
            }
    except Exception as e:
        return {
            "configured": True,
            "address": address,
            "error": str(e),
        }
