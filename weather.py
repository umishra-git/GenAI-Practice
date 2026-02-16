from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

#Initialize MCP server
mcp = FastMCP("weather")

#Constants
NWS_API_BASE_URL = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

#Endpoints

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API"""
    headers = {
               "User-Agent": USER_AGENTS, 
               "Accept": "applications/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None
    
def format_alert(feature: dict) -> str:
    """Format an alert into a readable string"""
    props = feature["properties"]
    return f"""
    Event: {props.get("event", "Unknown")}
    Awareness: {props.get("areaDesc", "Unknown")}
    Severity: {props.get("severity", "Unknown")}
    Description: {props.get("description", "Unknown")}
    Instructions: {props.get("instruction", "Unknown")}
    """

@mcp.tools()
async def get_alerts(state: str) -> str:
    """Get the alerts for a given state"""
    url = f"{NWS_API_BASE_URL}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts"

    if not data["features"]:
        return "No active alerts found"
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n\n".join(alerts)
