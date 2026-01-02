from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# 카카오 MCP 정보
MCP_INFO = {
    "name": "OOOTTT",
    "version": "1.0.0",
    "description": "OTT 구독료 최적화 도구"
}

# OTT 구독료 정보
SUBSCRIPTION_FEES = {
    "netflix": 17000,
    "watcha": 12900,
    "tving": 13900,
    "wavve": 13900,
    "disney": 13900,
    "apple": 8900
}

@app.route('/mcp', methods=['GET', 'POST', 'OPTIONS'])
def mcp_endpoint():
    if request.method == 'OPTIONS':
        response = Response()
        return add_cors_headers(response)
    
    # POST 요청 처리 (MCP 표준 프로토콜)
    if request.method == 'POST':
        data = request.json or {}
        method = data.get("method", "")
        
        # initialize 요청
        if method == "initialize":
            result = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": MCP_INFO
                }
            }
            return add_cors_headers(jsonify(result))
        
        # tools/list 요청
        elif method == "tools/list":
            result = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "tools": [
                        {
                            "name": "calculate_usage",
                            "description": "OTT 구독료 사용률 계산",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string", "description": "OTT 플랫폼 이름"},
                                    "watched_hours": {"type": "number", "description": "시청 시간"}
                                },
                                "required": ["platform", "watched_hours"]
                            }
                        },
                        {
                            "name": "calculate_remaining",
                            "description": "본전까지 남은 콘텐츠",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "current_percentage": {"type": "number"}
                                },
                                "required": ["platform", "current_percentage"]
                            }
                        },
                        {
                            "name": "recommend_short",
                            "description": "30분 이내 콘텐츠 추천",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "genre": {"type": "string"}
                                }
                            }
                        }
                    ]
                }
            }
            return add_cors_headers(jsonify(result))
        
        # tools/call 요청
        elif method == "tools/call":
            tool_name = data.get("params", {}).get("name", "")
            arguments = data.get("params", {}).get("arguments", {})
            
            # calculate_usage 도구
            if tool_name == "calculate_usage":
                platform = arguments.get("platform", "netflix")
                watched_hours = arguments.get("watched_hours", 0)
                
                monthly_fee = SUBSCRIPTION_FEES.get(platform, 15000)
                percentage = min((watched_hours * 1000 / monthly_fee) * 100, 100)
                
                emoji = "🎉" if percentage >= 100 else "👍" if percentage >= 80 else "📺" if percentage >= 50 else "😅"
                
                text = f"""## {platform.upper()} 사용률 분석 {emoji}

**현재 사용률:** {percentage:.1f}%  
**시청 시간:** {watched_hours}시간  
**월 구독료:** {monthly_fee:,}원

{('### 🎊 축하합니다! 본전 달성!' if percentage >= 100 else f'### 본전까지 {100-percentage:.1f}% 더 시청하세요!')}

> 💡 **Tip:** 주말 몰아보기로 사용률을 높여보세요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # calculate_remaining 도구
            elif tool_name == "calculate_remaining":
                platform = arguments.get("platform", "netflix")
                current = arguments.get("current_percentage", 50)
                remaining = 100 - current
                
                movies = remaining / 10
                episodes = remaining / 3.3
                
                text = f"""## 📊 {platform.upper()} 본전 달성 가이드

**현재 사용률:** {current:.1f}%  
**남은 비율:** {remaining:.1f}%

### 본전까지 필요한 시청량:
- 🎬 **영화:** 약 {movies:.0f}편
- 📺 **드라마:** 약 {episodes:.0f}화

> 💡 주말에 시리즈물 정주행을 추천드려요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # recommend_short 도구
            elif tool_name == "recommend_short":
                genre = arguments.get("genre", "")
                
                text = f"""## 🎬 30분 이내 추천 콘텐츠

### 코미디 (20-25분)
- **프렌즈** - 에피소드당 22분
- **브루클린 나인나인** - 에피소드당 22분
- **오피스** - 에피소드당 22분

### 애니메이션 (15-20분)
- **러브, 데스 + 로봇** - 에피소드당 15-20분
- **왓 이프...?** - 에피소드당 20-25분

### 다큐멘터리 (20-30분)
- **익스플레인** - 에피소드당 20분
- **세계의 끝과 함께** - 에피소드당 25분

> 💡 출퇴근이나 점심시간에 부담없이 즐기세요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # 알 수 없는 도구
            else:
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
                return add_cors_headers(jsonify(result))
    
    # GET 요청 - 서버 정보 반환
    response = jsonify(MCP_INFO)
    return add_cors_headers(response)

@app.route('/', methods=['GET'])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OOOTTT MCP Server</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #e50914; }
            .status { color: green; font-weight: bold; }
            .tool { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            code { background: #e9ecef; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 OOOTTT MCP Server</h1>
            <p class="status">✅ Server is running successfully!</p>
            <p>카카오 MCP 엔드포인트: <code>/mcp</code></p>
            
            <h3>사용 가능한 도구들:</h3>
            <div class="tool">
                <strong>calculate_usage</strong> - OTT 구독료 사용률 계산
            </div>
            <div class="tool">
                <strong>calculate_remaining</strong> - 본전까지 남은 콘텐츠 계산
            </div>
            <div class="tool">
                <strong>recommend_short</strong> - 30분 이내 콘텐츠 추천
            </div>
        </div>
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
