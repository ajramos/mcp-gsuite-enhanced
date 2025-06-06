# mcp-gsuite-enhanced

**Enhanced MCP server for Google Workspace with Google Meet integration and bug fixes**

[![Enhanced Version](https://img.shields.io/badge/Enhanced-Version-brightgreen)](https://github.com/ajramos/mcp-gsuite-enhanced) 
[![Original Project](https://img.shields.io/badge/Based%20on-mcp--gsuite-blue)](https://github.com/MarkusPfundstein/mcp-gsuite)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

MCP server to interact with Google products with enhanced functionality including working Google Meet integration and calendar event updates.

## Table of Contents

- [Quick Start](#🚀-quick-start)
- [Enhanced Features](#🎯-enhanced-features)
- [Features & Capabilities](#features--capabilities)
- [Example Prompts](#💡-example-prompts-to-try)
- [Installation](#install)
- [Google Authentication Setup](#setup-google-authentication)
- [Configuration Examples](#configuration-examples)
- [Google Meet Integration](#enhanced-google-meet-integration)
- [Development](#development)
- [Security](#security)
- [Credits](#credits)
- [License](#license)
- [Contributing](#contributing)
- [Support](#support)

## 🚀 Quick Start

**Get Google Workspace MCP running in 5 minutes!**

### Prerequisites
- Python 3.13+ and `uv` installed
- Google account with Gmail/Calendar access
- Cursor IDE (recommended) or any MCP client

### Step 1: Clone and Install
```bash
git clone https://github.com/ajramos/mcp-gsuite-enhanced.git
cd mcp-gsuite-enhanced
uv sync
```

### Step 2: Setup Google Cloud (One-time setup)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable **Gmail API** + **Google Calendar API**
3. Create **OAuth 2.0 Desktop** credentials 
4. Download and save as **`.gauth.json`** in project directory

### Step 3: Configure Accounts
Create **`.accounts.json`**:
```json
{
  "accounts": [
    {
      "email": "your-email@gmail.com",
      "account_type": "personal", 
      "extra_info": "Main personal Gmail and Calendar"
    }
  ]
}
```

### Step 4: Quick Configuration Check
```bash
python cursor_setup.py
```
This shows authentication status and generates Cursor configuration.

### Step 5: Authenticate
```bash
python auth_setup.py your-email@gmail.com
```
Opens browser for OAuth flow - grant permissions and you're done!

### Step 6: Configure in Cursor
1. Copy the JSON configuration from Step 4
2. Cursor → Settings (Cmd+,) → Search "MCP" 
3. Paste configuration and restart Cursor

### Step 7: Test it! 🎉
Try these commands in Cursor:
- *"List my calendars"* 
- *"Show my unread emails"*
- *"Create a test meeting with Google Meet link"*

**That's it!** You now have full Google Workspace integration with automatic Google Meet links! 

---

## 🎯 Enhanced Features

This enhanced version includes:
- ✅ **Working Google Meet integration** - Automatic Meet links in calendar events
- ✅ **Fixed `update_calendar_event`** - Previously broken, now fully functional
- ✅ **Improved attendee processing** - Fixed email parsing bugs
- ✅ **Updated dependencies** - Latest Google APIs and MCP version
- ✅ **Better error handling** - More robust calendar operations
- ✅ **Setup utilities** - `auth_setup.py` and `cursor_setup.py` for easy configuration

## Features & Capabilities

Right now, this MCP server supports Gmail and Calendar integration with the following capabilities:

1. General
* Multiple google accounts

2. Gmail
* Get your Gmail user information
* Query emails with flexible search (e.g., unread, from specific senders, date ranges, with attachments)
* Retrieve complete email content by ID
* Create new draft emails with recipients, subject, body and CC options
* Delete draft emails
* Reply to existing emails (can either send immediately or save as draft)
* Retrieve multiple emails at once by their IDs
* Download and save email attachments to local files
* Bulk save multiple attachments from different emails

3. Calendar
* List available calendars for your account
* Get calendar events within a specified time range
* Create new calendar events with attendees and **automatic Google Meet links** 🎪
* **Update existing calendar events** (summary, time, attendees) ⚡
* Delete calendar events
* Full timezone support for international scheduling

## 💡 Example Prompts to Try

### 📧 Gmail Operations
- **Email Search & Retrieval**
  - *"Retrieve my latest unread messages"*
  - *"Search my emails from the Scrum Master"*
  - *"Retrieve all emails from accounting"*
  - *"Take the email about ABC and summarize it"*

- **Email Composition & Replies**  
  - *"Write a nice response to Alice's last email and upload a draft"*
  - *"Reply to Bob's email with a Thank you note. Store it as draft"*

- **Attachment Management**
  - *"Download all attachments from emails with subject containing 'invoice'"*
  - *"Save attachments from all emails from john@company.com this week"*

### 📅 Calendar Management
- **Agenda & Scheduling**
  - *"What do I have on my agenda tomorrow?"*
  - *"Check my private account's Family agenda for next week"*
  - *"I need to plan an event with Tim for 2hrs next week. Suggest some time slots"*

- **Event Creation with Google Meet** 🎪
  - *"Create a meeting with John next Friday and include a Google Meet link"*
  - *"Schedule a client call for Thursday 2 PM and invite john@company.com"*
  - *"Create a team standup for every Monday at 9 AM with Google Meet"*
  - *"Create a project review meeting for tomorrow at 3 PM with Google Meet link and invite the whole team"*

- **Event Updates** ⚡ *(Enhanced Feature)*
  - *"Update my 3pm meeting to include Sarah as an attendee"*
  - *"Update the quarterly planning meeting to change the time to 4 PM and add sarah@company.com"*
  - *"Change tomorrow's team meeting location to Conference Room B"*

- **Advanced Calendar Queries**
  - *"List all my calendar events for next week that have Google Meet links"*
  - *"Show me all recurring meetings I have this month"*
  - *"Find all meetings with external attendees scheduled for next week"*

## Install

### Option 1: Enhanced Version (Recommended) 🚀

This enhanced version includes all the Google Meet fixes and improvements.

#### Cursor IDE Setup (Recommended)

For Cursor IDE users, use the setup helper script:

```bash
python cursor_setup.py
```

This will generate the correct MCP configuration and provide step-by-step instructions for adding it to your Cursor settings.

#### Manual Installation

You can install this enhanced version using uv (recommended):

```bash
# Clone and install from source (until published)
git clone https://github.com/ajramos/mcp-gsuite-enhanced
cd mcp-gsuite-enhanced
uv sync
```

Or with pip:

```bash
# Clone and install from source (until published)
git clone https://github.com/ajramos/mcp-gsuite-enhanced
cd mcp-gsuite-enhanced
pip install -e .
```

### Option 2: Original Version via Smithery 📦

If you prefer the original version (without the Google Meet enhancements), you can install it via Smithery:

```bash
npx -y @smithery/cli install mcp-gsuite --client claude
```

**Note:** The original version has some limitations:
- ❌ Google Meet integration may not work reliably
- ❌ `update_calendar_event` functionality has known issues
- ❌ Attendee processing bugs

## Setup Google Authentication

### Google Cloud Configuration

You'll need to create a Google Cloud project and configure OAuth2 credentials:

#### Step 1: Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the required APIs:
   - Go to "APIs & Services" → "Library"
   - Search for **"Gmail API"** and enable it
   - Search for **"Google Calendar API"** and enable it

#### Step 2: Setup OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select **"Desktop application"** as the application type
4. Configure the OAuth consent screen if prompted
5. Download the credentials JSON file and save it as **`.gauth.json`** in your project directory

#### Step 3: Configure Your Google Accounts

Create a `.accounts.json` file in your project directory to specify which Google accounts to use:

```json
{
  "accounts": [
    {
      "email": "your-work@company.com",
      "account_type": "work",
      "extra_info": "Work account with company calendar"
    },
    {
      "email": "your-personal@gmail.com", 
      "account_type": "personal",
      "extra_info": "Personal account with family calendar"
    }
  ]
}
```

**Fields explanation:**
- **`email`**: Your Google account email address
- **`account_type`**: Category like "work", "personal", etc. (helps with organization)
- **`extra_info`**: Additional context that helps the AI understand this account's purpose

#### Step 4: Authenticate Your Google Accounts

Once you have both `.gauth.json` and `.accounts.json` files, run the authentication setup for each account:

```bash
python auth_setup.py your-work@company.com
python auth_setup.py your-personal@gmail.com
```

This script will automatically handle the OAuth flow and store your credentials securely in `.oauth2.{email}.json` files.

> **⚠️ SECURITY WARNING**: Never commit credential files (`.gauth.json`, `.accounts.json`, `.oauth2.*.json`) to version control! Add them to your `.gitignore` file to prevent accidental exposure of sensitive authentication data.

### OAuth 2.0 Scopes (Automatic)

The server automatically requests these permissions - **no manual configuration needed**:

```json
[
  "openid",
  "https://www.googleapis.com/auth/userinfo.email",
  "https://mail.google.com/",
  "https://www.googleapis.com/auth/calendar"
]
```

These scopes allow the server to:
- ✅ Access your Gmail (read, send, manage drafts)
- ✅ Manage your Google Calendar (create, update, delete events)
- ✅ Create Google Meet links automatically
- ✅ Identify your Google account

### Configuration Examples

#### Claude Desktop (Enhanced Version)

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mcp-gsuite-enhanced": {
      "command": "uv",
      "args": [
        "--directory", 
        "/path/to/mcp-gsuite-enhanced",
        "run",
        "mcp-gsuite-enhanced"
      ]
    }
  }
}
```

#### Claude Desktop (Original Version)

If you installed via Smithery, your configuration is automatically handled. Alternatively:

```json
{
  "mcpServers": {
    "mcp-gsuite": {
      "command": "uvx",
      "args": ["mcp-gsuite"]
    }
  }
}
```

#### Using with uvx (Enhanced Version)

```json
{
  "mcpServers": {
    "mcp-gsuite-enhanced": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-gsuite-enhanced",
        "run",
        "mcp-gsuite-enhanced"
      ]
    }
  }
}
```



## Enhanced Google Meet Integration

The enhanced version automatically creates Google Meet links for new calendar events:

```json
{
  "calendar_id": "primary",
  "summary": "Team Standup",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T10:30:00Z",
  "attendees": "team@company.com,lead@company.com",
  "create_meet_link": true
}
```

Results in a calendar event with:
- ✅ Automatic Google Meet link
- ✅ Phone dial-in numbers
- ✅ Meeting PIN
- ✅ All attendees invited

## Development

To set up for development:

```bash
git clone https://github.com/ajramos/mcp-gsuite-enhanced
cd mcp-gsuite-enhanced
uv sync
uv run mcp-gsuite-enhanced
```

### Debugging with MCP Inspector

Since MCP servers run over stdio, debugging can be challenging. For the best debugging experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-gsuite-enhanced run mcp-gsuite-enhanced
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

#### Server Logs

You can also watch the server logs with this command:

```bash
# macOS
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-gsuite-enhanced.log

# Linux 
tail -n 20 -f ~/.config/Claude/logs/mcp-server-mcp-gsuite-enhanced.log

# Windows
Get-Content "$env:APPDATA\Claude\logs\mcp-server-mcp-gsuite-enhanced.log" -Wait -Tail 20
```

## Security

- All authentication is handled locally using OAuth 2.0
- Credentials are stored securely in local files
- No data is sent to third parties except Google's APIs
- Supports multiple Google accounts with isolated credentials

## Credits

Based on [mcp-gsuite](https://github.com/MarkusPfundstein/mcp-gsuite) by Markus Pfundstein.

Enhanced with Google Meet integration, bug fixes, and improved functionality by Angel Ramos.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues with the enhanced features:

1. **Check the logs** using the debugging instructions above
2. **Verify authentication** by running `python auth_setup.py <your-email>`
3. **Open an issue** with:
   - Your operating system
   - Python version
   - Error messages or logs
   - Steps to reproduce the issue

For general MCP questions, see the [Model Context Protocol documentation](https://modelcontextprotocol.io/).
