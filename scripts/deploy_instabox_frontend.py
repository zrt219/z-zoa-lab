"""Deploy updated frontend bundle and experiment run artifacts to Instabox sandbox instance."""

import base64
import io
import json
import os
import ssl
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path
import certifi

INSTABOX_EXE = os.environ.get("INSTABOX_EXE", "instabox")
REMOTE_BOX = os.environ.get("INSTABOX_BOX_ID", "sandbox")
REMOTE_WORKSPACE = "/data/home/workspace/Z-zoa-lab"
LOCAL_ROOT = Path(__file__).resolve().parent.parent


def run_remote_cmd(remote_cmd: str, stdin_data: bytes = None) -> subprocess.CompletedProcess:
    cmd = [
        INSTABOX_EXE,
        "exec",
        REMOTE_BOX,
    ]
    if stdin_data is not None:
        cmd.append("--stdin")
    cmd.extend(["--", remote_cmd])
    return subprocess.run(cmd, input=stdin_data, capture_output=True)


def stream_upload_archive(data: bytes, remote_tmp_path: str, chunk_size: int = 500_000) -> bool:
    """Upload binary data via 500KB chunked base64 stdin to stay under 1MB limit."""
    b64_data = base64.b64encode(data)
    run_remote_cmd(f"rm -f {remote_tmp_path}")
    total_chunks = (len(b64_data) + chunk_size - 1) // chunk_size
    print(f"[*] Streaming {len(data):,} bytes ({total_chunks} parts) to {remote_tmp_path}...")

    for idx, i in enumerate(range(0, len(b64_data), chunk_size)):
        chunk = b64_data[i : i + chunk_size]
        res = run_remote_cmd(f"base64 -d >> {remote_tmp_path}", stdin_data=chunk)
        if res.returncode != 0:
            print(f"❌ Chunk {idx+1}/{total_chunks} failed: {res.stderr.decode()}")
            return False
        print(f"  Sent part {idx+1}/{total_chunks} ({len(chunk):,} bytes)")

    # Verify size
    check_res = run_remote_cmd(f"stat -c %s {remote_tmp_path}")
    remote_size = int(check_res.stdout.decode().strip().splitlines()[-1])
    if remote_size != len(data):
        print(f"❌ Size mismatch: expected {len(data)}, got {remote_size}")
        return False
    print(f"✓ Verified archive on remote ({remote_size:,} bytes)")
    return True


def package_directory(source_dir: Path, arcname: str) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(str(source_dir), arcname=arcname)
    return buf.getvalue()


def deploy(target_runs=None):
    if target_runs is None:
        target_runs = ["GA-001", "WALLABY-001"]

    print("=" * 70)
    print(" Z-ZOA LIVE INSTABOX FRONTEND & RUN DEPLOYMENT")
    print(f" Target: {REMOTE_BOX} | Workspace: {REMOTE_WORKSPACE}")
    print("=" * 70)

    # 1. Package frontend dist
    dist_dir = LOCAL_ROOT / "frontend" / "dist"
    if not dist_dir.exists():
        print("❌ frontend/dist does not exist. Run 'npm run build' first.")
        sys.exit(1)

    print("\n[1/5] Packaging frontend/dist...")
    dist_tar = package_directory(dist_dir, arcname="dist")
    print(f"  frontend/dist archive size: {len(dist_tar):,} bytes (gzipped)")

    # 2. Stream upload frontend bundle and extract
    print("\n[2/5] Streaming frontend bundle to Instabox...")
    remote_dist_tar = "/tmp/frontend_dist.tar.gz"
    if not stream_upload_archive(dist_tar, remote_dist_tar):
        sys.exit(1)

    print("  Extracting frontend bundle on remote...")
    extract_dist_cmd = f"tar -xzf {remote_dist_tar} -C {REMOTE_WORKSPACE}/frontend/ && rm -f {remote_dist_tar}"
    res = run_remote_cmd(extract_dist_cmd)
    if res.returncode != 0:
        print(f"❌ Frontend extraction failed: {res.stderr.decode()}")
        sys.exit(1)
    print("  ✓ Frontend bundle unpacked to remote workspace")

    # 3. Stream upload run directories if available
    print("\n[3/5] Packaging and streaming experiment runs...")
    for run_name in target_runs:
        run_dir = LOCAL_ROOT / "runs" / run_name
        if run_dir.exists():
            print(f"\n  Packaging runs/{run_name}...")
            run_tar = package_directory(run_dir, arcname=run_name)
            remote_run_tar = f"/tmp/runs_{run_name.lower().replace('-', '_')}.tar.gz"
            if stream_upload_archive(run_tar, remote_run_tar):
                extract_run_cmd = f"mkdir -p {REMOTE_WORKSPACE}/runs && tar -xzf {remote_run_tar} -C {REMOTE_WORKSPACE}/runs/ && rm -f {remote_run_tar}"
                r_res = run_remote_cmd(extract_run_cmd)
                if r_res.returncode == 0:
                    print(f"  ✓ runs/{run_name} unpacked to remote workspace")
                else:
                    print(f"  ⚠️ Warning: {run_name} extraction failed: {r_res.stderr.decode()}")
        else:
            print(f"  ℹ️ runs/{run_name} not found locally, skipping.")

    # 4. Restart z-zoa.service and verify
    print("\n[4/5] Restarting z-zoa.service on Instabox...")
    restart_res = run_remote_cmd("sudo systemctl restart z-zoa")
    if restart_res.returncode != 0:
        print(f"❌ Restart failed: {restart_res.stderr.decode()}")
        sys.exit(1)

    time.sleep(3)

    status_res = run_remote_cmd("systemctl is-active z-zoa")
    status = status_res.stdout.decode().strip().splitlines()[-1]
    print(f"  Service status: {status}")
    if status != "active":
        print(f"❌ Service is not active! Output: {status_res.stdout.decode()}")
        sys.exit(1)
    print("  ✓ systemctl is-active z-zoa -> ACTIVE")

    # 5. Remote HTTP Verification
    print("\n[5/5] Verifying remote live endpoints...")
    base_url = "https://8000-agqvnks4mnchkhag5feiobn63u.instabox.tech"
    cert_ctx = ssl.create_default_context(cafile=certifi.where())
    headers = {"User-Agent": "Mozilla/5.0"}

    # Test /health with retry for server startup
    healthy = False
    for attempt in range(5):
        try:
            req = urllib.request.Request(f"{base_url}/health", headers=headers)
            with urllib.request.urlopen(req, context=cert_ctx, timeout=10) as r:
                body = json.loads(r.read().decode())
                print(f"  ✓ Remote /health: {body}")
                healthy = True
                break
        except Exception as e:
            print(f"  ... waiting for uvicorn to boot (attempt {attempt + 1}/5): {e}")
            time.sleep(3)

    if not healthy:
        print("❌ /health check failed after retries.")
        sys.exit(1)

    # Test /experiments/runs
    try:
        req = urllib.request.Request(f"{base_url}/experiments/runs", headers=headers)
        with urllib.request.urlopen(req, context=cert_ctx, timeout=10) as r:
            runs = json.loads(r.read().decode())
            run_ids = [run["run_id"] for run in runs]
            print(f"  ✓ Remote /experiments/runs ({len(runs)} runs listed): {run_ids[:6]}...")
            assert "VELA-001" in run_ids, "VELA-001 missing on remote!"
            print("  ✓ VELA-001 verified on live remote API!")
            if (LOCAL_ROOT / "runs" / "GA-001").exists():
                assert "GA-001" in run_ids, "GA-001 missing on remote!"
                print("  ✓ GA-001 verified on live remote API!")
            if (LOCAL_ROOT / "runs" / "WALLABY-001").exists():
                assert "WALLABY-001" in run_ids, "WALLABY-001 missing on remote!"
                print("  ✓ WALLABY-001 verified on live remote API!")
    except Exception as e:
        print(f"  ❌ /experiments/runs check failed: {e}")
        sys.exit(1)

    # Test frontend root
    try:
        req = urllib.request.Request(f"{base_url}/", headers=headers)
        with urllib.request.urlopen(req, context=cert_ctx, timeout=10) as r:
            html = r.read().decode()
            print(f"  ✓ Remote frontend HTML served ({len(html)} bytes)")
            # Find the active bundle name from local dist
            local_js = list((dist_dir / "assets").glob("index-*.js"))
            if local_js:
                bundle_name = local_js[0].name
                if bundle_name in html:
                    print(f"  ✓ Verified: Live index.html points to updated bundle {bundle_name}!")
                else:
                    print(f"  ⚠️ Live index.html does not contain {bundle_name}")
    except Exception as e:
        print(f"  ❌ Frontend root check failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print(" LIVE DEPLOYMENT COMPLETE & VERIFIED")
    print("=" * 70)


if __name__ == "__main__":
    deploy()
