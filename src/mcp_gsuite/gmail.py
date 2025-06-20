from googleapiclient.discovery import build 
from . import gauth
import logging
import base64
import traceback
from email.mime.text import MIMEText
from email.message import EmailMessage
from typing import Tuple


class GmailService():
    def __init__(self, user_id: str):
        credentials = gauth.get_stored_credentials(user_id=user_id)
        if not credentials:
            raise RuntimeError("No Oauth2 credentials stored")
        self.service = build('gmail', 'v1', credentials=credentials)

    def _parse_message(self, txt, parse_body=False) -> dict | None:
        """
        Parse a Gmail message into a structured format.
        
        Args:
            txt (dict): Raw message from Gmail API
            parse_body (bool): Whether to parse and include the message body (default: False)
        
        Returns:
            dict: Parsed message containing comprehensive metadata
            None: If parsing fails
        """
        try:
            message_id = txt.get('id')
            thread_id = txt.get('threadId')
            payload = txt.get('payload', {})
            headers = payload.get('headers', [])

            metadata = {
                'id': message_id,
                'threadId': thread_id,
                'historyId': txt.get('historyId'),
                'internalDate': txt.get('internalDate'),
                'sizeEstimate': txt.get('sizeEstimate'),
                'labelIds': txt.get('labelIds', []),
                'snippet': txt.get('snippet'),
            }

            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                
                if name == 'subject':
                    metadata['subject'] = value
                elif name == 'from':
                    metadata['from'] = value
                elif name == 'to':
                    metadata['to'] = value
                elif name == 'date':
                    metadata['date'] = value
                elif name == 'cc':
                    metadata['cc'] = value
                elif name == 'bcc':
                    metadata['bcc'] = value
                elif name == 'message-id':
                    metadata['message_id'] = value
                elif name == 'in-reply-to':
                    metadata['in_reply_to'] = value
                elif name == 'references':
                    metadata['references'] = value
                elif name == 'delivered-to':
                    metadata['delivered_to'] = value

            if parse_body:
                body = self._extract_body(payload)
                if body:
                    metadata['body'] = body

                metadata['mimeType'] = payload.get('mimeType')

            return metadata

        except Exception as e:
            logging.error(f"Error parsing message: {str(e)}")
            logging.error(traceback.format_exc())
            return None

    def _extract_body(self, payload) -> str | None:
        """
        Extract the email body from the payload.
        Handles both multipart and single part messages, including nested multiparts.
        """
        try:
            # For single part text/plain messages
            if payload.get('mimeType') == 'text/plain':
                data = payload.get('body', {}).get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            # For single part text/html messages
            if payload.get('mimeType') == 'text/html':
                data = payload.get('body', {}).get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            # For multipart messages (both alternative and related)
            if payload.get('mimeType', '').startswith('multipart/'):
                parts = payload.get('parts', [])
                
                # First try to find a direct text/plain part
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                
                # If no direct text/plain, recursively check nested multipart structures
                for part in parts:
                    if part.get('mimeType', '').startswith('multipart/'):
                        nested_body = self._extract_body(part)
                        if nested_body:
                            return nested_body
                            
                # If still no body found, try the first part as fallback
                if parts and 'body' in parts[0] and 'data' in parts[0]['body']:
                    data = parts[0]['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8')

            return None

        except Exception as e:
            logging.error(f"Error extracting body: {str(e)}")
            return None

    def query_emails(self, query=None, max_results=100):
        """
        Query emails from Gmail based on a search query.
        
        Args:
            query (str, optional): Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
                                If None, returns all emails
            max_results (int): Maximum number of emails to retrieve (1-500, default: 100)
        
        Returns:
            list: List of parsed email messages, newest first
        """
        try:
            # Ensure max_results is within API limits
            max_results = min(max(1, max_results), 500)
            
            # Get the list of messages
            result = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query if query else ''
            ).execute()

            messages = result.get('messages', [])
            parsed = []

            # Fetch full message details for each message
            for msg in messages:
                txt = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id']
                ).execute()
                parsed_message = self._parse_message(txt=txt, parse_body=False)
                if parsed_message:
                    parsed.append(parsed_message)
                    
            return parsed
            
        except Exception as e:
            logging.error(f"Error reading emails: {str(e)}")
            logging.error(traceback.format_exc())
            return []
        
    def get_email_by_id_with_attachments(self, email_id: str) -> Tuple[dict, dict] | Tuple[None, dict]:
        """
        Fetch and parse a complete email message by its ID including attachment IDs.
        
        Args:
            email_id (str): The Gmail message ID to retrieve
        
        Returns:
            Tuple[dict, list]: Complete parsed email message including body and list of attachment IDs
            Tuple[None, list]: If retrieval or parsing fails, returns None for email and empty list for attachment IDs
        """
        try:
            # Fetch the complete message by ID
            message = self.service.users().messages().get(
                userId='me',
                id=email_id
            ).execute()
            
            # Parse the message with body included
            parsed_email = self._parse_message(txt=message, parse_body=True)

            if parsed_email is None:
                return None, {}

            attachments = {}
            # Check if 'parts' exists in payload before trying to access it
            if "payload" in message and "parts" in message["payload"]:
                for part in message["payload"]["parts"]:
                    if "body" in part and "attachmentId" in part["body"]:
                        attachment_id = part["body"]["attachmentId"]
                        part_id = part["partId"]
                        attachment = {
                            "filename": part["filename"],
                            "mimeType": part["mimeType"],
                            "attachmentId": attachment_id,
                            "partId": part_id
                        }
                        attachments[part_id] = attachment
            else:
                # Handle case when there are no parts (single part message)
                logging.info(f"Email {email_id} does not have 'parts' in payload (likely single part message)")
                if "payload" in message and "body" in message["payload"] and "attachmentId" in message["payload"]["body"]:
                    # Handle potential attachment in single part message
                    attachment_id = message["payload"]["body"]["attachmentId"]
                    attachment = {
                        "filename": message["payload"].get("filename", "attachment"),
                        "mimeType": message["payload"].get("mimeType", "application/octet-stream"),
                        "attachmentId": attachment_id,
                        "partId": "0"
                    }
                    attachments["0"] = attachment

            return parsed_email, attachments
            
        except Exception as e:
            logging.error(f"Error retrieving email {email_id}: {str(e)}")
            logging.error(traceback.format_exc())
            return None, {}
        
    def create_draft(self, to: str, subject: str, body: str, cc: list[str] | None = None) -> dict | None:
        """
        Create a draft email message.
        
        Args:
            to (str): Email address of the recipient
            subject (str): Subject line of the email
            body (str): Body content of the email
            cc (list[str], optional): List of email addresses to CC
            
        Returns:
            dict: Draft message data including the draft ID if successful
            None: If creation fails
        """
        try:
            # Create message body
            message = {
                'to': to,
                'subject': subject,
                'text': body,
            }
            if cc:
                message['cc'] = ','.join(cc)
                
            # Create the message in MIME format
            mime_message = MIMEText(body)
            mime_message['to'] = to
            mime_message['subject'] = subject
            if cc:
                mime_message['cc'] = ','.join(cc)
                
            # Encode the message
            raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode('utf-8')
            
            # Create the draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={
                    'message': {
                        'raw': raw_message
                    }
                }
            ).execute()
            
            return draft
            
        except Exception as e:
            logging.error(f"Error creating draft: {str(e)}")
            logging.error(traceback.format_exc())
            return None
        
    def delete_draft(self, draft_id: str) -> bool:
        """
        Delete a draft email message.
        
        Args:
            draft_id (str): The ID of the draft to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.service.users().drafts().delete(
                userId='me',
                id=draft_id
            ).execute()
            return True
            
        except Exception as e:
            logging.error(f"Error deleting draft {draft_id}: {str(e)}")
            logging.error(traceback.format_exc())
            return False
        
    def create_reply(self, original_message: dict, reply_body: str, send: bool = False, cc: list[str] | None = None) -> dict | None:
        """
        Create a reply to an email message and either send it or save as draft.
        
        Args:
            original_message (dict): The original message data (as returned by get_email_by_id)
            reply_body (str): Body content of the reply
            send (bool): If True, sends the reply immediately. If False, saves as draft.
            cc (list[str], optional): List of email addresses to CC
            
        Returns:
            dict: Sent message or draft data if successful
            None: If operation fails
        """
        try:
            to_address = original_message.get('from')
            if not to_address:
                raise ValueError("Could not determine original sender's address")
            
            subject = original_message.get('subject', '')
            if not subject.lower().startswith('re:'):
                subject = f"Re: {subject}"


            original_date = original_message.get('date', '')
            original_from = original_message.get('from', '')
            original_body = original_message.get('body', '')
        
            full_reply_body = (
                f"{reply_body}\n\n"
                f"On {original_date}, {original_from} wrote:\n"
                f"> {original_body.replace('\n', '\n> ') if original_body else '[No message body]'}"
            )

            mime_message = MIMEText(full_reply_body)
            mime_message['to'] = to_address
            mime_message['subject'] = subject
            if cc:
                mime_message['cc'] = ','.join(cc)
                
            mime_message['In-Reply-To'] = original_message.get('id', '')
            mime_message['References'] = original_message.get('id', '')
            
            raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode('utf-8')
            
            message_body = {
                'raw': raw_message,
                'threadId': original_message.get('threadId')  # Ensure it's added to the same thread
            }

            if send:
                # Send the reply immediately
                result = self.service.users().messages().send(
                    userId='me',
                    body=message_body
                ).execute()
            else:
                # Save as draft
                result = self.service.users().drafts().create(
                    userId='me',
                    body={
                        'message': message_body
                    }
                ).execute()
            
            return result
            
        except Exception as e:
            logging.error(f"Error {'sending' if send else 'drafting'} reply: {str(e)}")
            logging.error(traceback.format_exc())
            return None
        
    def get_attachment(self, message_id: str, attachment_id: str) -> dict | None:
        """
        Retrieves a Gmail attachment by its ID.
        
        Args:
            message_id (str): The ID of the Gmail message containing the attachment
            attachment_id (str): The ID of the attachment to retrieve
        
        Returns:
            dict: Attachment data including filename and base64-encoded content
            None: If retrieval fails
        """
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id, 
                id=attachment_id
            ).execute()
            return {
                "size": attachment.get("size"),
                "data": attachment.get("data")
            }
            
        except Exception as e:
            logging.error(f"Error retrieving attachment {attachment_id} from message {message_id}: {str(e)}")
            logging.error(traceback.format_exc())
            return None

    def send_email(self, to: str, subject: str, body: str, cc: str = None, bcc: str = None) -> dict:
        """Send an email message directly through Gmail"""
        try:
            message = EmailMessage()
            message["To"] = to
            message["Subject"] = subject
            message.set_content(body)
            
            if cc:
                message["Cc"] = cc
            if bcc:
                message["Bcc"] = bcc

            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            send_message = self.service.users().messages().send(
                userId="me", 
                body=create_message
            ).execute()
            
            return {
                "status": "success", 
                "message_id": send_message['id'],
                "to": to,
                "subject": subject
            }
            
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return {"status": "error", "error_message": str(e)}

    def list_drafts(self, max_results: int = 50) -> list:
        """List all draft emails in Gmail"""
        try:
            result = self.service.users().drafts().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            drafts = result.get('drafts', [])
            parsed_drafts = []
            
            for draft in drafts:
                try:
                    draft_detail = self.service.users().drafts().get(
                        userId='me',
                        id=draft['id']
                    ).execute()
                    
                    message = draft_detail.get('message', {})
                    parsed_draft = self._parse_message(txt=message, parse_body=True)
                    if parsed_draft:
                        parsed_draft['draft_id'] = draft['id']
                        parsed_drafts.append(parsed_draft)
                        
                except Exception as e:
                    logging.error(f"Error parsing draft {draft['id']}: {str(e)}")
                    continue
                    
            return parsed_drafts
            
        except Exception as e:
            logging.error(f"Error listing drafts: {str(e)}")
            return []

    def get_unread_emails(self, max_results: int = 100) -> list:
        """Get all unread emails from Gmail"""
        try:
            result = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            parsed = []
            
            for msg in messages:
                try:
                    txt = self.service.users().messages().get(
                        userId='me', 
                        id=msg['id']
                    ).execute()
                    parsed_message = self._parse_message(txt=txt, parse_body=True)
                    if parsed_message:
                        parsed.append(parsed_message)
                except Exception as e:
                    logging.error(f"Error parsing unread email {msg['id']}: {str(e)}")
                    continue
                    
            return parsed
            
        except Exception as e:
            logging.error(f"Error getting unread emails: {str(e)}")
            return []

    def mark_email_read(self, email_id: str) -> bool:
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logging.error(f"Error marking email {email_id} as read: {str(e)}")
            return False

    def trash_email(self, email_id: str) -> bool:
        """Move an email to trash"""
        try:
            self.service.users().messages().trash(
                userId='me',
                id=email_id
            ).execute()
            return True
        except Exception as e:
            logging.error(f"Error moving email {email_id} to trash: {str(e)}")
            return False

    def list_labels(self) -> list:
        """List all Gmail labels"""
        try:
            result = self.service.users().labels().list(userId='me').execute()
            labels = result.get('labels', [])
            return [{'id': label['id'], 'name': label['name'], 'type': label.get('type', 'user')} for label in labels]
        except Exception as e:
            logging.error(f"Error listing labels: {str(e)}")
            return []

    def create_label(self, name: str, visibility: str = 'labelShow') -> dict:
        """Create a new Gmail label"""
        try:
            label = {
                'name': name,
                'labelListVisibility': visibility,
                'messageListVisibility': 'show'
            }
            result = self.service.users().labels().create(
                userId='me',
                body=label
            ).execute()
            return {'status': 'success', 'label_id': result['id'], 'name': result['name']}
        except Exception as e:
            logging.error(f"Error creating label '{name}': {str(e)}")
            return {'status': 'error', 'error_message': str(e)}

    def apply_label(self, email_id: str, label_id: str) -> bool:
        """Apply a label to an email"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return True
        except Exception as e:
            logging.error(f"Error applying label {label_id} to email {email_id}: {str(e)}")
            return False

    def remove_label(self, email_id: str, label_id: str) -> bool:
        """Remove a label from an email"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': [label_id]}
            ).execute()
            return True
        except Exception as e:
            logging.error(f"Error removing label {label_id} from email {email_id}: {str(e)}")
            return False

    def archive_email(self, email_id: str) -> bool:
        """Archive an email (remove from inbox)"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except Exception as e:
            logging.error(f"Error archiving email {email_id}: {str(e)}")
            return False

    def batch_archive_emails(self, email_ids: list[str]) -> dict:
        """Archive multiple emails at once"""
        try:
            success_count = 0
            failed_ids = []
            
            for email_id in email_ids:
                if self.archive_email(email_id):
                    success_count += 1
                else:
                    failed_ids.append(email_id)
            
            return {
                'status': 'completed',
                'total': len(email_ids),
                'success': success_count,
                'failed': len(failed_ids),
                'failed_ids': failed_ids
            }
        except Exception as e:
            logging.error(f"Error in batch archive: {str(e)}")
            return {'status': 'error', 'error_message': str(e)}

    def list_archived_emails(self, max_results: int = 100) -> list:
        """List archived emails (not in inbox but not in trash)"""
        try:
            result = self.service.users().messages().list(
                userId='me',
                q='-in:inbox -in:trash',
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            parsed = []
            
            for msg in messages:
                try:
                    txt = self.service.users().messages().get(
                        userId='me', 
                        id=msg['id']
                    ).execute()
                    parsed_message = self._parse_message(txt=txt, parse_body=True)
                    if parsed_message:
                        parsed.append(parsed_message)
                except Exception as e:
                    logging.error(f"Error parsing archived email {msg['id']}: {str(e)}")
                    continue
                    
            return parsed
            
        except Exception as e:
            logging.error(f"Error getting archived emails: {str(e)}")
            return []

    def restore_email_to_inbox(self, email_id: str) -> bool:
        """Restore an archived email back to inbox"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': ['INBOX']}
            ).execute()
            return True
        except Exception as e:
            logging.error(f"Error restoring email {email_id} to inbox: {str(e)}")
            return False

    def delete_label(self, label_id: str) -> dict:
        """Delete a Gmail label"""
        try:
            self.service.users().labels().delete(
                userId='me',
                id=label_id
            ).execute()
            return {'status': 'success', 'label_id': label_id, 'action': 'deleted'}
        except Exception as e:
            logging.error(f"Error deleting label {label_id}: {str(e)}")
            return {'status': 'error', 'error_message': str(e)}