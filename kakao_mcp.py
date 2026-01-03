from flask import Flask, request, jsonify, Response
import json
import requests
import os
import random

app = Flask(__name__)

# TMDB API 키 (실제 키로 교체하세요!)
TMDB_API_KEY = "e5bb4d8da5684d820330957a9713ead2"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# 기분별 장르 매핑
MOOD_GENRES = {
    "happy": {"genres": [35, 16, 10402], "name": "행복/신남", "emoji": "😊"},  # Comedy, Animation, Music
    "sad": {"genres": [18, 10749], "name": "우울/슬픔", "emoji": "😢"},  # Drama, Romance
    "excited": {"genres": [28, 12, 878], "name": "흥분/스릴", "emoji": "🤩"},  # Action, Adventure, SF
    "tired": {"genres": [35, 10751], "name": "피곤/지침", "emoji": "😴"},  # Comedy, Family
    "angry": {"genres": [28, 53], "name": "화남/스트레스", "emoji": "😤"},  # Action, Thriller
    "romantic": {"genres": [10749, 18], "name": "로맨틱", "emoji": "💕"},  # Romance, Drama
    "scared": {"genres": [27, 9648], "name": "무서움", "emoji": "😱"},  # Horror, Mystery
    "bored": {"genres": [12, 878, 14], "name": "심심함", "emoji": "🥱"}  # Adventure, SF, Fantasy
}

# 기분별 추천 영화 (백업용)
MOOD_MOVIES = {
    "happy": ["라라랜드", "그랜드부다페스트호텔", "인사이드아웃", "코코", "패딩턴"],
    "sad": ["어바웃타임", "이터널선샤인", "그녀", "비포선라이즈", "라이프이즈뷰티풀"],
    "excited": ["탑건 매버릭", "인셉션", "매드맥스", "존윅", "미션임파서블"],
    "tired": ["심야식당", "리틀포레스트", "먹고기도하고사랑하라", "줄리&줄리아"],
    "angry": ["아수라", "악인전", "아저씨", "테이큰", "다크나이트"],
    "romantic": ["노트북", "타이타닉", "미비포유", "캐롤", "콜미바이유어네임"],
    "scared": ["곤지암", "컨저링", "겟아웃", "미드소마", "유전"],
    "bored": ["인터스텔라", "아바타", "해리포터", "반지의제왕", "듄"]
}

def get_movies_by_mood(mood):
    """기분에 맞는 영화 TMDB에서 가져오기"""
    mood_data = MOOD_GENRES.get(mood, MOOD_GENRES["happy"])
    genre_ids = mood_data["genres"]
    
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/discover/movie",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "with_genres": "|".join(map(str, genre_ids)),  # OR 조건
                "sort_by": "popularity.desc",
                "page": 1,
                "vote_average.gte": 6.0  # 평점 6.0 이상
            }
        )
        if response.status_code == 200:
            return response.json().get("results", [])[:7]
    except:
        pass
    return []

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
                        "version": "4.0.0",
                        "description": "기분별 영화 추천 & OTT 본전 계산"
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
                            "name": "mood_recommend",
                            "description": "기분에 따른 영화 추천 (happy/sad/excited/tired/angry/romantic/scared/bored)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "mood": {"type": "string", "description": "현재 기분"}
                                },
                                "required": ["mood"]
                            }
                        },
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
                        },
                        {
                            "name": "quick_pick",
                            "description": "5초 만에 영화 골라주기 (장르/시간대 맞춤)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "time_available": {"type": "number", "description": "시청 가능 시간(분)"},
                                    "genre_preference": {"type": "string", "description": "선호 장르(선택)"}
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
            
            if tool_name == "mood_recommend":
                mood = arguments.get("mood", "happy").lower()
                mood_data = MOOD_GENRES.get(mood, MOOD_GENRES["happy"])
                
                # TMDB에서 영화 가져오기
                movies = get_movies_by_mood(mood)
                
                text = f"""## {mood_data['emoji']} {mood_data['name']} 기분에 딱 맞는 영화

### 💊 기분 처방전
"""
                
                # 기분별 메시지
                mood_messages = {
                    "happy": "행복한 기분을 더 업시킬 영화들이에요! 🎉",
                    "sad": "위로가 필요할 때 보면 좋은 영화들이에요 🫂",
                    "excited": "스릴 넘치는 영화로 흥분을 더해보세요! ⚡",
                    "tired": "편하게 누워서 볼 수 있는 영화들이에요 🛋️",
                    "angry": "속 시원한 액션으로 스트레스 날려요! 💥",
                    "romantic": "설레는 감정을 더 깊게 느껴보세요 💝",
                    "scared": "오싹한 스릴을 원한다면! 👻",
                    "bored": "지루함을 날려줄 모험이 기다려요! 🚀"
                }
                
                text += mood_messages.get(mood, "당신에게 딱 맞는 영화예요!") + "\n\n"
                
                if movies:
                    text += "### 🎬 추천 영화 (TMDB 실시간)\n\n"
                    for i, movie in enumerate(movies[:5], 1):
                        title = movie.get("title", "")
                        rating = movie.get("vote_average", 0)
                        overview = movie.get("overview", "")[:80]
                        
                        text += f"""**{i}. {title}** ⭐{rating:.1f}
{overview}...

"""
                else:
                    # 백업 데이터 사용
                    text += "### 🎬 추천 영화\n\n"
                    backup_movies = MOOD_MOVIES.get(mood, MOOD_MOVIES["happy"])
                    for i, title in enumerate(backup_movies[:5], 1):
                        text += f"**{i}. {title}**\n"
                    text += "\n"
                
                # 기분별 팁
                mood_tips = {
                    "happy": "🍿 팝콘과 함께 보면 더 좋아요!",
                    "sad": "🍫 달콤한 초콜릿을 준비하세요",
                    "excited": "🎮 영화 후 게임도 어때요?",
                    "tired": "☕ 따뜻한 차와 함께 릴렉스",
                    "angry": "🥊 운동 후 시청하면 효과 2배",
                    "romantic": "🕯️ 무드등과 와인 준비!",
                    "scared": "🔦 불 켜고 보세요!",
                    "bored": "📱 친구와 같이 보면 더 재밌어요"
                }
                
                text += f"\n> {mood_tips.get(mood, '🎬 좋은 시간 되세요!')}"
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "quick_pick":
                time_available = arguments.get("time_available", 120)
                genre = arguments.get("genre_preference", "")
                
                # 시간대별 영화 분류
                if time_available <= 90:
                    category = "short"
                    movies = ["컨택트 (90분)", "그래비티 (91분)", "토이스토리 (81분)"]
                elif time_available <= 120:
                    category = "standard"
                    movies = ["라라랜드 (128분)", "겟아웃 (104분)", "코코 (105분)"]
                else:
                    category = "long"
                    movies = ["인터스텔라 (169분)", "듄 (155분)", "아바타2 (192분)"]
                
                # 랜덤 선택
                selected = random.choice(movies)
                
                text = f"""## 🎯 5초 영화 선택 완료!

### 🎬 오늘의 선택: **{selected}**

⏱️ **시청 가능 시간:** {time_available}분
📽️ **추천 이유:** 딱 맞는 러닝타임!

### 🍿 즉시 시청 팁
1. 핸드폰 무음 모드
2. 간식 준비 완료
3. 화장실 다녀오기
4. **지금 바로 재생!**

> ⚡ 고민은 시간 낭비! 바로 시작하세요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # 기존 도구들 (trending_now, search_movie_info, smart_breakeven)
            elif tool_name == "trending_now":
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
                    text = "## ❌ 데이터를 가져올 수 없습니다"
                
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
                
                text = f"""## 💰 {platform.upper()} {plan} 본전 분석

### 📊 현재 상황
- **월 요금:** {fee:,}원
- **시청 시간:** {watched}시간
- **현재 가치:** {current_value:,.0f}원
- **사용률:** {percentage:.1f}%

### 🎯 본전 계산
- **영화 {movies_needed:.1f}편**이면 본전!
- **{max(0, movies_needed - (watched/2)):.1f}편** 더 보기

> {('🎉 본전 달성!' if percentage >= 100 else f'💪 {100-percentage:.1f}% 더 파이팅!')}"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
    
    response = jsonify({"name": "OOOTTT Plus", "version": "4.0.0"})
    return add_cors_headers(response)

@app.route('/', methods=['GET'])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OOOTTT Plus 4.0</title>
        <style>
            body { 
                font-family: 'Pretendard', -apple-system, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                color: white;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: rgba(255,255,255,0.95);
                padding: 40px;
                border-radius: 20px;
                color: #333;
            }
            h1 { color: #764ba2; }
            .feature {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 15px 20px;
                margin: 10px 0;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 OOOTTT Plus 4.0</h1>
            <p>✅ 기분별 영화 추천 시스템 작동중!</p>
            
            <div class="feature">
                <strong>🎭 mood_recommend</strong> - 기분에 따른 맞춤 영화
            </div>
            <div class="feature">
                <strong>⚡ quick_pick</strong> - 5초 만에 영화 선택
            </div>
            <div class="feature">
                <strong>🔥 trending_now</strong> - 실시간 인기 영화
            </div>
            <div class="feature">
                <strong>💰 smart_breakeven</strong> - OTT 본전 계산기
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
