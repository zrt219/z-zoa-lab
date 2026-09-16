"""CLI command parser and execution dispatcher for Z-ZOA."""

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from research.ledger import (
    anchor_run,
    verify_anchor,
    verify_chain,
    check_testnet_connectivity,
    bootstrap_testnet_account,
    get_account_status,
)
from research.ledger.xrpl_client import load_testnet_credentials


def main():
    parser = argparse.ArgumentParser(
        prog="zzoa",
        description="Z-ZOA Calculation Room CLI: Research workbench and XRPL notarization"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # --- Ledger Subparser ---
    ledger_parser = subparsers.add_parser("ledger", help="XRPL Testnet run anchoring & verification")
    ledger_sub = ledger_parser.add_subparsers(dest="ledger_action", help="Ledger actions")

    # ledger status
    ledger_sub.add_parser("status", help="Check XRPL Testnet connectivity and account status")

    # ledger bootstrap-account
    ledger_sub.add_parser("bootstrap-account", help="Bootstrap and fund a research account via Testnet faucet")

    # ledger anchor
    anchor_cmd = ledger_sub.add_parser("anchor", help="Anchor a frozen research run to XRPL Testnet")
    anchor_cmd.add_argument("--run", required=True, help="Unique run identifier (e.g. VELA-0017)")
    anchor_cmd.add_argument("--stage", required=True, help="Research stage (e.g. PREDICTION_FROZEN)")
    anchor_cmd.add_argument("--previous", default=None, help="Optional previous transaction hash")
    anchor_cmd.add_argument("--runs-dir", default="runs", help="Runs root directory")

    # ledger verify
    verify_cmd = ledger_sub.add_parser("verify", help="Verify cryptographic integrity of a run anchor")
    verify_cmd.add_argument("--run", required=True, help="Unique run identifier")
    verify_cmd.add_argument("--stage", required=True, help="Research stage")
    verify_cmd.add_argument("--runs-dir", default="runs", help="Runs root directory")

    # ledger verify-chain
    chain_cmd = ledger_sub.add_parser("verify-chain", help="Verify chronological chain of research anchors")
    chain_cmd.add_argument("--run", required=True, help="Unique run identifier")
    chain_cmd.add_argument("--runs-dir", default="runs", help="Runs root directory")

    args = parser.parse_args()

    if args.command == "ledger":
        handle_ledger(args)
    else:
        parser.print_help()
        sys.exit(1)


def handle_ledger(args):
    action = args.ledger_action
    if action == "status":
        conn = check_testnet_connectivity()
        creds = load_testnet_credentials()
        address = creds.get("address")
        print("=" * 60)
        print("Z-ZOA XRPL TESTNET STATUS")
        print("=" * 60)
        print(f"Network:          XRPL Testnet (ID 1)")
        print(f"Connection:       {'ONLINE' if conn.get('online') else 'OFFLINE'}")
        if conn.get("online"):
            print(f"Server Version:   {conn.get('server_version')}")
            print(f"Ledgers:          {conn.get('complete_ledgers')}")
        print(f"Account Address:  {address or 'None configured (run: python -m zzoa ledger bootstrap-account)'}")
        if address:
            st = get_account_status(address)
            if st.get("balance_drops"):
                xrp = int(st["balance_drops"]) / 1_000_000
                print(f"Balance:          {xrp:,.2f} XRP (Testnet)")
                print(f"Sequence:         {st.get('sequence')}")
        print(f"Disclaimer:       DEVELOPMENT RECORD XRPL TESTNET NOT A PERMANENT PUBLICATION ARCHIVE")
        print("=" * 60)

    elif action == "bootstrap-account":
        print("Bootstrapping dedicated Z-ZOA Testnet research account from faucet...")
        try:
            res = bootstrap_testnet_account()
            print("✓ Account funded successfully.")
            print(f"Public Address: {res['classic_address']}")
            print(f"Saved to:       {res['saved_to']} (local gitignored file)")
            print("NOTE: Seed key has been isolated locally and will never be shared.")
        except Exception as e:
            print(f"✗ Failed to bootstrap account: {e}", file=sys.stderr)
            sys.exit(1)

    elif action == "anchor":
        print(f"Anchoring Run '{args.run}' at stage '{args.stage}'...")
        try:
            receipt = anchor_run(
                run_id=args.run,
                stage=args.stage,
                runs_root=args.runs_dir,
                previous_tx_hash=args.previous,
            )
            print("✓ ANCHOR VALIDATED ON XRPL TESTNET")
            print(f"Run ID:            {receipt.run_id}")
            print(f"Stage:             {receipt.stage}")
            print(f"Anchor Hash:       {receipt.anchor_payload_sha256}")
            print(f"Transaction:       {receipt.tx_hash}")
            print(f"Ledger Index:      {receipt.ledger_index}")
            print(f"Previous TX:       {receipt.previous_tx_hash or 'None (Chain Origin)'}")
            print(f"Validated At:      {receipt.validated_at}")
            print(f"Receipt written to: runs/{args.run}/xrpl_receipt_{args.stage}.json")
        except Exception as e:
            print(f"✗ Anchoring failed: {e}", file=sys.stderr)
            sys.exit(1)

    elif action == "verify":
        res = verify_anchor(
            run_id=args.run,
            stage=args.stage,
            runs_root=args.runs_dir,
        )
        print(res.audit_report)
        if not res.is_valid():
            sys.exit(1)

    elif action == "verify-chain":
        res = verify_chain(
            run_id=args.run,
            runs_root=args.runs_dir,
        )
        print("=" * 60)
        print(f"Z-ZOA CHRONOLOGICAL RESEARCH CHAIN AUDIT: RUN {args.run}")
        print("=" * 60)
        print(res["audit_report"])
        print("-" * 60)
        print(f"Stages Verified:  {res['stages_verified']}")
        print(f"Chain Status:     {res['status']}")
        print("=" * 60)
        if not res["chain_valid"]:
            sys.exit(1)

    else:
        print("No action specified. Use --help for available actions.")
        sys.exit(1)
