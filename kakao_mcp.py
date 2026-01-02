from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

# CORS 헤더 추가 함수
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# 카카오 MCP가 요구하는 정보 형식
KAKAO_MCP_INFO = {
    "name": "OOOTTT",
    "version": "1.0.0",
    "description": "OTT 구독료 최적화 도구",
    "capabilities": {
        "tools": [
            {
                "name": "calculate_usage",
                "description": "OTT 구독료 사용률 계산",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "description": "OTT 플랫폼 (netflix, watcha, tving 등)"},
                        "watched_hours": {"type": "number", "description": "이번 달 시청 시간"}
                    },
                    "required": ["platform", "watched_hours"]
                }
            },
            {
                "name": "calculate_remaining",
                "description": "구독료 본전까지 남은 콘텐츠 계산",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "description": "OTT 플랫폼"},
                        "current_percentage": {"type": "number", "description": "현재 사용률(%)"}
                    },
                    "required": ["platform", "current_percentage"]
                }
            },
            {
                "name": "recommend_short_content",
                "description": "30분 이내 짧은 콘텐츠 추천",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "genre": {"type": "string", "description": "장르 (코미디, 드라마, 액션 등)"}
                    }
                }
            }
        ]
    }
}

@app.route('/mcp', methods=['GET', 'POST', 'OPTIONS'])
def mcp_endpoint():
    # OPTIONS 요청 처리 (CORS preflight)
    if request.method == 'OPTIONS':
        response = Response()
        return add_cors_headers(response)
    
    # GET 또는 POST 요청 모두 같은 정보 반환
    response = jsonify(KAKAO_MCP_INFO)
    return add_cors_headers(response)

@app.route('/mcp/tools/<tool_name>', methods=['POST', 'OPTIONS'])
def execute_tool(tool_name):
    if request.method == 'OPTIONS':
        response = Response()
        return add_cors_headers(response)
    
    try:
        data = request.json or {}
        
        if tool_name == "calculate_usage":
            platform = data.get("platform", "netflix")
            watched_hours = data.get("watched_hours", 0)
            
            # 구독료 정보
            fees = {
                "netflix": 17000,
                "watcha": 12900,
                "tving": 13900,
                "wavve": 13900,
                "disney": 13900
            }
            
            monthly_fee = fees.get(platform, 15000)
            percentage = min((watched_hours * 1000 / monthly_fee) * 100, 100)
            
            result = {
                "result": f"🎬 {platform} 사용률: {percentage:.1f}%\n"
                         f"시청 시간: {watched_hours}시간\n"
                         f"{'🎉 본전 달성!' if percentage >= 100 else f'본전까지 {100-percentage:.1f}% 더!'}"
            }
        
        elif tool_name == "calculate_remaining":
            platform = data.get("platform", "netflix")
            current = data.get("current_percentage", 50)
            remaining = 100 - current
            
            movies = remaining / 10
            episodes = remaining / 3.3
            
            result = {
                "result": f"📊 {platform} 본전까지:\n"
                         f"• 영화 {movies:.0f}편 또는\n"
                         f"• 드라마 {episodes:.0f}화 더 보기!"
            }
        
        elif tool_name == "recommend_short_content":
            genre = data.get("genre", "")
            
            recommendations = {
                "코미디": ["프렌즈 (22분)", "브루클린 나인나인 (22분)"],
                "드라마": ["블랙미러 (45분)", "러브데스로봇 (15분)"],
                "다큐": ["익스플레인 (20분)", "추상 (45분)"],
                "기본": ["프렌즈 (22분)", "심야식당 (24분)", "러브데스로봇 (15분)"]
            }
            
            shows = recommendations.get(genre, recommendations["기본"])
            result = {
                "result": f"🎬 30분 이내 추천:\n" + 
                         "\n".join([f"• {show}" for show in shows])
            }
        
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        response = jsonify(result)
        return add_cors_headers(response)
    
    except Exception as e:
        response = jsonify({"error": str(e)})
        return add_cors_headers(response), 500

@app.route('/', methods=['GET'])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OOOTTT MCP Server</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .status { color: green; font-weight: bold; }
            code { background: #f4f4f4; padding: 2px 5px; }
        </style>
    </head>
    <body>
        <h1>🎬 OOOTTT MCP Server</h1>
        <p class="status">✅ Server is running</p>
        <p>Kakao MCP Endpoint: <code>/mcp</code></p>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting OOOTTT MCP Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
