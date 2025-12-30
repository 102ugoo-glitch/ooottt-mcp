from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ooottt")
cat > ooottt_mcp.py << 'EOF'
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# FastMCP 서버 초기화
mcp = FastMCP("ooottt")

# OTT 구독료 정보
SUBSCRIPTION_FEES = {
    "netflix": 17000,
    "watcha": 12900,
    "tving": 13900,
    "wavve": 13900,
    "disney": 13900
}

@mcp.tool()
async def calculate_usage(platform: str, watched_hours: float) -> str:
    """Calculate OTT subscription usage percentage.
    
    Args:
        platform: OTT platform name (netflix, watcha, tving, wavve, disney)
        watched_hours: Hours watched this month
    """
    if platform not in SUBSCRIPTION_FEES:
        return f"Unknown platform: {platform}. Supported: {', '.join(SUBSCRIPTION_FEES.keys())}"
    
    monthly_fee = SUBSCRIPTION_FEES[platform]
    hourly_value = monthly_fee / 30  # Assuming 30 hours = 100% value
    current_value = watched_hours * hourly_value
    percentage = min((current_value / monthly_fee) * 100, 100)
    
    if percentage >= 100:
        return f"🎉 Great! You've watched {watched_hours} hours on {platform}, using {percentage:.1f}% of your subscription value!"
    elif percentage >= 80:
        return f"👍 Good job! {percentage:.1f}% used on {platform}. Almost at full value!"
    elif percentage >= 50:
        return f"📺 {percentage:.1f}% used on {platform}. Consider a weekend binge-watch!"
    else:
        return f"😅 Only {percentage:.1f}% used on {platform}. Time to watch something tonight?"

@mcp.tool()
async def calculate_remaining(platform: str, current_percentage: float) -> str:
    """Calculate how much content to watch to reach subscription value.
    
    Args:
        platform: OTT platform name
        current_percentage: Current usage percentage
    """
    if platform not in SUBSCRIPTION_FEES:
        return f"Unknown platform: {platform}"
    
    remaining = 100 - current_percentage
    movies_needed = remaining / 10  # Assuming 1 movie = 10% value
    episodes_needed = remaining / 3.3  # Assuming 1 episode = 3.3% value
    
    return f"""📊 {platform} usage analysis:
    Current usage: {current_percentage:.1f}%
    To reach 100% value:
    • Watch {movies_needed:.0f} more movies OR
    • Watch {episodes_needed:.0f} more drama episodes
    💡 Tip: Weekend binge-watching is the way to go!"""

@mcp.tool()
async def recommend_short_content(max_duration: int = 30) -> str:
    """Recommend short content under specified duration.
    
    Args:
        max_duration: Maximum duration in minutes (default 30)
    """
    recommendations = {
        15: ["Love, Death & Robots (15-20 min)", "What If...? (20-25 min)"],
        30: ["Friends (22 min)", "Brooklyn Nine-Nine (22 min)", "Midnight Diner (24 min)"],
        60: ["Black Mirror episodes (45-60 min)", "Sherlock mini episodes (45 min)"]
    }
    
    result = f"🎬 Content under {max_duration} minutes:\n"
    
    for duration, shows in recommendations.items():
        if duration <= max_duration:
            for show in shows:
                result += f"• {show}\n"
    
    return result

@mcp.tool()
async def search_by_description(description: str) -> str:
    """Find movies/shows by description.
    
    Args:
        description: Natural language description of the content
    """
    # Simple keyword matching for demo
    if "princess" in description.lower() and "dwarf" in description.lower():
        return """🍎 You're looking for Snow White!
        • Disney+: Snow White and the Seven Dwarfs
        • Netflix: Mirror Mirror
        • Various platforms: Snow White adaptations"""
    
    elif "cry" in description.lower() or "emotional" in description.lower():
        return """😭 Emotional recommendations:
        • Eternal Sunshine of the Spotless Mind
        • About Time
        • La La Land
        • Your Name
        • A Star is Born"""
    
    return f"Searching for: {description}... Try being more specific!"

def main():
    # Run the MCP server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
