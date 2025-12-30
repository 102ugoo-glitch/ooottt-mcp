from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

@app.route('/mcp', methods=['GET', 'POST', 'OPTIONS'])
def mcp_endpoint():
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    if request.method == 'GET':
        return jsonify({
            "name": "ooottt",
            "version": "1.0.0",
            "description": "OTT 구독료 최적화",
            "tools": [
                {"name": "calculate_usage", "description": "구독료 사용률 계산"},
                {"name": "calculate_remaining", "description": "본전까지 남은 콘텐츠"},
                {"name": "recommend_short_content", "description": "30분 이내 콘텐츠 추천"}
            ]
        })
    
    return jsonify({
        "name": "ooottt",
        "version": "1.0.0",
        "tools": ["calculate_usage", "calculate_remaining", "recommend_short_content"]
    })

@app.route('/', methods=['GET'])
def home():
    return "OOOTTT MCP Server Running"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
