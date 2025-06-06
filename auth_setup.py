#!/usr/bin/env python3
"""
Standalone authentication setup script for mcp-gsuite.
Run this script first to authenticate your Google account before using the MCP server.
"""

import sys
import os
import logging
from src.mcp_gsuite import gauth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-gsuite-auth")

def main():
    if len(sys.argv) != 2:
        print("Usage: python auth_setup.py <email@example.com>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    
    # Validate user exists in accounts
    accounts = gauth.get_account_info()
    if len(accounts) == 0:
        logger.error("No accounts specified in .accounts.json")
        sys.exit(1)
    
    if user_id not in [a.email for a in accounts]:
        logger.error(f"Account for email: {user_id} not specified in .accounts.json")
        logger.info(f"Available accounts: {', '.join([a.email for a in accounts])}")
        sys.exit(1)

    # Check if already authenticated
    credentials = gauth.get_stored_credentials(user_id=user_id)
    if credentials and not credentials.access_token_expired:
        logger.info(f"User {user_id} is already authenticated!")
        return

    # Start authentication flow
    logger.info(f"Starting authentication for {user_id}")
    auth_url = gauth.get_authorization_url(user_id, state={})
    
    print(f"\n{'='*60}")
    print(f"AUTHENTICATION REQUIRED FOR: {user_id}")
    print(f"{'='*60}")
    print(f"1. Open this URL in your browser:")
    print(f"   {auth_url}")
    print(f"2. Complete the OAuth flow")
    print(f"3. The authentication will be saved automatically")
    print(f"{'='*60}\n")
    
    # Start the OAuth callback server (blocking version for standalone script)
    import subprocess
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs
    import threading
    
    class AuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            if url.path != "/code":
                self.send_response(404)
                self.end_headers()
                return

            query = parse_qs(url.query)
            if "code" not in query:
                self.send_response(400)
                self.end_headers()
                return
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Authentication successful! You can close this tab.".encode("utf-8"))
            self.wfile.flush()

            # Exchange code for credentials
            try:
                creds = gauth.get_credentials(authorization_code=query["code"][0], state={})
                logger.info(f"Authentication completed successfully for {user_id}")
                self.server.auth_success = True
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                self.server.auth_success = False

            # Shutdown server
            def shutdown():
                self.server.shutdown()
            threading.Thread(target=shutdown, daemon=True).start()

    # Open browser
    if sys.platform == "darwin":
        subprocess.Popen(['open', auth_url])
    else:
        import webbrowser
        webbrowser.open(auth_url)
    
    # Start callback server
    server_address = ('', 4100)
    httpd = HTTPServer(server_address, AuthCallbackHandler)
    httpd.auth_success = False
    
    logger.info("Waiting for authentication callback...")
    try:
        httpd.serve_forever()
        if httpd.auth_success:
            logger.info(f"Authentication completed for {user_id}")
        else:
            logger.error("Authentication failed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Authentication cancelled by user")
        sys.exit(1)

if __name__ == "__main__":
    main() 