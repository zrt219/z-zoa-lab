import urllib.request
import urllib.error
import ssl
import json
import time
import certifi

def test_endpoint(name, url, ctx=None, max_retries=2):
    headers = {"User-Agent": "Mozilla/5.0", "Connection": "close"}
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                print(f"[SUCCESS] {name}")
                print(f"  URL:    {url}")
                print(f"  Status: {resp.status} {resp.reason}")
                server = resp.headers.get("Server", "N/A")
                content_type = resp.headers.get("Content-Type", "N/A")
                print(f"  Server: {server} | Content-Type: {content_type}")
                if "json" in content_type:
                    try:
                        parsed = json.loads(data)
                        print(f"  Payload: {json.dumps(parsed, indent=2)}")
                    except Exception:
                        print(f"  Body: {data[:120]}...")
                else:
                    first_line = data.strip().split("\n")[0]
                    print(f"  Snippet: {first_line[:80]}... (Total bytes: {len(data)})")
                print()
                return True, data
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries:
                print(f"[RETRY] {name} hit rate limit (HTTP 429), waiting 2s before retry {attempt + 1}/{max_retries}...")
                time.sleep(2)
                continue
            print(f"[FAILURE] {name}")
            print(f"  URL:   {url}")
            print(f"  Error: HTTPError: HTTP Error {e.code}: {e.reason}\n")
            return False, str(e)
        except Exception as e:
            print(f"[FAILURE] {name}")
            print(f"  URL:   {url}")
            print(f"  Error: {type(e).__name__}: {e}\n")
            return False, str(e)

if __name__ == "__main__":
    print("=" * 65)
    print(" Z-ZOA APPLICATION & INSTABOX BRIDGE CONNECTIVITY VERIFICATION")
    print("=" * 65)
    print()

    results = []

    # 1. Local backend
    res, _ = test_endpoint("Local Backend API Documentation", "http://127.0.0.1:8000/docs")
    results.append(res)
    res, _ = test_endpoint("Local Backend Health Check", "http://127.0.0.1:8000/health")
    results.append(res)

    # 2. Local frontend
    res, _ = test_endpoint("Local Vite Frontend (No Trailing Slash)", "http://127.0.0.1:5173")
    results.append(res)
    res, _ = test_endpoint("Local Vite Frontend (App Shell)", "http://127.0.0.1:5173/")
    results.append(res)
    res, _ = test_endpoint("Local Vite Proxy Bridge -> Backend Health", "http://127.0.0.1:5173/health")
    results.append(res)

    # 3. Remote Instabox
    cert_ctx = ssl.create_default_context(cafile=certifi.where())
    res, _ = test_endpoint("Remote Instabox Swagger Documentation", "https://8000-agqvnks4mnchkhag5feiobn63u.instabox.tech/docs", ctx=cert_ctx)
    results.append(res)
    res, _ = test_endpoint("Remote Instabox Health Check", "https://8000-agqvnks4mnchkhag5feiobn63u.instabox.tech/health", ctx=cert_ctx)
    results.append(res)

    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f">>> ALL {total} ENDPOINTS VERIFIED SUCCESSFULLY ({passed}/{total} PASS) <<<")
    else:
        print(f">>> VERIFICATION FAILED: {total - passed} endpoint(s) failed <<<")
        exit(1)
