from flask import Flask, request, jsonify, Response
import json
import requests
import os

app = Flask(__name__)

# TMDB API 키 직접 입력 (여기에 실제 키 넣으세요!)
TMDB_API_KEY = "e5bb4d8da5684d820330957a9713ead2"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def get_trending_movies():
    """TMDB에서 현재 트렌딩 영화 가져오기"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/trending/movie/week",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "region": "KR"
            }
        )
        if response.status_code == 200:
            return response.json().get("results", [])[:7]
        else:
            print(f"TMDB Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching trending: {e}")
        return []

def search_movie(query):
    """영화 검색"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "query": query,
                "page": 1
            }
        )
        if response.status_code == 200:
            return response.json().get("results", [])[:5]
    except:
        pass
    return []

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
                        "description": "TMDB 실시간 영화 추천"
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
                            "name": "trending_now",
                            "description": "현재 실시간 인기 영화 TOP 7",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "search_movie_info",
                            "description": "영화 검색 및 정보 확인",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "영화 제목"}
                                },
                                "required": ["title"]
                            }
                        },
                        {
                            "name": "smart_breakeven",
                            "description": "OTT 본전 계산",
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
            
            if tool_name == "trending_now":
                movies = get_trending_movies()
                
                if movies:
                    text = "## 🔥 실시간 인기 영화 TOP 7\n*TMDB 한국 기준*\n\n"
                    
                    for i, movie in enumerate(movies, 1):
                        title = movie.get("title", "제목 없음")
                        rating = movie.get("vote_average", 0)
                        overview = movie.get("overview", "")[:100]
                        release = movie.get("release_date", "")[:4]
                        
                        text += f"""### {i}. {title} ({release})
⭐ **평점:** {rating:.1f}/10
📝 {overview}...

"""
                    
                    text += "> 📊 TMDB 실시간 데이터 기준"
                else:
                    text = "## ❌ 데이터를 가져올 수 없습니다\nTMDB API 키를 확인해주세요."
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "search_movie_info":
                title = arguments.get("title", "")
                movies = search_movie(title)
                
                text = f"""## 🔍 "{title}" 검색 결과\n\n"""
                
                if movies:
                    for movie in movies[:3]:
                        text += f"""### 📽️ {movie.get('title', '')}
**개봉:** {movie.get('release_date', '미정')[:4]}년
**평점:** ⭐ {movie.get('vote_average', 0):.1f}/10
**줄거리:** {movie.get('overview', '정보 없음')[:150]}...

"""
                else:
                    text += "검색 결과가 없습니다."
                
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
                movie_price = 1600
                movies_needed = fee / movie_price
                current_value = watched * 800
                percentage = (current_value / fee) * 100
                
                # 트렌딩 영화 가져와서 추천
                trending = get_trending_movies()[:3]
                
                text = f"""## 💰 {platform.upper()} {plan} 본전 분석

### 📊 현재 상황
- **월 요금:** {fee:,}원
- **시청 시간:** {watched}시간
- **현재 가치:** {current_value:,.0f}원
- **사용률:** {percentage:.1f}%

### 🎯 본전 계산
- **영화 {movies_needed:.1f}편**이면 본전!
- **{max(0, movies_needed - (watched/2)):.1f}편** 더 보기

### 🎬 지금 볼만한 인기 영화
"""
                for movie in trending:
                    text += f"• **{movie.get('title', '')}** ⭐{movie.get('vote_average', 0):.1f}\n"
                
                text += f"\n> {('🎉 본전 달성!' if percentage >= 100 else f'💪 {100-percentage:.1f}% 더 파이팅!')}"
                
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
    <h1>🎬 OOOTTT Plus with TMDB</h1>
    <p>✅ Server Running</p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
