# MCP Client for Telephony Server

This client sends SMS messages via the Telephony MCP Server using the Model Context Protocol (MCP).

## 📋 Prerequisites

1. **MCP Server Running**: The telephony MCP server must be running at `http://127.0.0.1:8000/mcp/`
   ```bash
   .venv/bin/python main.py
   ```

2. **OpenLIT Dashboard (Optional)**: For observability, OpenLIT should be running
   ```bash
   # In the openlit directory
   docker-compose up -d
   # Dashboard: http://localhost:3000
   ```

## 🚀 Usage

### Interactive Mode

Run without arguments for an interactive session:

```bash
.venv/bin/python mcp_client.py
```

You'll be prompted to enter:
- Destination phone number (e.g., `+14155551234`)
- Message text
- Sender number (optional, press Enter to use server default)

### Command-Line Mode

Send SMS directly from command line:

```bash
# Basic usage (uses server's default sender number)
.venv/bin/python mcp_client.py "+14155551234" "Hello from MCP!"

# With custom sender number
.venv/bin/python mcp_client.py "+14155551234" "Hello!" "+14155556789"
```

### Test Script

Use the included test script:

```bash
# Edit test_sms_client.py to set your phone number
.venv/bin/python test_sms_client.py
```

## 📱 Examples

### Example 1: Quick SMS
```bash
.venv/bin/python mcp_client.py "+14155551234" "Meeting starts in 10 minutes!"
```

### Example 2: Interactive Session
```bash
$ .venv/bin/python mcp_client.py

============================================================
📱 Telephony MCP Client - SMS Sender
============================================================

Interactive Mode - Send SMS via MCP Server
Type 'quit' or 'exit' to stop

📞 Enter destination number (e.g., +14155551234): +14155551234
💬 Enter message text: Hello from MCP!
📤 Enter sender number (optional, press Enter to use default): 

------------------------------------------------------------
🔌 Connecting to MCP server at http://127.0.0.1:8000/mcp/
📋 Fetching available tools...
✅ Connected! Server: Telephony
📱 Available tools: ['make_call', 'send_sms', 'transfer_call', ...]

📤 Sending SMS to +14155551234...
💬 Message: Hello from MCP!
✅ Result: SMS sent to +14155551234.
------------------------------------------------------------
```

## 🔍 Observability

With OpenLIT running, all SMS operations are traced:

1. **Client → Server**: HTTP requests to MCP endpoint
2. **Server → Vonage**: SMS API calls
3. **Performance**: Response times, success rates
4. **Errors**: Detailed error traces

View in OpenLIT Dashboard: http://localhost:3000

## 🛠️ How It Works

1. **Initialize MCP Session**
   - Connects to `http://127.0.0.1:8000/mcp/`
   - Performs MCP protocol handshake
   - Sends initialization notification

2. **List Available Tools**
   - Queries server for available MCP tools
   - Confirms `send_sms` tool is available

3. **Call send_sms Tool**
   - Sends tool call request with parameters:
     - `to`: Destination phone number
     - `text`: Message content
     - `from_`: Sender number (optional)
   
4. **Receive Response**
   - Processes tool result
   - Displays success/error message

## 📊 MCP Protocol Details

The client uses JSON-RPC 2.0 over HTTP:

### Initialize Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {"listChanged": true},
      "sampling": {}
    },
    "clientInfo": {
      "name": "telephony-mcp-client",
      "version": "1.0.0"
    }
  }
}
```

### Tool Call Request
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "send_sms",
    "arguments": {
      "to": "+14155551234",
      "text": "Hello from MCP!",
      "from_": "+14155556789"
    }
  }
}
```

## ⚙️ Configuration

The client connects to the MCP server at:
- **URL**: `http://127.0.0.1:8000/mcp/`

To change the server URL, edit `mcp_client.py`:
```python
mcp_url = "http://127.0.0.1:8000/mcp/"  # Change this line
```

## 🐛 Troubleshooting

### Connection Refused
```
❌ Failed to initialize MCP session: Cannot connect
```
**Solution**: Make sure the MCP server is running:
```bash
.venv/bin/python main.py
```

### SMS Not Sending
```
❌ Failed to send SMS: Vonage API credentials are not fully configured
```
**Solution**: Check your `.env` file has:
- `VONAGE_API_KEY`
- `VONAGE_API_SECRET`
- `VONAGE_LVN` (sender number)

### Tool Not Found
```
❌ Error: Tool 'send_sms' not found
```
**Solution**: Verify the server has the SMS tool enabled. Check server logs.

## 📚 Related Files

- `mcp_client.py` - Main MCP client implementation
- `test_sms_client.py` - Test script with example usage
- `main.py` - MCP server entry point
- `servers/telephony_server.py` - Server implementation with send_sms tool

## 🔗 Resources

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [OpenLIT Documentation](https://docs.openlit.io/)
- [Vonage SMS API](https://developer.vonage.com/en/messaging/sms/overview)
