from flask import Flask, request, jsonify, Response
import json
import os

app = Flask(__name__)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# 하드코딩된 영화 데이터 (TMDB 대신 임시)
TRENDING_MOVIES = [
    {"title": "듄: 파트2", "rating": 8.5, "year": "2024", "overview": "폴 아트레이디스의 운명적인 여정"},
    {"title": "파묘", "rating": 7.8, "year": "2024", "overview": "기이한 사건을 파헤치는 무속인들"},
    {"title": "오펜하이머", "rating": 8.9, "year": "2023", "overview": "원자폭탄의 아버지 이야기"},
    {"title": "범죄도시4", "rating": 7.2, "year": "2024", "overview": "마동석의 강력 액션"},
    {"title": "인사이드 아웃2", "rating": 8.1, "year": "2024", "overview": "새로운 감정들의 모험"}
]

# OTT별 영화 매핑
OTT_CONTENT = {
    "netflix": ["오펜하이머", "듄: 파트2", "범죄도시4"],
    "watcha": ["파묘", "인사이드 아웃2", "듄: 파트2"],
    "disney": ["인사이드 아웃2", "아바타2", "마블 시리즈"],
    "tving": ["파묘", "범죄도시4", "서울의 봄"],
    "wavve": ["범죄도시4", "파묘", "서울의 봄"]
}

@app.route('/mcp', methods=['GET', 'POST', 'OPTIONS'])
def mcp_endpoint():
    if request.method == 'OPTIONS':
        response = Response()
        return add_cors_headers(response)
    
    if request.method == 'POST':
        data = request.json or {}
        method = data.get("method", "")
        
        if method == "initialize":
            result = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "OOOTTT Plus",
                        "version": "3.0.0",
                        "description": "실시간 영화 정보 & OTT 추천"
                    }
                }
            }
            return add_cors_headers(jsonify(result))
        
        elif method == "tools/list":
            result = {
                "jsonrpc": "2.0",
                "id": data.get("id", 1),
                "result": {
                    "tools": [
                        {
                            "name": "trending_on_ott",
                            "description": "내 OTT에서 볼 수 있는 현재 인기 영화",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"}
                                },
                                "required": ["platform"]
                            }
                        },
                        {
                            "name": "find_movie_ott",
                            "description": "특정 영화가 어느 OTT에 있는지 검색",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "movie_title": {"type": "string"}
                                },
                                "required": ["movie_title"]
                            }
                        },
                        {
                            "name": "smart_breakeven",
                            "description": "취향 맞춤 본전 계산",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "plan": {"type": "string"},
                                    "watched_hours": {"type": "number"}
                                }
                            }
                        }
                    ]
                }
            }
            return add_cors_headers(jsonify(result))
        
        elif method == "tools/call":
            tool_name = data.get("params", {}).get("name", "")
            arguments = data.get("params", {}).get("arguments", {})
            
            if tool_name == "trending_on_ott":
                platform = arguments.get("platform", "netflix")
                movies = OTT_CONTENT.get(platform, ["콘텐츠 정보 없음"])
                
                text = f"""## 🔥 {platform.upper()} 인기 영화

"""
                for i, title in enumerate(movies, 1):
                    # 영화 정보 찾기
                    movie_info = next((m for m in TRENDING_MOVIES if m["title"] == title), None)
                    if movie_info:
                        text += f"""### {i}. {movie_info['title']} ({movie_info['year']})
⭐ **평점:** {movie_info['rating']}/10
📝 {movie_info['overview']}

"""
                    else:
                        text += f"### {i}. {title}\n\n"
                
                text += f"> 💡 주말에 2-3편 보면 {platform} 본전 달성!"
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "find_movie_ott":
                movie_title = arguments.get("movie_title", "").lower()
                found_platforms = []
                
                for platform, movies in OTT_CONTENT.items():
                    for movie in movies:
                        if movie_title in movie.lower():
                            found_platforms.append((platform, movie))
                
                text = f"""## 🔍 "{movie_title}" 검색 결과

"""
                if found_platforms:
                    for platform, title in found_platforms:
                        text += f"### ✅ {platform.upper()}\n"
                        text += f"• {title} 시청 가능\n\n"
                else:
                    text += "검색 결과가 없습니다. 다른 제목으로 시도해보세요.\n\n"
                    text += "**현재 인기 영화:**\n"
                    for movie in TRENDING_MOVIES[:3]:
                        text += f"• {movie['title']}\n"
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "smart_breakeven":
                platform = arguments.get("platform", "netflix")
                plan = arguments.get("plan", "광고형")
                watched = arguments.get("watched_hours", 0)
                
                fees = {
                    "광고형": 5500,
                    "스탠다드": 13500,
                    "프리미엄": 17000
                }
                
                fee = fees.get(plan, 5500)
                movie_price = 1600  # 평균 영화 가격
                movies_needed = fee / movie_price
                current_value = watched * 800  # 시간당 가치
                percentage = (current_value / fee) * 100
                
                text = f"""## 💰 {platform.upper()} {plan} 본전 분석

### 📊 현재 상황
- **월 요금:** {fee:,}원
- **시청 시간:** {watched}시간
- **현재 가치:** {current_value:,.0f}원
- **사용률:** {percentage:.1f}%

### 🎯 본전 계산
- **영화 {movies_needed:.1f}편**이면 본전!
- **{max(0, movies_needed - (watched/2)):.1f}편** 더 보기

### 🎬 추천 콘텐츠
{chr(10).join([f'• {movie}' for movie in OTT_CONTENT.get(platform, [])[:3]])}

> {('🎉 본전 달성!' if percentage >= 100 else f'💪 {100-percentage:.1f}% 더 파이팅!')}"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
    
    response = jsonify({"name": "OOOTTT Plus", "version": "3.0.0"})
    return add_cors_headers(response)

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>🎬 OOOTTT Plus 3.0</h1>
    <p>실시간 영화 추천 시스템</p>
    <p>✅ Server Running</p>
    """

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 OOOTTT Plus 3.0 Server")
    app.run(host='0.0.0.0', port=port, debug=False)
