# web_server.py - 웹 API 서버
from flask import Flask, request, jsonify
import asyncio
from server import OOOTTTServer

app = Flask(__name__)
server = OOOTTTServer()

@app.route('/mcp', methods=['POST'])
def mcp_endpoint():
    """MCP 엔드포인트"""
    try:
        data = request.json
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(server.handle_request(data))
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """홈페이지"""
    return """
    <h1>🎬 OOOTTT MCP Server</h1>
    <p>OTT 구독료 최적화 + 프롬프트로 콘텐츠 찾기!</p>
    <p>Status: ✅ Running</p>
    <ul>
        <li>구독료 사용률 계산</li>
        <li>본전까지 남은 콘텐츠</li>
        <li>30분 이내 콘텐츠 추천</li>
        <li>설명으로 영화 찾기 (NEW!)</li>
    </ul>
    """

if __name__ == '__main__':
    print("🚀 OOOTTT 웹 서버 시작!")
    print("👉 http://localhost:5000 으로 접속하세요!")
    app.run(host='0.0.0.0', port=5000, debug=True)