"""MCP Google Calendar Tools Module"""

from collections.abc import Sequence
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
from . import gauth
from . import calendar
import json
from . import toolhandler

CALENDAR_ID_ARG="__calendar_id__"

def get_calendar_id_arg_schema() -> dict[str, str]:
    return {
        "type": "string",
        "description": """Optional ID of the specific agenda for which you are executing this action.
                          If not provided, the default calendar is being used. 
                          If not known, the specific calendar id can be retrieved with the list_calendars tool""",
        "default": "primary"
    }

def process_attendees(attendees):
    """
    Helper function to process attendees parameter.
    Converts string to list if needed.
    """
    if attendees is None:
        return []
    if isinstance(attendees, str):
        # Split comma-separated string into list of email addresses
        return [email.strip() for email in attendees.split(',') if email.strip()]
    return attendees

class ListCalendarsToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("list_calendars")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Lists all calendars accessible by the user. 
            Call it before any other tool whenever the user specifies a particular agenda (Family, Holidays, etc.).""",
            inputSchema={
                "type": "object",
                "properties": {
                    "__user_id__": self.get_user_id_arg_schema(),
                },
                "required": [toolhandler.USER_ID_ARG]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        user_id = args.get(toolhandler.USER_ID_ARG)
        if not user_id:
            raise RuntimeError(f"Missing required argument: {toolhandler.USER_ID_ARG}")

        calendar_service = calendar.CalendarService(user_id=user_id)
        calendars = calendar_service.list_calendars()

        return [
            TextContent(
                type="text",
                text=json.dumps(calendars, indent=2)
            )
        ]

class GetCalendarEventsToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("get_calendar_events")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Retrieves calendar events from the user's Google Calendar within a specified time range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "__user_id__": self.get_user_id_arg_schema(),
                    "__calendar_id__": get_calendar_id_arg_schema(),
                    "time_min": {
                        "type": "string",
                        "description": "Start time in RFC3339 format (e.g. 2024-12-01T00:00:00Z). Defaults to current time if not specified."
                    },
                    "time_max": {
                        "type": "string", 
                        "description": "End time in RFC3339 format (e.g. 2024-12-31T23:59:59Z). Optional."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return (1-2500)",
                        "minimum": 1,
                        "maximum": 2500,
                        "default": 250
                    },
                    "show_deleted": {
                        "type": "boolean",
                        "description": "Whether to include deleted events",
                        "default": False
                    }
                },
                "required": [toolhandler.USER_ID_ARG]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        
        user_id = args.get(toolhandler.USER_ID_ARG)
        if not user_id:
            raise RuntimeError(f"Missing required argument: {toolhandler.USER_ID_ARG}")
        
        calendar_service = calendar.CalendarService(user_id=user_id)
        events = calendar_service.get_events(
            time_min=args.get('time_min'),
            time_max=args.get('time_max'),
            max_results=args.get('max_results', 250),
            show_deleted=args.get('show_deleted', False),
            calendar_id=args.get(CALENDAR_ID_ARG, 'primary'),
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(events, indent=2)
            )
        ]

class CreateCalendarEventToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("create_calendar_event")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Creates a new event in a specified Google Calendar of the specified user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "__user_id__": self.get_user_id_arg_schema(),
                    "__calendar_id__": get_calendar_id_arg_schema(),
                    "summary": {
                        "type": "string",
                        "description": "Title of the event"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location of the event (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description or notes for the event (optional)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in RFC3339 format (e.g. 2024-12-01T10:00:00Z)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in RFC3339 format (e.g. 2024-12-01T11:00:00Z)"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of attendee email addresses (optional)"
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
                "required": [toolhandler.USER_ID_ARG, "summary", "start_time", "end_time"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # Validate required arguments
        required = ["summary", "start_time", "end_time"]
        if not all(key in args for key in required):
            raise RuntimeError(f"Missing required arguments: {', '.join(required)}")

        user_id = args.get(toolhandler.USER_ID_ARG)
        if not user_id:
            raise RuntimeError(f"Missing required argument: {toolhandler.USER_ID_ARG}")

        # Use the server calendar_id if available, otherwise fall back to legacy format
        calendar_id_from_legacy = args.get(CALENDAR_ID_ARG, 'primary')
        calendar_id_from_server = args.get('calendar_id')
        final_calendar_id = calendar_id_from_server or calendar_id_from_legacy

        calendar_service = calendar.CalendarService(user_id=user_id)
        
        # Process attendees using helper function
        attendees = process_attendees(args.get("attendees"))
        
        event = calendar_service.create_event(
            summary=args["summary"],
            start_time=args["start_time"],
            end_time=args["end_time"],
            location=args.get("location"),
            description=args.get("description"),
            attendees=attendees,
            send_notifications=args.get("send_notifications", True),
            timezone=args.get("timezone"),
            calendar_id=final_calendar_id,
            create_meet_link=args.get("create_meet_link", True),
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(event, indent=2)
            )
        ]
    
class DeleteCalendarEventToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("delete_calendar_event")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Deletes an event from the user's Google Calendar by its event ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "__user_id__": self.get_user_id_arg_schema(),
                    "__calendar_id__": get_calendar_id_arg_schema(),
                    "event_id": {
                        "type": "string",
                        "description": "The ID of the calendar event to delete"
                    },
                    "send_notifications": {
                        "type": "boolean",
                        "description": "Whether to send cancellation notifications to attendees",
                        "default": True
                    }
                },
                "required": [toolhandler.USER_ID_ARG, "event_id"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if "event_id" not in args:
            raise RuntimeError("Missing required argument: event_id")
        
        user_id = args.get(toolhandler.USER_ID_ARG)
        if not user_id:
            raise RuntimeError(f"Missing required argument: {toolhandler.USER_ID_ARG}")

        calendar_service = calendar.CalendarService(user_id=user_id)
        success = calendar_service.delete_event(
            event_id=args["event_id"],
            send_notifications=args.get("send_notifications", True),
            calendar_id=args.get(CALENDAR_ID_ARG, 'primary'),
        )

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "success": success,
                    "message": "Event successfully deleted" if success else "Failed to delete event"
                }, indent=2)
            )
        ]

class UpdateCalendarEventToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("update_calendar_event")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Updates an existing event in the user's Google Calendar.",
            inputSchema={
                "type": "object",
                "properties": {
                    "__user_id__": self.get_user_id_arg_schema(),
                    "__calendar_id__": get_calendar_id_arg_schema(),
                    "event_id": {
                        "type": "string",
                        "description": "The ID of the calendar event to update"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Title of the event (optional)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location of the event (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description or notes for the event (optional)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in RFC3339 format (e.g. 2024-12-01T10:00:00Z) (optional)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in RFC3339 format (e.g. 2024-12-01T11:00:00Z) (optional)"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of attendee email addresses (optional)"
                    },
                    "send_notifications": {
                        "type": "boolean",
                        "description": "Whether to send notifications to attendees",
                        "default": True
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone for the event (e.g. 'America/New_York') (optional)"
                    },
                    "create_meet_link": {
                        "type": "boolean",
                        "description": "Whether to create a Google Meet link for the event (only if not already present)",
                        "default": False
                    }
                },
                "required": [toolhandler.USER_ID_ARG, "event_id"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if "event_id" not in args:
            raise RuntimeError("Missing required argument: event_id")
        
        user_id = args.get(toolhandler.USER_ID_ARG)
        if not user_id:
            raise RuntimeError(f"Missing required argument: {toolhandler.USER_ID_ARG}")

        # Use the server calendar_id if available, otherwise fall back to legacy format
        calendar_id_from_legacy = args.get(CALENDAR_ID_ARG, 'primary')
        calendar_id_from_server = args.get('calendar_id')
        final_calendar_id = calendar_id_from_server or calendar_id_from_legacy

        calendar_service = calendar.CalendarService(user_id=user_id)
        
        # Prepare update arguments, only including non-None values
        update_kwargs = {
            'event_id': args["event_id"],
            'send_notifications': args.get("send_notifications", True),
            'calendar_id': final_calendar_id,
            'create_meet_link': args.get("create_meet_link", False)
        }
        
        # Add optional fields only if they're provided
        if "summary" in args:
            update_kwargs["summary"] = args["summary"]
        if "location" in args:
            update_kwargs["location"] = args["location"]
        if "description" in args:
            update_kwargs["description"] = args["description"]
        if "start_time" in args:
            update_kwargs["start_time"] = args["start_time"]
        if "end_time" in args:
            update_kwargs["end_time"] = args["end_time"]
        if "attendees" in args:
            update_kwargs["attendees"] = process_attendees(args["attendees"])
        if "timezone" in args:
            update_kwargs["timezone"] = args["timezone"]
        
        updated_event = calendar_service.update_event(**update_kwargs)

        return [
            TextContent(
                type="text",
                text=json.dumps(updated_event, indent=2)
            )
        ]