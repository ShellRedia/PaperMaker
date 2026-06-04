"""简单 HTML 测试页 — 用浏览器打开，测试翻译 SSE 前端"""
TEST_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>翻译测试</title>
<style>
body{font-family:system-ui;max-width:600px;margin:40px auto;padding:20px;background:#1a1a2e;color:#eee}
#output{background:#16213e;padding:12px;border-radius:8px;min-height:100px;margin:10px 0;white-space:pre-wrap;font-family:monospace;font-size:13px}
textarea{width:100%;padding:8px;border-radius:6px;background:#0f3460;color:#fff;border:1px solid #533483;min-height:60px}
button{padding:10px 24px;border-radius:6px;background:#533483;color:#fff;border:none;cursor:pointer;font-size:16px}
button:hover{background:#7b2d8e}
#status{color:#e94560;margin-left:10px}
</style>
</head>
<body>
<h1>🌐 翻译 SSE 测试</h1>
<textarea id="input" placeholder="输入中文论文文字...">SAM是最常用的分割模型</textarea><br><br>
<button onclick="testTranslate()">➤ 翻译</button><span id="status"></span>
<div id="output"></div>
<div id="debug" style="font-size:11px;color:#888;margin-top:10px"></div>
<script>
async function testTranslate() {
    const text = document.getElementById('input').value.trim()
    if (!text) return
    const output = document.getElementById('output')
    const status = document.getElementById('status')
    const debug = document.getElementById('debug')
    output.textContent = ''
    status.textContent = '请求中...'
    debug.textContent = ''

    const API_BASE = window.__PAPERMAKER_API__ || window.location.origin
    debug.textContent = 'API_BASE: ' + API_BASE

    try {
        const resp = await fetch(API_BASE + '/api/translate/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, history: []}),
        })
        status.textContent = '状态: ' + resp.status
        if (!resp.ok) {
            output.textContent = 'HTTP Error: ' + resp.status + ' ' + await resp.text()
            return
        }
        const reader = resp.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        while (true) {
            const {done, value} = await reader.read()
            if (done) break
            buffer += decoder.decode(value, {stream: true})
            const lines = buffer.split('\\n')
            buffer = lines.pop() || ''
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6))
                    if (data.type === 'token') {
                        output.textContent += data.payload.token
                    } else if (data.type === 'done') {
                        status.textContent = '✓ 完成'
                        output.textContent += '\\n\\n--- 完整结果 ---\\n'
                        output.textContent += 'EN: ' + data.payload.english + '\\n'
                        output.textContent += 'CN: ' + data.payload.chinese
                    } else if (data.type === 'error') {
                        status.textContent = '✗ 错误: ' + data.payload
                    }
                }
            }
        }
    } catch (e) {
        status.textContent = '✗ 异常'
        output.textContent = 'Error: ' + e.message
        debug.textContent += '\\n' + e.stack
    }
}
</script>
</body>
</html>
"""

with open('c:/Users/gaomany/Desktop/PythonProjects/PaperMaker/backend/static/test_translate.html', 'w', encoding='utf-8') as f:
    f.write(TEST_PAGE)

print('Test page written to backend/static/test_translate.html')
print('Open: http://127.0.0.1:PORT/test_translate.html after starting the app')
