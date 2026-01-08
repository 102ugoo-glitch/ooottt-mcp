from flask import Flask, request, jsonify, Response
import json
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# OTT 구독료 정보
OTT_FEES = {
    "넷플릭스": 13500,
    "netflix": 13500,
    "왓챠": 12900,
    "watcha": 12900,
    "티빙": 13900,
    "tving": 13900,
    "웨이브": 13900,
    "wavve": 13900,
    "디즈니": 13900,
    "disney": 13900
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
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "OOOTTT",
                        "version": "6.0.0",
                        "description": "OTT 본전 계산 & 스마트 추천"
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
                            "name": "calculate_usage",
                            "description": "시청 시간으로 OTT 사용률 계산",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string", "description": "OTT 플랫폼명"},
                                    "hours": {"type": "number", "description": "시청 시간"}
                                },
                                "required": ["platform", "hours"]
                            }
                        },
                        {
                            "name": "calculate_remaining",
                            "description": "본전까지 남은 콘텐츠 계산",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "current_percent": {"type": "number", "description": "현재 사용률(%)"}
                                },
                                "required": ["platform", "current_percent"]
                            }
                        },
                        {
                            "name": "recommend_short",
                            "description": "30분 이내 짧은 콘텐츠 추천",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "duration": {"type": "number", "description": "최대 시간(분)"}
                                }
                            }
                        },
                        {
                            "name": "multi_ott_analysis",
                            "description": "여러 OTT 통합 분석",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "platforms": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "사용중인 OTT 리스트"
                                    }
                                },
                                "required": ["platforms"]
                            }
                        },
                        {
                            "name": "weekend_binge",
                            "description": "주말 몰아보기 추천",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "available_hours": {"type": "number", "description": "시청 가능 시간"}
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
            
            # calculate_usage: "넷플릭스 20시간 봤는데 본전?"
            if tool_name == "calculate_usage":
                platform = arguments.get("platform", "넷플릭스")
                hours = arguments.get("hours", 0)
                
                monthly_fee = OTT_FEES.get(platform.lower(), 13500)
                hourly_value = monthly_fee / 30
                current_value = hours * hourly_value
                percentage = min((current_value / monthly_fee) * 100, 100)
                
                emoji = "🎉" if percentage >= 100 else "👍" if percentage >= 70 else "💪"
                
                text = f"""## {emoji} {platform} 사용률 분석

**현재 사용률: {percentage:.1f}%**
- 시청 시간: {hours}시간
- 현재 가치: {current_value:,.0f}원
- 월 구독료: {monthly_fee:,}원

{f'🎊 축하해요! 본전 달성!' if percentage >= 100 else f'📺 본전까지 {100-percentage:.1f}% 남았어요!'}

> 💡 일일 2시간 시청 시 한달 60시간 = 200% 달성!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # calculate_remaining: "왓챠 50% 썼는데 본전까지 뭘 더?"
            elif tool_name == "calculate_remaining":
                platform = arguments.get("platform", "왓챠")
                current = arguments.get("current_percent", 50)
                
                remaining = 100 - current
                movies = remaining / 10
                episodes = remaining / 3.3
                
                text = f"""## 📊 {platform} 본전 가이드

**현재 {current}% 사용중!**

### 본전(100%)까지:
- 🎬 영화 {movies:.0f}편 더 보기
- 📺 드라마 {episodes:.0f}화 더 보기
- ⏱️ 약 {remaining/2:.0f}시간 필요

### 추천 전략:
{f'🔥 주말 몰아보기로 한번에!' if remaining > 30 else '✨ 오늘 영화 1편이면 달성!'}

> 매일 1편씩만 봐도 3일이면 본전!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # recommend_short: "30분 이내 콘텐츠 추천"
            elif tool_name == "recommend_short":
                duration = arguments.get("duration", 30)
                
                recommendations = {
                    15: ["러브데스로봇 (15분)", "왓이프 (20분)", "심슨가족 (22분)"],
                    30: ["프렌즈 (22분)", "브루클린나인나인 (22분)", "오피스 (24분)"],
                    45: ["블랙미러 (45분)", "셜록 미니 (45분)", "트루디텍티브 (40분)"]
                }
                
                text = f"""## ⏱️ {duration}분 이내 추천

### 추천 콘텐츠:"""
                
                for limit, shows in recommendations.items():
                    if limit <= duration:
                        text += f"\n**{limit}분 이내:**\n"
                        for show in shows:
                            text += f"• {show}\n"
                
                text += """
### 시청 팁:
- 점심시간 활용하기
- 출퇴근 지하철에서
- 잠들기 전 가볍게

> 짧아도 알찬 콘텐츠들이에요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # multi_ott_analysis: "넷플, 왓챠, 티빙 다 쓰는데 분석"
            elif tool_name == "multi_ott_analysis":
                platforms = arguments.get("platforms", ["넷플릭스", "왓챠"])
                
                total_cost = sum([OTT_FEES.get(p.lower(), 13000) for p in platforms])
                
                text = f"""## 💰 멀티 OTT 통합 분석

### 구독 현황:
"""
                for platform in platforms:
                    fee = OTT_FEES.get(platform.lower(), 13000)
                    text += f"• {platform}: {fee:,}원\n"
                
                text += f"""
### 총 지출: {total_cost:,}원/월

### 본전 달성 조건:
- 플랫폼당 월 10시간 = 본전
- 총 {len(platforms) * 10}시간 시청 필요
- 일일 {(len(platforms) * 10 / 30):.1f}시간 시청 권장

### 💡 절약 팁:
{f'• 2개로 줄이면 {total_cost - 26400:,}원 절약!' if len(platforms) > 2 else '• 친구와 계정 공유 고려'}
{f'• 가장 적게 보는 1개 해지 추천' if len(platforms) > 2 else '• 번갈아가며 구독하기'}

> 연간 {total_cost * 12:,}원 지출중!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
            
            # weekend_binge: "주말에 6시간 있는데 뭐 볼까"
            elif tool_name == "weekend_binge":
                hours = arguments.get("available_hours", 6)
                
                if hours <= 3:
                    content = "영화 1편 + 드라마 2화"
                    recommend = ["인셉션 (148분)", "파라사이트 (132분)"]
                elif hours <= 6:
                    content = "영화 2-3편 또는 시리즈 1개"
                    recommend = ["오징어게임 시즌1", "킹덤 시즌1", "D.P. 시즌1"]
                else:
                    content = "시리즈 완주 가능!"
                    recommend = ["종이의집 파트1", "스위트홈 시즌1", "지옥 전편"]
                
                text = f"""## 🍿 주말 {hours}시간 몰아보기 가이드

### 추천 구성:
**{content}**

### 추천 콘텐츠:
"""
                for item in recommend:
                    text += f"• {item}\n"
                
                text += f"""
### 시청 전략:
- 1시간마다 10분 휴식
- 간식과 음료 준비
- 핸드폰 무음 모드

### 본전 효과:
{hours}시간 시청 = 약 {(hours/30*100):.0f}% 사용률!

> 🎬 주말 몰아보기로 본전 달성하세요!"""
                
                result = {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": text}]
                    }
                }
                return add_cors_headers(jsonify(result))
    
    response = jsonify({"name": "OOOTTT", "version": "6.0.0"})
    return add_cors_headers(response)

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>🎬 OOOTTT v6.0</h1>
    <p>✅ 모든 도구 정상 작동중</p>
    <ul>
        <li>calculate_usage - 사용률 계산</li>
        <li>calculate_remaining - 남은 콘텐츠</li>
        <li>recommend_short - 짧은 콘텐츠</li>
        <li>multi_ott_analysis - 멀티 OTT 분석</li>
        <li>weekend_binge - 주말 몰아보기</li>
    </ul>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
