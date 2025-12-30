# web_server.py - MCP 표준 프로토콜 버전
from flask import Flask, request, jsonify
import asyncio
from server import OOOTTTServer
import json

app = Flask(__name__)
server = OOOTTTServer()

@app.route('/mcp', methods=['POST', 'OPTIONS'])
def mcp_endpoint():
    """MCP 표준 엔드포인트"""
    
    # CORS 처리
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        # JSON-RPC 형식 처리
        data = request.json
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # MCP 표준 응답 형식
        if data.get("method") == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "ooottt",
                        "version": "1.0.0"
                    }
                }
            }
        elif data.get("method") == "tools/list":
            result = loop.run_until_complete(server.handle_request(data))
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": result
            }
        elif data.get("method") == "tools/call":
            result = loop.run_until_complete(server.handle_request(data))
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": result
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }
        
        # CORS 헤더 추가
        json_response = jsonify(response)
        json_response.headers['Access-Control-Allow-Origin'] = '*'
        json_response.headers['Content-Type'] = 'application/json'
        return json_response
    
    except Exception as e:
        error_response = jsonify({
            "jsonrpc": "2.0",
            "id": request.json.get("id", 1) if request.json else 1,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        })
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        return error_response, 500

@app.route('/', methods=['GET'])
def home():
    """홈페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OOOTTT MCP Server</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { color: #e50914; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🎬 OOOTTT MCP Server</h1>
        <p>OTT 구독료 최적화 + 프롬프트로 콘텐츠 찾기!</p>
        <p class="status">✅ Server Running</p>
        <h3>기능:</h3>
        <ul>
            <li>구독료 사용률 계산</li>
            <li>본전까지 남은 콘텐츠</li>
            <li>30분 이내 콘텐츠 추천</li>
            <li>설명으로 영화 찾기</li>
        </ul>
        <p>MCP Endpoint: <code>/mcp</code></p>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health():
    """헬스체크 엔드포인트"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)