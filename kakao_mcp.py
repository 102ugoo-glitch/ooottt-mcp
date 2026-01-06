from flask import Flask, request, jsonify, Response
import json
import os

app = Flask(__name__)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# OTT 구독료 정보
SUBSCRIPTION_FEES = {
    "netflix": {"광고형": 5500, "스탠다드": 13500, "프리미엄": 17000},
    "넷플릭스": {"광고형": 5500, "스탠다드": 13500, "프리미엄": 17000},
    "watcha": {"베이직": 7900, "프리미엄": 12900},
    "왓챠": {"베이직": 7900, "프리미엄": 12900},
    "tving": {"베이직": 7900, "스탠다드": 10900, "프리미엄": 13900},
    "티빙": {"베이직": 7900, "스탠다드": 10900, "프리미엄": 13900},
    "wavve": {"베이직": 7900, "스탠다드": 10900, "프리미엄": 13900},
    "웨이브": {"베이직": 7900, "스탠다드": 10900, "프리미엄": 13900}
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
                    "protocolVersion": "2025-03-26",  # ✅ 최신 버전으로 업데이트
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "OOOTTT",
                        "version": "5.0.0",
                        "description": "OTT 구독료 본전 계산기"
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
                            "name": "check_breakeven",  # ✅ 대화 예시 1번과 매칭
                            "description": "시청 시간으로 본전 여부 확인",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string", "description": "OTT 플랫폼 (넷플릭스, 왓챠 등)"},
                                    "hours": {"type": "number", "description": "시청한 시간"},
                                    "plan": {"type": "string", "description": "요금제 (광고형/스탠다드/프리미엄)"}
                                }
                            }
                        },
                        {
                            "name": "calculate_spent",  # ✅ 대화 예시 2번과 매칭
                            "description": "지금까지 사용한 구독료 계산",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "days_used": {"type": "number", "description": "사용한 일수"},
                                    "plan": {"type": "string"}
                                }
                            }
                        },
                        {
                            "name": "remaining_content",  # ✅ 대화 예시 3번과 매칭
                            "description": "남은 기간 동안 봐야할 콘텐츠 수",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "days_left": {"type": "number", "description": "남은 일수"},
                                    "current_usage_percent": {"type": "number", "description": "현재 사용률"}
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
            
            # check_breakeven: "넷플릭스 20시간 봤는데 본전 찼어?"
            if tool_name == "check_breakeven":
                platform = arguments.get("platform", "넷플릭스").lower()
                hours = arguments.get("hours", 0)
                plan = arguments.get("plan", "스탠다드")
                
                # 플랫폼별 요금 가져오기
                fees = SUBSCRIPTION_FEES.get(platform, SUBSCRIPTION_FEES["넷플릭스"])
                monthly_fee = fees.get(plan, 13500)
                
                # 본전 계산 (월 30시간 = 100%)
                hourly_value = monthly_fee / 30
                current_value = hours * hourly_value
                percentage = min((current_value / monthly_fee) * 100, 100)
                
                if percentage >= 100:
                    emoji = "🎉"
                    status = "본전 달성!"
                    message = f"축하해요! 이미 구독료 이상의 가치를 뽑았네요!"
                elif percentage >= 80:
                    emoji = "😊"
                    status = "거의 본전!"
                    message = f"조금만 더! {100-percentage:.0f}% 남았어요!"
                else:
                    emoji = "💪"
                    status = "더 봐야해요"
                    message = f"본전까지 {100-percentage:.0f}% 더 시청하세요!"
                
                text = f"""## {emoji} {platform.upper()} 본전 체크

### 📊 현재 상황
- **시청 시간:** {hours}시간
- **요금제:** {plan} ({monthly_fee:,}원)
- **현재 가치:** {current_value:,.0f}원
- **사용률:** {percentage:.0f}%

### 🎯 {status}
{message}

> 💡 팁: 주말 몰아보기로 본전 달성하세요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # calculate_spent: "나 지금까지 구독료 얼마까지 썼어?"
            elif tool_name == "calculate_spent":
                platform = arguments.get("platform", "넷플릭스").lower()
                days_used = arguments.get("days_used", 15)
                plan = arguments.get("plan", "스탠다드")
                
                fees = SUBSCRIPTION_FEES.get(platform, SUBSCRIPTION_FEES["넷플릭스"])
                monthly_fee = fees.get(plan, 13500)
                daily_fee = monthly_fee / 30
                spent = daily_fee * days_used
                
                text = f"""## 💰 {platform.upper()} 구독료 사용 현황

### 📅 사용 기간
- **사용 일수:** {days_used}일
- **일일 요금:** {daily_fee:,.0f}원
- **요금제:** {plan}

### 💸 지출 금액
- **현재까지 사용료:** {spent:,.0f}원
- **월 구독료:** {monthly_fee:,}원
- **남은 금액:** {monthly_fee - spent:,.0f}원

### 📊 사용률
- **{(spent/monthly_fee*100):.0f}%** 사용 완료
- **{100-(spent/monthly_fee*100):.0f}%** 남음

> 💡 일 평균 2시간씩 보면 본전!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # remaining_content: "남은 결제일까지 몇 편 보면 될까?"
            elif tool_name == "remaining_content":
                platform = arguments.get("platform", "넷플릭스").lower()
                days_left = arguments.get("days_left", 10)
                current_usage = arguments.get("current_usage_percent", 60)
                
                remaining_percent = 100 - current_usage
                movies_needed = remaining_percent / 10  # 영화 1편 = 10%
                episodes_needed = remaining_percent / 3.3  # 드라마 1화 = 3.3%
                daily_movies = movies_needed / max(days_left, 1)
                
                text = f"""## 📺 {platform.upper()} 본전 달성 가이드

### 📅 남은 기간
- **결제일까지:** {days_left}일
- **현재 사용률:** {current_usage:.0f}%
- **목표:** 100% (본전)

### 🎬 본전까지 필요한 시청량
- **영화:** {movies_needed:.0f}편
- **또는 드라마:** {episodes_needed:.0f}화

### 📋 추천 시청 계획
- **하루에 영화** {daily_movies:.1f}편
- **또는 드라마** {daily_movies * 3:.0f}화
- **주말 몰아보기:** 영화 {movies_needed/2:.0f}편씩

### 🎯 빠른 달성 팁
1. 인기 시리즈 정주행
2. 주말에 영화 마라톤
3. 출퇴근 시간 활용

> ⏰ 하루 2시간씩만 투자하면 충분해요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
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
    
    response = jsonify({"name": "OOOTTT", "version": "5.0.0"})
    return add_cors_headers(response)

@app.route('/', methods=['GET'])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OOOTTT - OTT 본전 계산기</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; }
            h1 { color: #e50914; }
            .status { color: #4CAF50; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 OOOTTT v5.0</h1>
            <p class="status">✅ MCP 서버 정상 작동중</p>
            <p>프로토콜 버전: 2025-03-26</p>
            
            <h3>지원 기능:</h3>
            <ul>
                <li>check_breakeven - 본전 여부 확인</li>
                <li>calculate_spent - 사용 금액 계산</li>
                <li>remaining_content - 남은 시청량 계산</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "5.0.0"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 OOOTTT v5.0 Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
