from flask import Flask, request, Response, jsonify
import json
import time

app = Flask(__name__)

@app.route('/sse', methods=['POST', 'OPTIONS'])
def mcp_sse():
    """SSE endpoint for Kakao MCP"""
    
    # CORS 처리
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    def generate():
        try:
            data = request.json or {}
            method = data.get("method", "")
            
            # 응답 생성
            if "init" in method.lower():
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "ooottt",
                            "version": "1.0.0"
                        }
                    }
                }
            elif "tool" in method.lower():
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "tools": [
                            {"name": "calculate_usage", "description": "구독료 사용률 계산"},
                            {"name": "calculate_remaining", "description": "본전까지 남은 콘텐츠"},
                            {"name": "recommend_short_content", "description": "30분 이내 콘텐츠 추천"}
                        ]
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {"status": "ok"}
                }
            
            # SSE 형식으로 전송
            yield f"data: {json.dumps(response)}\n\n"
            
        except Exception as e:
            error = {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {"code": -32603, "message": str(e)}
            }
            yield f"data: {json.dumps(error)}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "ooottt",
        "version": "1.0.0",
        "mcp": {
            "version": "2024-11-05",
            "endpoint": "/sse"
        }
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
