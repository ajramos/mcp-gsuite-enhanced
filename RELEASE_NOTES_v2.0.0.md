# 🚀 MCP GSuite Enhanced v2.0.0 Release Notes

**Release Date**: June 7, 2025

## 🎉 Major Release: Complete Gmail API Coverage

This is a major release that transforms MCP GSuite Enhanced from a basic Gmail/Calendar integration to a **comprehensive Google Workspace automation platform** with complete Gmail API coverage.

## 📊 What's New

### 🎯 **27 Total Tools** (vs 13 in v1.0.1)
- **5 Calendar tools** (unchanged)
- **22 Gmail tools** (+14 new tools)

### ✨ **14 New Gmail Tools Added**

#### 📧 **Email Management**
- `send_email` - Send emails directly via Gmail
- `list_drafts` - List Gmail drafts with full details
- `get_unread_emails` - Retrieve unread emails with filtering
- `mark_email_read` - Mark emails as read
- `trash_email` - Move emails to trash

#### 🏷️ **Label Management** 
- `list_labels` - List all Gmail labels (system + user)
- `create_label` - Create new custom labels
- `apply_label` - Apply labels to emails
- `remove_label` - Remove labels from emails  
- `delete_label` - Delete custom labels permanently

#### 📁 **Archive Management**
- `archive_email` - Archive individual emails
- `batch_archive_emails` - Archive multiple emails at once
- `list_archived_emails` - List archived emails
- `restore_email_to_inbox` - Restore archived emails to inbox

## 🔧 **Technical Improvements**

### **Comprehensive API Coverage**
- ✅ Complete Gmail API functionality coverage
- ✅ All major Gmail operations supported
- ✅ Consistent error handling across all tools
- ✅ Optimized performance for bulk operations

### **Enhanced Architecture**
- ✅ Consistent tool naming conventions (removed redundant prefixes)
- ✅ Improved handler class structure
- ✅ Better separation of concerns
- ✅ Enhanced logging and error reporting

## 📋 **Upgrade Guide**

### **Breaking Changes**: None
- All existing v1.0.1 tools maintain backward compatibility
- Tool names remain the same for existing functionality
- No changes to existing API contracts

### **New Capabilities**
- Email lifecycle management (send → read → archive → restore)
- Complete label management workflow  
- Bulk operations for efficiency
- Advanced email filtering and search

## 🧪 **Verification & Testing**

All new tools have been thoroughly tested:
- ✅ Email sending functionality verified
- ✅ Label creation, application, and deletion tested
- ✅ Archive/restore workflows validated
- ✅ Bulk operations performance confirmed
- ✅ Error handling scenarios tested

## 📚 **Usage Examples**

### **Email Workflow**
```python
# Send an email
send_email(to="user@example.com", subject="Hello", body="Test message")

# Mark as read when received
mark_email_read(email_id="abc123")

# Apply label for organization
create_label(name="Important")
apply_label(email_id="abc123", label_id="Label_1")

# Archive when done
archive_email(email_id="abc123")
```

### **Label Management**
```python
# Create organizational labels
create_label(name="Project Alpha")
create_label(name="Urgent")

# Apply to emails
apply_label(email_id="email1", label_id="Label_1") 
apply_label(email_id="email2", label_id="Label_2")

# Remove when not needed
remove_label(email_id="email1", label_id="Label_1")
delete_label(label_id="Label_1")
```

### **Bulk Operations**
```python
# Archive multiple emails at once
batch_archive_emails(email_ids=["email1", "email2", "email3"])

# List and manage drafts
drafts = list_drafts(max_results=50)
unread = get_unread_emails(max_results=100)
```

## 🎯 **What's Next**

v2.0.0 represents the completion of core Gmail functionality. Future releases may include:
- Advanced Calendar features
- Integration with other Google Workspace services
- Automation workflows and templates
- Performance optimizations

## 🙏 **Acknowledgments**

This release builds upon the solid foundation established in v1.0.0 and incorporates comprehensive Gmail API coverage inspired by the Gmail MCP Server reference implementation.

---

**Full changelog**: [CHANGELOG.md](CHANGELOG.md)  
**Installation**: `pip install mcp-gsuite-enhanced==2.0.0`  
**Documentation**: [README.md](README.md) 