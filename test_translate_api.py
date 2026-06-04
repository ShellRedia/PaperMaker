"""Test backend translate endpoints"""
import asyncio, sys, json, httpx
import uvicorn, threading, time

sys.path.insert(0, ".")

from backend.main import create_app
app = create_app()

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=17892, log_level="warning")

t = threading.Thread(target=run_server, daemon=True)
t.start()

for _ in range(30):
    try:
        r = httpx.get("http://127.0.0.1:17892/health", timeout=0.3)
        if r.status_code == 200:
            print("[OK] Backend ready")
            break
    except:
        time.sleep(0.1)
else:
    print("[FAIL] Backend startup timeout")
    sys.exit(1)

async def test():
    print("\n--- Test POST /api/translate (non-stream) ---")
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "http://127.0.0.1:17892/api/translate",
            json={"text": "SAM is the most common segmentation model", "history": []},
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", {})
            print(f"English: {result.get('english', 'N/A')[:200]}")
            print(f"Chinese: {result.get('chinese', 'N/A')[:200]}")
        else:
            print(f"Error: {resp.text[:500]}")

    print("\n--- Test POST /api/translate/stream (SSE) ---")
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            "http://127.0.0.1:17892/api/translate/stream",
            json={"text": "transformer is a neural network architecture based on self-attention", "history": []},
        ) as resp:
            print(f"Status: {resp.status_code}")
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    chunk = json.loads(line[6:])
                    t = chunk.get("type", "?")
                    if t == "token":
                        tok = chunk["payload"]["token"]
                        # Safely print token content
                        print(f"  -> token: {repr(tok)}")
                    elif t == "done":
                        p = chunk["payload"]
                        print(f"  => done: english={repr(p.get('english','')[:100])}")
                        print(f"           chinese={repr(p.get('chinese','')[:100])}")
                    elif t == "error":
                        print(f"  !! error: {chunk['payload'][:200]}")

asyncio.run(test())
