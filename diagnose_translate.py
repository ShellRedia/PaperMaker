"""诊断翻译链路 — 从 DB 读取配置，测试 LLM API"""
import asyncio, sys, json, httpx
sys.path.insert(0, ".")
from backend.db.database import init_db, get_db
from sqlalchemy import select
from backend.db.schema import AppSettings

async def main():
    await init_db()

    # 1. 读配置
    async for db in get_db():
        result = await db.execute(
            select(AppSettings).where(
                AppSettings.key.in_(["llm_api_url", "llm_api_key", "llm_model_name"])
            )
        )
        rows = {r.key: r.value for r in result.scalars().all()}
        url = rows.get("llm_api_url", "")
        key = rows.get("llm_api_key", "")
        model = rows.get("llm_model_name", "")
        break

    print(f"URL: {url}")
    print(f"Key: {'SET' if key else 'NOT SET'} (length={len(key)})")
    print(f"Model: {model}")
    print()

    if not key:
        print("ERROR: API Key 未配置！")
        return

    # 2. 直连 LLM API
    target_url = f"{url.rstrip('/')}/v1/chat/completions"
    print(f"请求: {target_url}")
    print(f"模型: {model}")
    print(f"输入: SAM是最常用的分割模型")
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                target_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": 'Reply with ONLY JSON: {"english": "...", "chinese": "..."}'},
                        {"role": "user", "content": "SAM是最常用的分割模型"},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048,
                },
            )
            print(f"HTTP Status: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                print(f"LLM 返回: {content[:800]}")
            else:
                print(f"错误响应: {resp.text[:600]}")
        except httpx.TimeoutException:
            print("ERROR: 请求超时 (60s)")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")

asyncio.run(main())
