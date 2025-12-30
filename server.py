# server.py - OOOTTT 고도화 버전
import os
import json
import asyncio
import sys
import requests
from datetime import datetime, timedelta

# TMDB API 키
TMDB_API_KEY = "여기에_TMDB_API키_넣기"
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', 'default_key')

class OOOTTTServer:
    def __init__(self):
        self.name = "ooottt"
        self.version = "1.0.0"
        
        self.subscription_fees = {
            "netflix": 17000,
            "watcha": 12900,
            "tving": 13900,
            "wavve": 13900,
            "disney": 13900,
            "apple": 8900,
            "amazon": 7900
        }
    
    async def handle_request(self, request):
        """요청 처리"""
        method = request.get("method")
        
        if method == "initialize":
            return {
                "protocolVersion": "0.1.0",
                "capabilities": {"tools": {}}
            }
        
        elif method == "tools/list":
            return {"tools": self.get_tools_list()}
        
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            arguments = request.get("params", {}).get("arguments", {})
            
            # 도구 매핑
            tool_handlers = {
                "calculate_usage": self.calculate_usage,
                "calculate_remaining": self.calculate_remaining,
                "recommend_short_content": self.recommend_short_content,
                "search_by_description": self.search_by_description,
                "analyze_viewing_pattern": self.analyze_viewing_pattern,
                "share_account_optimizer": self.share_account_optimizer,
                "expiring_content_alert": self.expiring_content_alert,
                "subscription_manager": self.subscription_manager,
                "ott_trend_report": self.ott_trend_report
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                return await handler(arguments)
        
        return {"error": "Unknown method"}
    
    def get_tools_list(self):
        """도구 목록 반환"""
        return [
            {
                "name": "calculate_usage",
                "description": "지금까지 구독료의 몇 %를 썼는지 계산",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string"},
                        "watched_hours": {"type": "number"}
                    }
                }
            },
            {
                "name": "calculate_remaining",
                "description": "구독료 본전까지 몇 편 더 봐야하는지",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string"},
                        "current_percentage": {"type": "number"}
                    }
                }
            },
            {
                "name": "recommend_short_content",
                "description": "30분 이내 콘텐츠 추천",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "genre": {"type": "string"}
                    }
                }
            },
            {
                "name": "search_by_description",
                "description": "설명으로 영화/드라마 찾기",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"}
                    }
                }
            },
            {
                "name": "analyze_viewing_pattern",
                "description": "시청 패턴 분석 & 최적 시간 추천",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "weekday_free_time": {"type": "number"},
                        "weekend_free_time": {"type": "number"},
                        "preferred_time": {"type": "string"},
                        "content_type": {"type": "string"}
                    }
                }
            },
            {
                "name": "share_account_optimizer",
                "description": "친구와 계정 공유 최적화",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "my_genres": {"type": "array"},
                        "friend_genres": {"type": "array"},
                        "platform": {"type": "string"}
                    }
                }
            },
            {
                "name": "expiring_content_alert",
                "description": "곧 사라지는 콘텐츠 알림",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string"},
                        "days": {"type": "number"}
                    }
                }
            },
            {
                "name": "subscription_manager",
                "description": "구독 최적화 추천",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "subscriptions": {"type": "array"},
                        "monthly_usage": {"type": "object"},
                        "budget": {"type": "number"}
                    }
                }
            },
            {
                "name": "ott_trend_report",
                "description": "이번달 OTT 트렌드 리포트",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string"}
                    }
                }
            }
        ]
    
    async def ott_trend_report(self, args):
        """OTT 트렌드 리포트"""
        platform = args.get("platform", "netflix")
        
        try:
            # TMDB에서 트렌딩 가져오기
            response = requests.get(
                f"{TMDB_BASE_URL}/trending/all/week",
                params={
                    "api_key": TMDB_API_KEY,
                    "language": "ko-KR"
                }
            )
            
            message = f"📈 {platform.upper()} 이번주 트렌드 리포트\n\n"
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])[:5]
                
                message += "🔥 TOP 5 인기 콘텐츠:\n"
                for i, item in enumerate(results, 1):
                    title = item.get("title") or item.get("name")
                    rating = item.get("vote_average", 0)
                    message += f"{i}. {title} ⭐{rating:.1f}\n"
                
                message += "\n💡 트렌드 인사이트:\n"
                message += "• 한국 콘텐츠가 계속 강세!\n"
                message += "• 주말엔 가족 영화가 인기\n"
                message += "• 20-30대는 로맨스 드라마 선호"
            else:
                message += "트렌드 데이터를 가져올 수 없었어요 😅"
            
        except:
            message = "트렌드 분석 중 오류가 발생했어요"
        
        return {
            "content": [{
                "type": "text",
                "text": message
            }]
        }
    
    # 기존 함수들도 모두 포함...
    async def calculate_usage(self, args):
        platform = args.get("platform", "netflix")
        watched_hours = args.get("watched_hours", 0)
        monthly_fee = self.subscription_fees.get(platform, 17000)
        hourly_value = monthly_fee / 30
        current_value = watched_hours * hourly_value
        percentage = min((current_value / monthly_fee) * 100, 100)
        
        emoji = "🎉" if percentage >= 100 else "👍" if percentage >= 80 else "📺" if percentage >= 50 else "😅"
        message = f"{emoji} {platform}에서 {percentage:.1f}% 사용 중!"
        
        return {"content": [{"type": "text", "text": message}]}
    
    async def calculate_remaining(self, args):
        platform = args.get("platform", "netflix")
        current = args.get("current_percentage", 50)
        remaining = 100 - current
        movies = remaining / 10
        episodes = remaining / 3.3
        
        message = f"📊 {platform} 본전까지:\n"
        message += f"• 영화 {movies:.0f}편 또는\n"
        message += f"• 드라마 {episodes:.0f}화 더 보기!"
        
        return {"content": [{"type": "text", "text": message}]}
    
    async def recommend_short_content(self, args):
        message = "🎬 30분 이내 추천:\n"
        message += "• 프렌즈 (22분)\n"
        message += "• 러브,데스+로봇 (15분)\n"
        message += "• 브루클린 나인나인 (22분)"
        
        return {"content": [{"type": "text", "text": message}]}
    
    async def search_by_description(self, args):
        description = args.get("description", "")
        
        if "공주" in description and "난쟁이" in description:
            message = "🍎 백설공주 찾으셨네요!\n"
            message += "• 디즈니+: 백설공주\n"
            message += "• 넷플릭스: 스노우화이트"
        elif "눈물" in description:
            message = "😭 감동 영화:\n"
            message += "• 이터널 선샤인\n"
            message += "• 어바웃 타임\n"
            message += "• 라라랜드"
        else:
            message = f"'{description}' 검색 중..."
        
        return {"content": [{"type": "text", "text": message}]}
    
    async def analyze_viewing_pattern(self, args):
        weekday = args.get("weekday_free_time", 2)
        weekend = args.get("weekend_free_time", 6)
        monthly = ((weekday * 5) + (weekend * 2)) * 4
        
        message = f"📊 시청 패턴 분석\n"
        message += f"• 월간 가능: {monthly}시간\n"
        message += f"• 필요: 30시간\n"
        message += "✅ 충분!" if monthly >= 30 else "⚠️ 부족!"
        
        return {"content": [{"type": "text", "text": message}]}
    
    async def share_account_optimizer(self, args):
        my_genres = set(args.get("my_genres", []))
        friend_genres = set(args.get("friend_genres", []))
        common = my_genres & friend_genres
        platform = args.get("platform", "netflix")
        fee = self.subscription_fees.get(platform, 17000)
        
        message = f"👥 계정 공유 분석\n"
        if common:
            message += f"🤝 공통: {', '.join(common)}\n"
        message += f"💰 1인당: {fee/2:,.0f}원"
        
        return {"content": [{"type": "text", "text": message}]}
    
    async def expiring_content_alert(self, args):
        platform = args.get("platform", "netflix")
        message = f"⏰ {platform} 곧 만료:\n"
        message += "🔴 오징어게임 (3일)\n"
        message += "🟡 기생충 (5일)"
        
        return {"content": [{"type": "text", "text": message}]}
    
    async def subscription_manager(self, args):
        subs = args.get("subscriptions", [])
        budget = args.get("budget", 30000)
        total = sum([self.subscription_fees.get(s, 15000) for s in subs])
        
        message = f"💼 구독 관리\n"
        message += f"• {len(subs)}개 구독\n"
        message += f"• 총 {total:,}원\n"
        message += "✅ 적정!" if total <= budget else f"⚠️ {total-budget:,}원 초과!"
        
        return {"content": [{"type": "text", "text": message}]}

async def main():
    server = OOOTTTServer()
    print(f"🚀 OOOTTT v{server.version} 시작!", file=sys.stderr)
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = await server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())