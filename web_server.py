from flask import Flask, request, jsonify
import asyncio
from server import OOOTTTServer

app = Flask(__name__)
server = OOOTTTServer()

@app.route('/mcp', methods=['GET', 'POST', 'OPTIONS'])
def mcp_endpoint():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    if request.method == 'GET':
        return jsonify({
            "name": "ooottt",
            "version": "1.0.0",
            "tools": ["calculate_usage", "calculate_remaining", "recommend_short_content"]
        })
    
    try:
        data = request.json or {}
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(server.handle_request(data))
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/', methods=['GET'])
def home():
    return "<h1>OOOTTT MCP Server</h1><p>Status: Running</p>"

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
