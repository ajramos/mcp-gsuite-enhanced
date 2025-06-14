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
from . import __version__

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
             ),
             # Additional Gmail tools
             types.Tool(
                 name="send_email",
                 description="Send an email via Gmail",
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
                         },
                         "cc": {
                             "type": "string",
                             "description": "CC recipients (optional)"
                         },
                         "bcc": {
                             "type": "string",
                             "description": "BCC recipients (optional)"
                         }
                     },
                     "required": ["__user_id__", "to", "subject", "body"]
                 }
             ),
             types.Tool(
                 name="list_drafts",
                 description="List Gmail drafts",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "max_results": {
                             "type": "integer",
                             "description": "Maximum number of drafts to return (default: 10)"
                         }
                     },
                     "required": ["__user_id__"]
                 }
             ),
             types.Tool(
                 name="get_unread_emails",
                 description="Get unread Gmail emails",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "max_results": {
                             "type": "integer",
                             "description": "Maximum number of emails to return (default: 10)"
                         }
                     },
                     "required": ["__user_id__"]
                 }
             ),
             # Advanced Gmail management tools
             types.Tool(
                 name="mark_email_read",
                 description="Mark a Gmail email as read",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "email_id": {
                             "type": "string",
                             "description": "The ID of the email to mark as read"
                         }
                     },
                     "required": ["__user_id__", "email_id"]
                 }
             ),
             types.Tool(
                 name="trash_email",
                 description="Move a Gmail email to trash",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "email_id": {
                             "type": "string",
                             "description": "The ID of the email to move to trash"
                         }
                     },
                     "required": ["__user_id__", "email_id"]
                 }
             ),
             types.Tool(
                 name="list_labels",
                 description="List all Gmail labels",
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
                 name="create_label",
                 description="Create a new Gmail label",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "name": {
                             "type": "string",
                             "description": "Name of the label to create"
                         },
                         "visibility": {
                             "type": "string",
                             "description": "Label visibility (labelShow, labelHide)",
                             "default": "labelShow"
                         }
                     },
                     "required": ["__user_id__", "name"]
                 }
             ),
             types.Tool(
                 name="apply_label",
                 description="Apply a label to a Gmail email",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "email_id": {
                             "type": "string",
                             "description": "The ID of the email"
                         },
                         "label_id": {
                             "type": "string",
                             "description": "The ID of the label to apply"
                         }
                     },
                     "required": ["__user_id__", "email_id", "label_id"]
                 }
             ),
             types.Tool(
                 name="remove_label",
                 description="Remove a label from a Gmail email",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "email_id": {
                             "type": "string",
                             "description": "The ID of the email"
                         },
                         "label_id": {
                             "type": "string",
                             "description": "The ID of the label to remove"
                         }
                     },
                     "required": ["__user_id__", "email_id", "label_id"]
                 }
             ),
             types.Tool(
                 name="archive_email",
                 description="Archive a Gmail email (remove from inbox)",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "email_id": {
                             "type": "string",
                             "description": "The ID of the email to archive"
                         }
                     },
                     "required": ["__user_id__", "email_id"]
                 }
             ),
             types.Tool(
                 name="batch_archive_emails",
                 description="Archive multiple Gmail emails at once",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "email_ids": {
                             "type": "array",
                             "items": {"type": "string"},
                             "description": "List of email IDs to archive"
                         }
                     },
                     "required": ["__user_id__", "email_ids"]
                 }
             ),
             types.Tool(
                 name="list_archived_emails",
                 description="List archived Gmail emails",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "max_results": {
                             "type": "integer",
                             "description": "Maximum number of archived emails to return (default: 100)",
                             "default": 100
                         }
                     },
                     "required": ["__user_id__"]
                 }
             ),
             types.Tool(
                 name="restore_email_to_inbox",
                 description="Restore an archived email back to inbox",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "email_id": {
                             "type": "string",
                             "description": "The ID of the email to restore to inbox"
                         }
                     },
                     "required": ["__user_id__", "email_id"]
                 }
             ),
             types.Tool(
                 name="delete_label",
                 description="Delete a Gmail label",
                 inputSchema={
                     "type": "object",
                     "properties": {
                         "__user_id__": {
                             "type": "string",
                             "description": f"The EMAIL of the Google account. Available accounts: {', '.join([a.email for a in accounts])}"
                         },
                         "label_id": {
                             "type": "string",
                             "description": "The ID of the label to delete"
                         }
                     },
                     "required": ["__user_id__", "label_id"]
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

            # Handle different tools using registry
            from .tools_calendar import (
                ListCalendarsToolHandler, GetCalendarEventsToolHandler, 
                CreateCalendarEventToolHandler, DeleteCalendarEventToolHandler,
                UpdateCalendarEventToolHandler
            )
            from .tools_gmail import (
                QueryEmailsToolHandler, GetEmailByIdToolHandler, 
                CreateDraftToolHandler, DeleteDraftToolHandler,
                ReplyEmailToolHandler, GetAttachmentToolHandler,
                BulkGetEmailsByIdsToolHandler, BulkSaveAttachmentsToolHandler,
                SendEmailToolHandler, ListDraftsToolHandler, GetUnreadEmailsToolHandler,
                MarkEmailReadToolHandler, TrashEmailToolHandler, ListLabelsToolHandler,
                CreateLabelToolHandler, ApplyLabelToolHandler, RemoveLabelToolHandler,
                ArchiveEmailToolHandler, BatchArchiveEmailsToolHandler, 
                ListArchivedEmailsToolHandler, RestoreEmailToInboxToolHandler, DeleteLabelToolHandler
            )
            
            # Tool handler registry
            tool_handlers = {
                "list_calendars": ListCalendarsToolHandler,
                "get_calendar_events": GetCalendarEventsToolHandler,
                "create_calendar_event": CreateCalendarEventToolHandler,
                "delete_calendar_event": DeleteCalendarEventToolHandler,
                "update_calendar_event": UpdateCalendarEventToolHandler,
                "query_emails": QueryEmailsToolHandler,
                "get_email_by_id": GetEmailByIdToolHandler,
                "create_draft": CreateDraftToolHandler,
                "delete_draft": DeleteDraftToolHandler,
                "reply_email": ReplyEmailToolHandler,
                "get_attachment": GetAttachmentToolHandler,
                "bulk_get_emails": BulkGetEmailsByIdsToolHandler,
                "bulk_save_attachments": BulkSaveAttachmentsToolHandler,
                # Step 2 additions
                "send_email": SendEmailToolHandler,
                "list_drafts": ListDraftsToolHandler,
                "get_unread_emails": GetUnreadEmailsToolHandler,
                # Advanced Gmail management tools
                "mark_email_read": MarkEmailReadToolHandler,
                "trash_email": TrashEmailToolHandler,
                "list_labels": ListLabelsToolHandler,
                "create_label": CreateLabelToolHandler,
                "apply_label": ApplyLabelToolHandler,
                "remove_label": RemoveLabelToolHandler,
                "archive_email": ArchiveEmailToolHandler,
                "batch_archive_emails": BatchArchiveEmailsToolHandler,
                "list_archived_emails": ListArchivedEmailsToolHandler,
                "restore_email_to_inbox": RestoreEmailToInboxToolHandler,
                "delete_label": DeleteLabelToolHandler,
            }
            
            if name in tool_handlers:
                handler_class = tool_handlers[name]
                handler = handler_class()
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
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )