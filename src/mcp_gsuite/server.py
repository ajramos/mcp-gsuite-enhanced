import logging
import sys
import asyncio
import json
from typing import Any
import traceback

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from . import gauth
from . import tools_gmail
from . import tools_calendar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Initialize the server
    server = Server("mcp-gsuite")
    
    # Log platform and account info
    logger.info(sys.platform)
    accounts = gauth.get_account_info()
    for account in accounts:
        creds = gauth.get_stored_credentials(user_id=account.email)
        if creds:
            logger.info(f"found credentials for {account.email}")
    logger.info(f"Available accounts: {', '.join([a.email for a in accounts])}")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools."""
        logger.info("Listing tools")
        
        tools = [
            # Calendar tools
            types.Tool(
                name="list_calendars",
                description="List all calendars for the authenticated user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "__user_id__": {
                            "type": "string",
                            "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                        }
                    },
                    "required": ["__user_id__"]
                }
            ),
            types.Tool(
                name="get_calendar_events",
                description="Get events from a specific calendar",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "__user_id__": {
                            "type": "string",
                            "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID to get events from"
                        },
                        "time_min": {
                            "type": "string",
                            "description": "Start time for events (ISO format)"
                        },
                        "time_max": {
                            "type": "string",
                            "description": "End time for events (ISO format)"
                        }
                    },
                    "required": ["__user_id__", "calendar_id"]
                }
            ),
            types.Tool(
                name="create_calendar_event",
                description="Create a new calendar event with attendees and Google Meet link",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "__user_id__": {
                            "type": "string",
                            "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID to create event in"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Event title/summary"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time (ISO format)"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time (ISO format)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location of the event (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description or notes for the event (optional)"
                        },
                                                 "attendees": {
                             "type": "string",
                             "description": "Comma-separated list of attendee emails (optional)"
                         },
                        "send_notifications": {
                            "type": "boolean",
                            "description": "Whether to send notifications to attendees",
                            "default": True
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone for the event (e.g. 'America/New_York'). Defaults to UTC if not specified."
                        },
                        "create_meet_link": {
                            "type": "boolean",
                            "description": "Whether to create a Google Meet link for the event",
                            "default": True
                        }
                    },
                    "required": ["__user_id__", "calendar_id", "summary", "start_time", "end_time"]
                }
                         ),
             types.Tool(
                 name="delete_calendar_event",
                 description="Delete a calendar event",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "calendar_id": {
                             "type": "string",
                             "description": "Calendar ID containing the event"
                         },
                         "event_id": {
                             "type": "string",
                             "description": "Event ID to delete"
                         }
                     },
                     "required": ["__user_id__", "calendar_id", "event_id"]
                 }
             ),
             types.Tool(
                 name="update_calendar_event",
                 description="Update an existing calendar event",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "calendar_id": {
                             "type": "string",
                             "description": "Calendar ID containing the event"
                         },
                         "event_id": {
                             "type": "string",
                             "description": "Event ID to update"
                         },
                         "summary": {
                             "type": "string",
                             "description": "Event title/summary (optional)"
                         },
                         "start_time": {
                             "type": "string",
                             "description": "Start time (ISO format) (optional)"
                         },
                         "end_time": {
                             "type": "string",
                             "description": "End time (ISO format) (optional)"
                         },
                         "create_meet_link": {
                             "type": "boolean",
                             "description": "Whether to create a Google Meet link (only if not already present)",
                             "default": False
                         },
                         "attendees": {
                             "type": "string",
                             "description": "Comma-separated list of attendee emails (optional)"
                         }
                     },
                     "required": ["__user_id__", "calendar_id", "event_id"]
                 }
             ),
             # Gmail tools
             types.Tool(
                name="query_emails",
                description="Search and query emails",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "__user_id__": {
                            "type": "string",
                            "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                        },
                        "query": {
                            "type": "string",
                            "description": "Gmail search query"
                        }
                    },
                    "required": ["__user_id__"]
                }
            ),
            types.Tool(
                name="get_email_by_id",
                description="Get email content by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "__user_id__": {
                            "type": "string",
                            "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                        },
                        "email_id": {
                            "type": "string",
                            "description": "Email ID to retrieve"
                        }
                                         },
                     "required": ["__user_id__", "email_id"]
                 }
             ),
             types.Tool(
                 name="create_draft",
                 description="Create a draft email",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "to": {
                             "type": "string",
                             "description": "Recipient email address"
                         },
                         "subject": {
                             "type": "string",
                             "description": "Email subject"
                         },
                         "body": {
                             "type": "string",
                             "description": "Email body content"
                         }
                     },
                     "required": ["__user_id__", "to", "subject", "body"]
                 }
             ),
             types.Tool(
                 name="delete_draft",
                 description="Delete a draft email",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "draft_id": {
                             "type": "string",
                             "description": "Draft ID to delete"
                         }
                     },
                     "required": ["__user_id__", "draft_id"]
                 }
             ),
             types.Tool(
                 name="reply_email",
                 description="Reply to an email",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "thread_id": {
                             "type": "string",
                             "description": "Thread ID to reply to"
                         },
                         "body": {
                             "type": "string",
                             "description": "Reply body content"
                         },
                         "send_directly": {
                             "type": "boolean",
                             "description": "Whether to send directly or save as draft"
                         }
                     },
                     "required": ["__user_id__", "thread_id", "body"]
                 }
             ),
             types.Tool(
                 name="get_attachment",
                 description="Download an email attachment",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "message_id": {
                             "type": "string",
                             "description": "Message ID containing the attachment"
                         },
                         "attachment_id": {
                             "type": "string",
                             "description": "Attachment ID to download"
                         }
                     },
                     "required": ["__user_id__", "message_id", "attachment_id"]
                 }
             ),
             types.Tool(
                 name="bulk_get_emails",
                 description="Get multiple emails by their IDs",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "message_ids": {
                             "type": "array",
                             "items": {"type": "string"},
                             "description": "List of message IDs to retrieve"
                         }
                     },
                     "required": ["__user_id__", "message_ids"]
                 }
             ),
             types.Tool(
                 name="bulk_save_attachments",
                 description="Save multiple attachments from emails",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "attachments": {
                             "type": "array",
                             "items": {
                                 "type": "object",
                                 "properties": {
                                     "message_id": {"type": "string"},
                                     "attachment_id": {"type": "string"},
                                     "filename": {"type": "string"}
                                 }
                             },
                             "description": "List of attachments to save"
                         }
                     },
                     "required": ["__user_id__", "attachments"]
                 }
             )
         ]
        
        return tools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool calls."""
        logger.info(f"call_tool: {name} with arguments: {arguments}")
        
        try:
            if not isinstance(arguments, dict):
                raise RuntimeError("arguments must be dictionary")
            
            if "__user_id__" not in arguments:
                raise RuntimeError("__user_id__ argument is missing")

            user_id = arguments["__user_id__"]
            
            # Verify authentication
            accounts = gauth.get_account_info()
            if user_id not in [a.email for a in accounts]:
                raise RuntimeError(f"Account for email: {user_id} not specified in .accounts.json")

            credentials = gauth.get_stored_credentials(user_id=user_id)
            if not credentials:
                raise RuntimeError(f"No credentials found for {user_id}. Please run: python auth_setup.py {user_id}")
            
            if credentials.access_token_expired:
                logger.info("Access token expired, attempting refresh...")
                try:
                    user_info = gauth.get_user_info(credentials=credentials)
                    gauth.store_credentials(credentials=credentials, user_id=user_id)
                    logger.info(f"Successfully refreshed credentials for {user_id}")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {e}")
                    raise RuntimeError(f"Failed to refresh credentials for {user_id}: {e}")

            # Handle different tools
            if name == "list_calendars":
                from .tools_calendar import ListCalendarsToolHandler
                handler = ListCalendarsToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "get_calendar_events":
                from .tools_calendar import GetCalendarEventsToolHandler
                handler = GetCalendarEventsToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "create_calendar_event":
                from .tools_calendar import CreateCalendarEventToolHandler
                handler = CreateCalendarEventToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "query_emails":
                from .tools_gmail import QueryEmailsToolHandler
                handler = QueryEmailsToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "get_email_by_id":
                from .tools_gmail import GetEmailByIdToolHandler
                handler = GetEmailByIdToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "delete_calendar_event":
                from .tools_calendar import DeleteCalendarEventToolHandler
                handler = DeleteCalendarEventToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "update_calendar_event":
                from .tools_calendar import UpdateCalendarEventToolHandler
                handler = UpdateCalendarEventToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "create_draft":
                from .tools_gmail import CreateDraftToolHandler
                handler = CreateDraftToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "delete_draft":
                from .tools_gmail import DeleteDraftToolHandler
                handler = DeleteDraftToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "reply_email":
                from .tools_gmail import ReplyEmailToolHandler
                handler = ReplyEmailToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "get_attachment":
                from .tools_gmail import GetAttachmentToolHandler
                handler = GetAttachmentToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "bulk_get_emails":
                from .tools_gmail import BulkGetEmailsByIdsToolHandler
                handler = BulkGetEmailsByIdsToolHandler()
                return handler.run_tool(arguments)
                
            elif name == "bulk_save_attachments":
                from .tools_gmail import BulkSaveAttachmentsToolHandler
                handler = BulkSaveAttachmentsToolHandler()
                return handler.run_tool(arguments)
                
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(f"Error during call_tool: {str(e)}")
            raise RuntimeError(f"Caught Exception. Error: {str(e)}")

    # Start the server
    logger.info("Starting MCP GSuite server...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-gsuite",
                server_version="0.4.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )