import base64
import os
import subprocess
import sys
from pathlib import Path

def upload(local_file: str, remote_file: str):
    p = Path(local_file)
    if not p.exists():
        print(f"File {local_file} does not exist")
        return False
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode('ascii')
    
    instabox_exe = os.environ.get("INSTABOX_EXE", "instabox")
    remote_box = os.environ.get("INSTABOX_BOX_ID", "sandbox")
    cmd = [
        instabox_exe,
        "exec",
        remote_box,
        "--",
        f"python3 -c \"import base64; from pathlib import Path; p = Path('{remote_file}'); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(base64.b64decode('{b64}'))\""
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✓ Uploaded {local_file} -> {remote_file}")
        return True
    else:
        print(f"❌ Failed: {res.stderr}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_to_instabox.py <local_path> <remote_path>")
        sys.exit(1)
    upload(sys.argv[1], sys.argv[2])
