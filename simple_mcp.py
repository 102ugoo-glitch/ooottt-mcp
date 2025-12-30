from flask import Flask, request, Response, jsonify
import json
import time

app = Flask(__name__)

# 1. 카카오 MCP가 처음 연결을 시도할 때 (SSE 연결)
@app.route('/mcp', methods=['GET'])
def mcp_sse():
    def generate():
        # 연결 직후 카카오 서버에 '나 여기 있어'라고 알리는 필수 메시지
        # data 부분의 uri는 실제 메시지를 주고받을 POST 엔드포인트입니다.
        yield f"event: endpoint\ndata: {request.base_url}/message\n\n"
        
        while True:
            time.sleep(15)  # 연결 유지를 위한 하트비트
            yield ": keep-alive\n\n"

    return Response(generate(), mimetype='text/event-stream')

# 2. 카카오가 실제로 도구 목록(List)이나 호출(Call)을 보낼 때 (JSON-RPC)
@app.route('/mcp/message', methods=['POST'])
def mcp_message():
    data = request.json or {}
    method = data.get("method", "")
    request_id = data.get("id", 1)

    # 도구 목록 요청 (list_tools)
    if "tools/list" in method:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {"name": "calculate_usage", "description": "구독료 사용률 계산"},
                    {"name": "calculate_remaining", "description": "본전까지 남은 콘텐츠 수 계산"},
                    {"name": "recommend_short", "description": "30분 이내 짧은 콘텐츠 추천"}
                ]
            }
        })

    # 초기화 요청 (initialize)
    elif "initialize" in method:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ooottt", "version": "1.0.0"}
            }
        })

    return jsonify({"jsonrpc": "2.0", "id": request_id, "result": {}})

@app.route('/')
def home():
    return "<h1>OOOTTT MCP Server Running</h1>"

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
