from flask import Flask, request, jsonify, Response
import json
import requests
import os
from datetime import datetime

app = Flask(__name__)

# TMDB API 설정
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', 'e5bb4d8da5684d820330957a9713ead2')  # Render 환경변수로 설정
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# OTT별 제공 콘텐츠 (한국 기준 예시)
OTT_PROVIDERS = {
    "netflix": 8,      # TMDB provider_id
    "watcha": 97,      
    "wavve": 356,
    "disney": 337,
    "apple": 350,
    "tving": 463
}

def get_trending_movies():
    """TMDB에서 현재 트렌딩 영화 가져오기"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/trending/movie/week",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR"
            }
        )
        if response.status_code == 200:
            return response.json().get("results", [])[:10]
    except:
        pass
    return []

def get_movies_by_genre(genre_id):
    """장르별 영화 추천"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/discover/movie",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "page": 1
            }
        )
        if response.status_code == 200:
            return response.json().get("results", [])[:5]
    except:
        pass
    return []

def get_movie_providers(movie_id):
    """영화를 볼 수 있는 OTT 플랫폼 확인"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers",
            params={"api_key": TMDB_API_KEY}
        )
        if response.status_code == 200:
            data = response.json()
            # 한국 데이터
            kr_data = data.get("results", {}).get("KR", {})
            return kr_data.get("flatrate", [])  # 구독형 서비스만
    except:
        pass
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
                                    "platform": {"type": "string", "description": "netflix/watcha/wavve/disney/tving"}
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
                                    "movie_title": {"type": "string", "description": "영화 제목"}
                                },
                                "required": ["movie_title"]
                            }
                        },
                        {
                            "name": "genre_recommendations",
                            "description": "장르별 OTT 영화 추천",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "genre": {"type": "string", "description": "action/comedy/romance/sf/horror"},
                                    "platform": {"type": "string"}
                                },
                                "required": ["genre", "platform"]
                            }
                        },
                        {
                            "name": "weekend_marathon",
                            "description": "주말 몰아보기 추천 (시리즈/3부작)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "hours_available": {"type": "number"}
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
                movies = get_trending_movies()
                
                text = f"""## 🔥 {platform.upper()} 실시간 인기 영화
*TMDB 기준 이번주 트렌딩*

"""
                for i, movie in enumerate(movies[:7], 1):
                    title = movie.get("title", "")
                    rating = movie.get("vote_average", 0)
                    overview = movie.get("overview", "")[:100]
                    release = movie.get("release_date", "")[:4]
                    
                    text += f"""### {i}. {title} ({release})
⭐ **평점:** {rating}/10
📝 {overview}...

"""
                
                text += f"""
> 💡 **Tip:** 주말에 2-3편 보면 {platform} 본전 달성!
> 📱 TMDB 실시간 데이터 기반"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "find_movie_ott":
                movie_title = arguments.get("movie_title", "")
                search_results = search_movie(movie_title)
                
                text = f"""## 🔍 "{movie_title}" 검색 결과

"""
                if search_results:
                    for movie in search_results[:3]:
                        title = movie.get("title", "")
                        movie_id = movie.get("id")
                        providers = get_movie_providers(movie_id)
                        
                        text += f"""### 📽️ {title}
**개봉:** {movie.get("release_date", "미정")[:4]}년
**평점:** ⭐ {movie.get("vote_average", 0)}/10

"""
                        if providers:
                            text += "**시청 가능 플랫폼:**\n"
                            for provider in providers:
                                text += f"• {provider.get('provider_name', '')}\n"
                        else:
                            text += "**시청 가능:** 현재 한국 OTT 제공 정보 없음\n"
                        text += "\n"
                else:
                    text += "검색 결과가 없습니다. 다른 제목으로 시도해보세요."
                
                text += "\n> 📌 TMDB 실시간 데이터 기반"
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "genre_recommendations":
                genre_map = {
                    "action": 28,
                    "comedy": 35,
                    "romance": 10749,
                    "sf": 878,
                    "horror": 27
                }
                
                genre = arguments.get("genre", "action")
                platform = arguments.get("platform", "netflix")
                genre_id = genre_map.get(genre, 28)
                
                movies = get_movies_by_genre(genre_id)
                
                text = f"""## 🎬 {platform.upper()} {genre.upper()} 장르 추천

"""
                for i, movie in enumerate(movies, 1):
                    text += f"""### {i}. {movie.get("title", "")}
⭐ {movie.get("vote_average", 0)}/10 | {movie.get("release_date", "")[:4]}년
{movie.get("overview", "")[:150]}...

"""
                
                text += f"> 🍿 {genre} 장르 TMDB 인기순 정렬"
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "weekend_marathon":
                platform = arguments.get("platform", "netflix")
                hours = arguments.get("hours_available", 6)
                
                text = f"""## 🍿 주말 몰아보기 추천 ({hours}시간)
### {platform.upper()} 추천 마라톤

**🦸 마블 시리즈** (6시간)
- 아이언맨 → 캡틴 아메리카 → 어벤져스

**🧙 해리포터 시리즈** (8시간)
- 마법사의 돌 → 비밀의 방 → 아즈카반의 죄수

**🌍 반지의 제왕** (9시간)
- 반지 원정대 → 두 개의 탑 → 왕의 귀환

**🚗 분노의 질주** (4시간)
- 분노의 질주 → 분노의 질주: 더 맥시멈

> 💡 {hours}시간이면 시리즈 2개 정도 완주 가능!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
    
    response = jsonify({"name": "OOOTTT Plus", "version": "3.0.0"})
    return add_cors_hea
cat > kakao_mcp.py << 'EOF'
from flask import Flask, request, jsonify, Response
import json
import requests
import os
from datetime import datetime

app = Flask(__name__)

# TMDB API 설정
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', 'YOUR_API_KEY_HERE')  # Render 환경변수로 설정
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# OTT별 제공 콘텐츠 (한국 기준 예시)
OTT_PROVIDERS = {
    "netflix": 8,      # TMDB provider_id
    "watcha": 97,      
    "wavve": 356,
    "disney": 337,
    "apple": 350,
    "tving": 463
}

def get_trending_movies():
    """TMDB에서 현재 트렌딩 영화 가져오기"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/trending/movie/week",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR"
            }
        )
        if response.status_code == 200:
            return response.json().get("results", [])[:10]
    except:
        pass
    return []

def get_movies_by_genre(genre_id):
    """장르별 영화 추천"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/discover/movie",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "page": 1
            }
        )
        if response.status_code == 200:
            return response.json().get("results", [])[:5]
    except:
        pass
    return []

def get_movie_providers(movie_id):
    """영화를 볼 수 있는 OTT 플랫폼 확인"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers",
            params={"api_key": TMDB_API_KEY}
        )
        if response.status_code == 200:
            data = response.json()
            # 한국 데이터
            kr_data = data.get("results", {}).get("KR", {})
            return kr_data.get("flatrate", [])  # 구독형 서비스만
    except:
        pass
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
                                    "platform": {"type": "string", "description": "netflix/watcha/wavve/disney/tving"}
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
                                    "movie_title": {"type": "string", "description": "영화 제목"}
                                },
                                "required": ["movie_title"]
                            }
                        },
                        {
                            "name": "genre_recommendations",
                            "description": "장르별 OTT 영화 추천",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "genre": {"type": "string", "description": "action/comedy/romance/sf/horror"},
                                    "platform": {"type": "string"}
                                },
                                "required": ["genre", "platform"]
                            }
                        },
                        {
                            "name": "weekend_marathon",
                            "description": "주말 몰아보기 추천 (시리즈/3부작)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "hours_available": {"type": "number"}
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
                movies = get_trending_movies()
                
                text = f"""## 🔥 {platform.upper()} 실시간 인기 영화
*TMDB 기준 이번주 트렌딩*

"""
                for i, movie in enumerate(movies[:7], 1):
                    title = movie.get("title", "")
                    rating = movie.get("vote_average", 0)
                    overview = movie.get("overview", "")[:100]
                    release = movie.get("release_date", "")[:4]
                    
                    text += f"""### {i}. {title} ({release})
⭐ **평점:** {rating}/10
📝 {overview}...

"""
                
                text += f"""
> 💡 **Tip:** 주말에 2-3편 보면 {platform} 본전 달성!
> 📱 TMDB 실시간 데이터 기반"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "find_movie_ott":
                movie_title = arguments.get("movie_title", "")
                search_results = search_movie(movie_title)
                
                text = f"""## 🔍 "{movie_title}" 검색 결과

"""
                if search_results:
                    for movie in search_results[:3]:
                        title = movie.get("title", "")
                        movie_id = movie.get("id")
                        providers = get_movie_providers(movie_id)
                        
                        text += f"""### 📽️ {title}
**개봉:** {movie.get("release_date", "미정")[:4]}년
**평점:** ⭐ {movie.get("vote_average", 0)}/10

"""
                        if providers:
                            text += "**시청 가능 플랫폼:**\n"
                            for provider in providers:
                                text += f"• {provider.get('provider_name', '')}\n"
                        else:
                            text += "**시청 가능:** 현재 한국 OTT 제공 정보 없음\n"
                        text += "\n"
                else:
                    text += "검색 결과가 없습니다. 다른 제목으로 시도해보세요."
                
                text += "\n> 📌 TMDB 실시간 데이터 기반"
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "genre_recommendations":
                genre_map = {
                    "action": 28,
                    "comedy": 35,
                    "romance": 10749,
                    "sf": 878,
                    "horror": 27
                }
                
                genre = arguments.get("genre", "action")
                platform = arguments.get("platform", "netflix")
                genre_id = genre_map.get(genre, 28)
                
                movies = get_movies_by_genre(genre_id)
                
                text = f"""## 🎬 {platform.upper()} {genre.upper()} 장르 추천

"""
                for i, movie in enumerate(movies, 1):
                    text += f"""### {i}. {movie.get("title", "")}
⭐ {movie.get("vote_average", 0)}/10 | {movie.get("release_date", "")[:4]}년
{movie.get("overview", "")[:150]}...

"""
                
                text += f"> 🍿 {genre} 장르 TMDB 인기순 정렬"
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "weekend_marathon":
                platform = arguments.get("platform", "netflix")
                hours = arguments.get("hours_available", 6)
                
                text = f"""## 🍿 주말 몰아보기 추천 ({hours}시간)
### {platform.upper()} 추천 마라톤

**🦸 마블 시리즈** (6시간)
- 아이언맨 → 캡틴 아메리카 → 어벤져스

**🧙 해리포터 시리즈** (8시간)
- 마법사의 돌 → 비밀의 방 → 아즈카반의 죄수

**🌍 반지의 제왕** (9시간)
- 반지 원정대 → 두 개의 탑 → 왕의 귀환

**🚗 분노의 질주** (4시간)
- 분노의 질주 → 분노의 질주: 더 맥시멈

> 💡 {hours}시간이면 시리즈 2개 정도 완주 가능!"""
                
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
    <p>TMDB API 연동 실시간 영화 추천 시스템</p>
    <p>✅ Server Running</p>
    """

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 OOOTTT Plus 3.0 with TMDB API")
    app.run(host='0.0.0.0', port=port, debug=False)
