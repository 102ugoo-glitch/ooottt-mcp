from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

FEES = {"netflix": 17000, "watcha": 12900, "tving": 13900}

@app.route('/mcp', methods=['GET', 'POST', 'OPTIONS'])
def mcp():
    if request.method == 'OPTIONS':
        resp = Response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    
    if request.method == 'GET':
        return jsonify({"name": "ooottt", "version": "1.0.0"})
    
    try:
        data = request.json or {}
        method = data.get("method", "")
        
        if "init" in method.lower():
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "ooottt", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                }
            })
        
        elif "list" in method.lower():
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "tools": [
                        {"name": "calculate_usage", "description": "구독료 사용률 계산"},
                        {"name": "calculate_remaining", "description": 
"본전까지 남은 콘텐츠"},
                        {"name": "recommend_short", "description": "30분 
이내 추천"}
                    ]
                }
            })
        
        return jsonify({"jsonrpc": "2.0", "id": 1, "result": {"status": 
"ok"}})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/')
def home():
    return "<h1>OOOTTT MCP</h1>"

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
