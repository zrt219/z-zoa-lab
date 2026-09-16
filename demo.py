import os
import sys
import json
import uuid
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Demo uses testnet faucet directly to generate wallet; no hardcoded secrets needed.
from research.ledger.anchor import anchor_run
from research.ledger.verify import verify_anchor
from research.ledger.xrpl_client import get_xrpl_client, get_testnet_wallet

def main():
    run_id = f"SYNTHETIC-{uuid.uuid4().hex[:6]}"
    runs_dir = Path("runs")
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"--- 1. Creating synthetic run: {run_id} ---")
    manifest = {
        "run_id": run_id,
        "git_commit": "abcdef1",
        "datasets": [],
        "manifest_sha256": "fake_hash_value"
    }
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)
        
    print("--- 2. Anchoring run on XRPL Testnet ---")
    client = get_xrpl_client()
    from xrpl.wallet import generate_faucet_wallet
    
    print("Funding a temporary wallet from Testnet faucet...")
    wallet = generate_faucet_wallet(client, debug=True)
    
    receipt = anchor_run(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        runs_root=runs_dir,
        client=client,
        wallet=wallet
    )
    print(f"Anchored! TX Hash: {receipt.tx_hash}")
    
    print("--- 3. Verifying transaction ---")
    res = verify_anchor(run_id, "PREDICTION_FROZEN", runs_root=runs_dir, client=client)
    print(res.audit_report)
    assert res.is_valid(), "Verification should succeed"
    
    print("--- 4. Mutating manifest ---")
    manifest["git_commit"] = "badc0de"
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)
        
    print("--- 5. Verifying mutated transaction ---")
    res_mutated = verify_anchor(run_id, "PREDICTION_FROZEN", runs_root=runs_dir, client=client)
    print(res_mutated.audit_report)
    assert not res_mutated.is_valid(), "Verification MUST fail after mutation"
    
    print("--- DEMONSTRATION SUCCESSFUL ---")

if __name__ == '__main__':
    main()
