#!/usr/bin/env python3
"""
MCP Client for Telephony Server
Sends SMS messages via the Telephony MCP Server
"""
import asyncio
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import httpx


def parse_sse_response(response_text: str):
    """
    Parse Server-Sent Events (SSE) response to extract JSON
    Format is:
    event: message
    data: {...json...}
    """
    response_text = response_text.strip()
    
    # Parse SSE format
    lines = response_text.split('\n')
    for line in lines:
        if line.startswith('data: '):
            json_str = line.replace('data: ', '', 1)
            return json.loads(json_str)
    
    # Fallback: try parsing as regular JSON
    if response_text and not response_text.startswith('event:'):
        return json.loads(response_text)
    
    return {}


async def send_sms_via_mcp(to_number: str, message: str, from_number: str = None):
    """
    Send SMS via MCP server using HTTP transport
    
    Args:
        to_number: Destination phone number (e.g., "+14155551234")
        message: SMS message text
        from_number: Optional sender number (defaults to server's VONAGE_LVN)
    """
    # MCP server endpoint
    mcp_url = "http://127.0.0.1:8000/mcp/"
    
    # Headers required by MCP server
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(headers=headers) as http_client:
        # Initialize MCP session
        print(f"🔌 Connecting to MCP server at {mcp_url}")
        
        # List available tools
        print("📋 Fetching available tools...")
        
        # Make MCP initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "telephony-mcp-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await http_client.post(mcp_url, json=init_request)
        
        if response.status_code != 200:
            print(f"❌ Failed to initialize MCP session: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Parse SSE response
        init_result = parse_sse_response(response.text)
        print(f"✅ Connected! Server: {init_result.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Extract session ID from response headers
        session_id = response.headers.get('mcp-session-id')
        
        # Prepare headers for subsequent requests
        if session_id:
            http_client.headers['mcp-session-id'] = session_id
            print(f"📝 Session ID: {session_id}")
        else:
            print(f"⚠️  No session ID found in headers")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await http_client.post(mcp_url, json=initialized_notification)
        
        # List tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await http_client.post(mcp_url, json=list_tools_request)
        if response.status_code == 200:
            tools_result = parse_sse_response(response.text)
            tools = tools_result.get("result", {}).get("tools", [])
            print(f"📱 Available tools: {[tool['name'] for tool in tools]}")
        
        # Prepare SMS parameters
        sms_params = {
            "to": to_number,
            "text": message
        }
        
        if from_number:
            sms_params["from_"] = from_number
        
        # Call send_sms tool
        print(f"\n📤 Sending SMS to {to_number}...")
        print(f"💬 Message: {message}")
        
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "send_sms",
                "arguments": sms_params
            }
        }
        
        response = await http_client.post(mcp_url, json=call_tool_request)
        
        if response.status_code != 200:
            print(f"❌ Failed to send SMS: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        result = parse_sse_response(response.text)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Extract result
        tool_result = result.get("result", {})
        content = tool_result.get("content", [])
        
        if content:
            for item in content:
                if item.get("type") == "text":
                    print(f"✅ Result: {item.get('text')}")
        else:
            print(f"✅ SMS sent successfully!")
        
        print(f"\n📊 Full response: {result}")


async def interactive_mode():
    """
    Interactive mode for sending multiple SMS messages
    """
    print("=" * 60)
    print("📱 Telephony MCP Client - SMS Sender")
    print("=" * 60)
    print("\nInteractive Mode - Send SMS via MCP Server")
    print("Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            to_number = input("📞 Enter destination number (e.g., +14155551234): ").strip()
            
            if to_number.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not to_number:
                print("❌ Please enter a valid phone number")
                continue
            
            message = input("💬 Enter message text: ").strip()
            
            if not message:
                print("❌ Please enter a message")
                continue
            
            from_number = input("📤 Enter sender number (optional, press Enter to use default): ").strip()
            
            print("\n" + "-" * 60)
            
            # Send SMS
            await send_sms_via_mcp(
                to_number=to_number,
                message=message,
                from_number=from_number if from_number else None
            )
            
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """
    Main entry point
    """
    if len(sys.argv) > 1:
        # Command-line mode
        if len(sys.argv) < 3:
            print("Usage:")
            print("  Interactive mode:  python mcp_client.py")
            print("  Command-line mode: python mcp_client.py <to_number> <message> [from_number]")
            print("\nExample:")
            print('  python mcp_client.py "+14155551234" "Hello from MCP!" "+14155556789"')
            sys.exit(1)
        
        to_number = sys.argv[1]
        message = sys.argv[2]
        from_number = sys.argv[3] if len(sys.argv) > 3 else None
        
        await send_sms_via_mcp(to_number, message, from_number)
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
