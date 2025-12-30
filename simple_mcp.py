from flask import Flask, request, Response, jsonify
import json
import time

app = Flask(__name__)

# [수정] methods에 'POST'를 추가하고, POST 요청 시 바로 JSON을 반환합니다.
@app.route('/mcp', methods=['GET', 'POST'])
def mcp_sse():
    # 카카오가 정보를 불러올 때 POST로 요청하면 바로 정보를 줍니다.
    if request.method == 'POST':
        mcp_data = {
            "mcpVersion": "1.0",
            "capabilities": {
                "tools": [
                    {"name": "calculate_usage", "description": "구독료 사용률 계산"},
                    {"name": "calculate_remaining", "description": "본전까지 남은 콘텐츠"},
                    {"name": "recommend_short", "description": "30분 이내 추천"}
                ]
            }
        }
        return jsonify(mcp_data)

    # GET 요청 시에는 SSE 스트림을 열어줍니다 (표준 규격)
    def generate():
        endpoint_url = f"{request.host_url.rstrip('/')}/mcp/message"
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        while True:
            time.sleep(20)
            yield ": keep-alive\n\n"

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
