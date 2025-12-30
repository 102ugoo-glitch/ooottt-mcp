from flask import Flask, request, Response, jsonify
import json
import time

app = Flask(__name__)

@app.route('/mcp', methods=['GET'])
def mcp_sse():
    def generate():
        # [중요] 카카오 MCP는 연결 직후 이 형식을 반드시 기다립니다.
        # data의 URL은 반드시 https://.../mcp/message 형태여야 합니다.
        endpoint_url = f"{request.host_url.rstrip('/')}/mcp/message"
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        
        while True:
            time.sleep(20)
            yield ": keep-alive\n\n"

    # 헤더에 Cache-Control과 X-Accel-Buffering을 추가하여 연결 끊김 방지
    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive'
    }
    return Response(generate(), headers=headers)

@app.route('/mcp/message', methods=['POST'])
def mcp_message():
    data = request.json or {}
    method = data.get("method", "")
    request_id = data.get("id", 1)

    # 1. 초기화 단계
    if "initialize" in method:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ooottt", "version": "1.0.0"}
            }
        })

    # 2. 도구 목록 제공 단계
    elif "tools/list" in method:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {"name": "calculate_usage", "description": "구독료 사용률 계산"},
                    {"name": "calculate_remaining", "description": "본전까지 남은 콘텐츠"},
                    {"name": "recommend_short", "description": "30분 이내 추천"}
                ]
            }
        })

    return jsonify({"jsonrpc": "2.0", "id": request_id, "result": {}})

@app.route('/')
def home():
    return "MCP Server Status: OK"

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
