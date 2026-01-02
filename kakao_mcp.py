from flask import Flask, request, jsonify, Response
import json
import random

app = Flask(__name__)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# OTT 요금제 정보
OTT_PLANS = {
    "netflix": {
        "광고형": 5500,
        "스탠다드": 13500,
        "프리미엄": 17000
    },
    "watcha": {
        "베이직": 7900,
        "프리미엄": 12900
    },
    "tving": {
        "베이직": 7900,
        "스탠다드": 10900,
        "프리미엄": 13900
    }
}

# 영화 데이터베이스 (장르별)
MOVIE_DATABASE = {
    "sf": {
        "titles": ["인터스텔라", "듄", "블레이드러너 2049", "매트릭스", "인셉션", "그래비티", "마션", "엣지 오브 투모로우"],
        "avg_price": 1800
    },
    "animation": {
        "titles": ["로봇드림", "스즈메의 문단속", "엘리멘탈", "코코", "소울", "루카", "인사이드아웃", "업"],
        "avg_price": 1540
    },
    "action": {
        "titles": ["존윅4", "탑건 매버릭", "미션임파서블", "분노의 질주", "아바타2", "스파이더맨", "배트맨", "덱스터"],
        "avg_price": 2000
    },
    "romance": {
        "titles": ["라라랜드", "어바웃타임", "노트북", "비포선라이즈", "그녀", "이터널선샤인", "캐롤", "콜미바이유어네임"],
        "avg_price": 1500
    },
    "thriller": {
        "titles": ["파라사이트", "올드보이", "셔터아일랜드", "조디악", "나를 찾아줘", "프레스티지", "메멘토", "세븐"],
        "avg_price": 1700
    },
    "comedy": {
        "titles": ["그랜드부다페스트호텔", "킹스맨", "나이브스아웃", "프리가이", "바톤아카데미", "돈룩업", "스쿨오브락"],
        "avg_price": 1400
    }
}

def get_genre_from_movies(movies):
    """영화 제목들로부터 장르 추측"""
    genre_keywords = {
        "sf": ["인터스텔라", "듄", "스타워즈", "매트릭스", "블레이드러너", "AI", "로봇", "우주"],
        "animation": ["픽사", "지브리", "디즈니", "드림웍스", "애니", "코코", "토이스토리", "겨울왕국"],
        "action": ["미션", "액션", "전투", "히어로", "마블", "DC", "존윅", "제임스본드"],
        "romance": ["사랑", "로맨스", "연애", "러브", "노트북", "타이타닉", "비포"],
        "thriller": ["스릴러", "서스펜스", "공포", "미스터리", "살인", "추리"],
        "comedy": ["코미디", "웃긴", "개그", "코믹", "하하"]
    }
    
    movie_text = " ".join(movies).lower()
    scores = {}
    
    for genre, keywords in genre_keywords.items():
        score = sum(1 for keyword in keywords if keyword.lower() in movie_text)
        if score > 0:
            scores[genre] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "action"  # 기본값

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
                        "name": "OOOTTT",
                        "version": "2.0.0",
                        "description": "스마트 OTT 본전 계산기"
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
                            "name": "smart_breakeven",
                            "description": "취향 기반 본전 영화 추천",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "favorite_movies": {
                                        "type": "array",
                                        "description": "좋아하는 영화 3개",
                                        "items": {"type": "string"}
                                    },
                                    "platform": {"type": "string", "description": "OTT 플랫폼"},
                                    "plan": {"type": "string", "description": "요금제 타입"}
                                },
                                "required": ["favorite_movies", "platform", "plan"]
                            }
                        },
                        {
                            "name": "calculate_real_value",
                            "description": "실제 영화 가격 기준 본전 계산",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "plan": {"type": "string"},
                                    "watched_count": {"type": "number", "description": "이번달 본 영화 수"}
                                },
                                "required": ["platform", "plan", "watched_count"]
                            }
                        },
                        {
                            "name": "recommend_by_budget",
                            "description": "남은 예산으로 볼 영화 추천",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "remaining_budget": {"type": "number"},
                                    "genre": {"type": "string"}
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
            
            if tool_name == "smart_breakeven":
                favorite_movies = arguments.get("favorite_movies", [])
                platform = arguments.get("platform", "netflix")
                plan = arguments.get("plan", "광고형")
                
                # 장르 파악
                genre = get_genre_from_movies(favorite_movies)
                genre_data = MOVIE_DATABASE.get(genre, MOVIE_DATABASE["action"])
                
                # 요금제 가격
                monthly_fee = OTT_PLANS.get(platform, {}).get(plan, 5500)
                
                # 영화당 평균 가격
                avg_movie_price = genre_data["avg_price"]
                
                # 본전 영화 수 계산
                breakeven_count = monthly_fee / avg_movie_price
                
                # 추천 영화 선택
                recommended = random.sample(genre_data["titles"], min(5, len(genre_data["titles"])))
                
                text = f"""## 🎬 맞춤형 본전 분석 - {platform.upper()} {plan}

### 📊 당신의 취향 분석
**좋아하는 영화:** {', '.join(favorite_movies)}  
**추측 장르:** {genre.upper()} 팬이시군요! 

### 💰 본전 계산
**월 요금:** {monthly_fee:,}원  
**영화 1편 평균 가격:** {avg_movie_price:,}원  
**본전 달성 필요 편수:** {breakeven_count:.1f}편

### 🎯 이번 달 꼭 보세요! (본전 영화)
{chr(10).join([f'• **{movie}** - 예상 가치 {avg_movie_price:,}원' for movie in recommended[:int(breakeven_count)+1]])}

### 💡 스마트 팁
{f'• {int(breakeven_count)}편만 보면 본전!' if breakeven_count < 5 else f'• 주말마다 2편씩 보면 본전 달성!'}
- 광고형은 적은 편수로도 본전 가능!
- 취향 맞는 영화 위주로 보면 만족도 UP!

> 🎉 **{plan} 요금제는 {int(breakeven_count)+1}편이면 이득!**"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "calculate_real_value":
                platform = arguments.get("platform", "netflix")
                plan = arguments.get("plan", "광고형")
                watched_count = arguments.get("watched_count", 0)
                
                monthly_fee = OTT_PLANS.get(platform, {}).get(plan, 5500)
                avg_price = 1600  # 평균 영화 가격
                total_value = watched_count * avg_price
                percentage = (total_value / monthly_fee) * 100
                remaining = max(0, monthly_fee - total_value)
                
                text = f"""## 💰 실제 가치 기준 본전 계산

### 📺 {platform.upper()} {plan} 요금제
**월 요금:** {monthly_fee:,}원

### 🎬 이번 달 시청 현황
**시청한 영화:** {watched_count}편  
**실제 가치:** {total_value:,}원  
**사용률:** {percentage:.1f}%

### 📊 본전 분석
{f'🎉 **축하합니다! {total_value-monthly_fee:,}원 이득!**' if percentage >= 100 else f'💪 **{remaining:,}원 ({remaining/avg_price:.1f}편) 더 보면 본전!**'}

### 💡 절약 팁
- 영화관 1편 = OTT 3-4편 가격
- {plan}은 {monthly_fee/avg_price:.1f}편이면 본전
- 매주 1-2편씩 꾸준히 시청하세요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            elif tool_name == "recommend_by_budget":
                remaining = arguments.get("remaining_budget", 3000)
                genre = arguments.get("genre", "action")
                
                genre_data = MOVIE_DATABASE.get(genre, MOVIE_DATABASE["action"])
                movies_count = int(remaining / genre_data["avg_price"])
                recommendations = random.sample(genre_data["titles"], min(movies_count, len(genre_data["titles"])))
                
                text = f"""## 🎯 남은 예산 활용 추천

### 💵 남은 본전 예산: {remaining:,}원

### 🎬 추천 {genre.upper()} 영화 ({movies_count}편)
{chr(10).join([f'• **{movie}**' for movie in recommendations])}

### 💡 시청 전략
- 이번 주말: 2편 몰아보기
- 평일 저녁: 1편씩 나눠보기
- 출퇴근길: 모바일로 조금씩

> ⚡ **{movies_count}편 모두 보면 완벽한 본전 달성!**"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
    
    response = jsonify({"name": "OOOTTT", "version": "2.0.0"})
    return add_cors_headers(response)

@app.route('/', methods=['GET'])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OOOTTT 2.0 - 스마트 본전 계산기</title>
        <style>
            body { font-family: 'Pretendard', Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
            h1 { color: #764ba2; font-size: 2.5em; }
            .feature { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; margin: 15px 0; border-radius: 15px; }
            .status { color: #4CAF50; font-weight: bold; font-size: 1.2em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 OOOTTT 2.0</h1>
            <p class="status">✅ 스마트 본전 계산기 작동중!</p>
            
            <div class="feature">
                <h3>🆕 smart_breakeven</h3>
                <p>좋아하는 영화 3개로 취향 분석 → 맞춤 본전 영화 추천!</p>
            </div>
            
            <div class="feature">
                <h3>💰 calculate_real_value</h3>
                <p>실제 영화 대여 가격 기준으로 진짜 본전 계산!</p>
            </div>
            
            <div class="feature">
                <h3>🎯 recommend_by_budget</h3>
                <p>남은 예산으로 딱 맞는 영화 추천!</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "2.0.0"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting OOOTTT 2.0 Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
