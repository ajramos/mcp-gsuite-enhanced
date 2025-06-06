#!/usr/bin/env python3
"""
Cursor-specific configuration for MCP GSuite
"""
import json
import os
import sys

def create_cursor_mcp_config():
    """Creates Cursor-specific configuration"""
    
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    config = {
        "mcpServers": {
            "mcp-gsuite": {
                "command": "uv",
                "args": [
                    "--directory", 
                    current_dir,
                    "run",
                    "mcp-gsuite"
                ],
                "env": {
                    "PYTHONPATH": current_dir,
                    "UV_PROJECT_ENVIRONMENT": os.path.join(current_dir, ".venv")
                }
            }
        }
    }
    
    print("🔧 Cursor Configuration:")
    print("="*50)
    print(json.dumps(config, indent=2))
    print("="*50)
    
    # Cursor-specific instructions
    print("\n📋 CURSOR SETUP INSTRUCTIONS:")
    print("1. Go to Cursor → Settings (Cmd+,)")
    print("2. Search for 'MCP' in settings")
    print("3. Add the configuration above to the corresponding field")
    print("4. Save and restart Cursor")
    print("5. Verify that the server is not already running:")
    print(f"   ps aux | grep mcp-gsuite")
    print("6. If there are processes, terminate them before activating in Cursor")
    
    return config

def check_authentication():
    """Verifies that authentication is configured"""
    from src.mcp_gsuite import gauth
    
    accounts = gauth.get_account_info()
    authenticated = []
    
    for account in accounts:
        creds = gauth.get_stored_credentials(user_id=account.email)
        if creds and not creds.access_token_expired:
            authenticated.append(account.email)
    
    print(f"\n🔐 AUTHENTICATION STATUS:")
    print(f"Configured accounts: {len(accounts)}")
    print(f"Authenticated accounts: {len(authenticated)}")
    
    if len(authenticated) == 0:
        print("❌ NO ACCOUNTS ARE AUTHENTICATED")
        print("Run: python auth_setup.py <email>")
        return False
    else:
        print("✅ Authentication successful")
        for email in authenticated:
            print(f"   - {email}")
        return True

def main():
    print("🚀 MCP GSUITE CONFIGURATOR FOR CURSOR\n")
    
    # Check authentication
    auth_ok = check_authentication()
    
    # Create configuration
    config = create_cursor_mcp_config()
    
    if not auth_ok:
        print("\n⚠️  IMPORTANT: You must authenticate at least one account before using MCP in Cursor")
        return
    
    print("\n✅ Everything ready to configure in Cursor!")
    print("\n💡 ADDITIONAL TIPS:")
    print("- If Cursor keeps giving errors, try:")
    print("  1. Disable MCP, completely close Cursor")
    print("  2. Restart Cursor")
    print("  3. Re-enable MCP with the new configuration")
    print("- Port 4100 must be available")
    print("- Verify that no other MCP processes are running")

if __name__ == "__main__":
    main() 