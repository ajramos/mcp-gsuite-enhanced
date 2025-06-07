# Changelog

All notable changes to mcp-gsuite-enhanced will be documented in this file.

## [2.0.0] - 2025-06-07

### 🚀 Major Release: Complete Gmail API Coverage

This major release transforms MCP GSuite Enhanced into a comprehensive Google Workspace automation platform with **complete Gmail API coverage**.

#### 📊 Summary
- **27 total tools** (vs 13 in v1.0.1)
- **5 Calendar tools** (unchanged)
- **22 Gmail tools** (+14 new Gmail tools)

#### ✨ New Gmail Tools Added (14)

**📧 Email Management**
- `send_email` - Send emails directly via Gmail
- `list_drafts` - List Gmail drafts with full details  
- `get_unread_emails` - Retrieve unread emails with filtering
- `mark_email_read` - Mark emails as read
- `trash_email` - Move emails to trash

**🏷️ Label Management**
- `list_labels` - List all Gmail labels (system + user)
- `create_label` - Create new custom labels
- `apply_label` - Apply labels to emails
- `remove_label` - Remove labels from emails
- `delete_label` - Delete custom labels permanently

**📁 Archive Management** 
- `archive_email` - Archive individual emails
- `batch_archive_emails` - Archive multiple emails at once
- `list_archived_emails` - List archived emails
- `restore_email_to_inbox` - Restore archived emails to inbox

#### 🔧 Technical Improvements
- ✅ Complete Gmail API functionality coverage
- ✅ Consistent tool naming conventions (removed redundant prefixes)
- ✅ Enhanced error handling and logging
- ✅ Optimized performance for bulk operations
- ✅ Backward compatibility maintained

#### 🧪 Verification
- All 14 new tools thoroughly tested and verified
- Email lifecycle workflows validated
- Label management operations confirmed
- Archive/restore functionality working
- Bulk operations performance optimized

---

## [1.0.0] - 2025-06-06

### 🎯 Enhanced Features
This is the first release of the enhanced version, based on mcp-gsuite v0.4.1 by Markus Pfundstein.

### ✅ Added
- **Google Meet Integration**: Automatic Google Meet link creation for calendar events
- **Fixed `update_calendar_event`**: Previously broken functionality now works correctly
- **Enhanced attendee processing**: Fixed email parsing bugs with `process_attendees()` helper function
- **Setup utilities**: Added `auth_setup.py` and `cursor_setup.py` for easier configuration
- **Comprehensive documentation**: Updated README with detailed setup instructions
- **Better error handling**: Improved calendar operations with robust exception handling

### 🔧 Fixed
- **Critical bug**: Fixed attendees parameter processing (was iterating over characters instead of emails)
- **Parameter types**: Changed attendees from array to string type in MCP server definition
- **Dependency issues**: Updated to latest stable versions of all dependencies

### 📦 Updated Dependencies
- `google-api-python-client`: Updated from 2.154.0 to 2.171.0 (17 versions newer)
- `mcp`: Updated from 1.3.0 to 1.9.3
- Removed unnecessary dependencies (`beautifulsoup4`, `httplib2`, `python-dotenv`, `pytz`, `requests`)

### 🧹 Cleanup
- Removed unused API specification files (213KB total):
  - `gmail.v1.json`
  - `gmail-api-openapi-spec.yaml` 
  - `google-calendar-api-openapi-spec.yaml`
- Cleaned up test files and temporary scripts
- Refactored code to eliminate duplication

### 🎪 Google Meet Features
- Automatic Meet link generation for new events
- Phone dial-in numbers included
- Meeting PIN provided
- Full integration with Google Calendar API

### 💡 Developer Experience
- Simplified Python version requirement (>=3.10 instead of >=3.13)
- Added development dependencies for better code quality
- Enhanced project metadata and URLs
- Improved command-line interface

### 🏆 Credits
Based on the excellent work by Markus Pfundstein on the original mcp-gsuite project.
Enhanced by Angel Ramos with focus on Google Meet integration and bug fixes.

---

## Original Project
For the history of the original project, see: https://github.com/MarkusPfundstein/mcp-gsuite 