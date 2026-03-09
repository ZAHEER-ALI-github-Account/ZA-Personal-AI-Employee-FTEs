---
name: email-mcp-server
description: MCP server for sending emails via Gmail API
---

# Email MCP Server

## Tools

- `send_email` - Send emails
- `create_draft` - Create drafts
- `search_emails` - Search Gmail
- `read_email` - Read emails
- `mark_as_read` - Mark as read

## Usage

```python
from mcp_servers.email_mcp_server import EmailMCPServer

server = EmailMCPServer()
server.send_email(to="client@example.com", subject="Invoice", body="Please find attached...")
```
