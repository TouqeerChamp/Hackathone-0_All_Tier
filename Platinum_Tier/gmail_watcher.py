import os
import pickle
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Scopes required for reading Gmail, creating drafts, and modifying messages
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Configuration from environment
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.pickle")

def authenticate_gmail():
    """
    Authenticate and return Gmail service object
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This is where you'll place your credentials.json file
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_latest_unread_emails(max_results=10):
    """
    Fetch the latest unread emails from Gmail

    Args:
        max_results (int): Maximum number of emails to fetch

    Returns:
        list: List of email message objects
    """
    try:
        service = authenticate_gmail()

        # Search for unread emails
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        emails = []
        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id']
            ).execute()
            emails.append(msg)

        return emails

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def save_emails_to_inbox(emails):
    """
    Save email content to files in the /inbox folder

    Args:
        emails (list): List of email message objects
    """
    inbox_dir = 'inbox'
    if not os.path.exists(inbox_dir):
        os.makedirs(inbox_dir)

    for i, email in enumerate(emails):
        # Extract email ID to create unique filename
        email_id = email['id']
        filename = f'{inbox_dir}/email_{email_id}.json'

        # Save email as JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(email, f, indent=2, ensure_ascii=False)

        print(f'Saved email to {filename}')

def mark_as_read(email_id):
    """
    Mark an email as read after processing

    Args:
        email_id (str): The ID of the email to mark as read
    """
    try:
        service = authenticate_gmail()
        # Modify the message to remove the UNREAD label
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
    except HttpError as error:
        print(f'An error occurred while marking email as read: {error}')

def create_draft(service, original_email_data, reply_text):
    """
    Create a draft reply for a specific message ID using the Gmail API

    Args:
        service: Gmail API service object
        original_email_data (dict): Original email data containing the message details
        reply_text (str): The text content of the reply

    Returns:
        dict: The created draft object or None if failed
    """
    try:
        # Extract original message ID
        original_message_id = original_email_data['id']

        # Get the original message to extract sender, subject, etc.
        original_message = service.users().messages().get(
            userId='me',
            id=original_message_id
        ).execute()

        # Extract headers from the original email
        headers = original_message['payload'].get('headers', [])
        from_header = None
        subject_header = None

        for header in headers:
            if header['name'].lower() == 'from':
                from_header = header['value']
            elif header['name'].lower() == 'subject':
                subject_header = header['value']

        # Create the reply subject (prefix with "Re:" if not already present)
        if subject_header and not subject_header.lower().startswith('re:'):
            reply_subject = f"Re: {subject_header}"
        else:
            reply_subject = subject_header

        # Format the reply body with the original message quoted
        reply_body = f"{reply_text}\n\n\n---------- Original Message ---------\n"
        if from_header:
            reply_body += f"From: {from_header}\n"
        if subject_header:
            reply_body += f"Subject: {subject_header}\n"

        # Extract the original message body content
        original_body = extract_message_body(original_message)
        if original_body:
            reply_body += f"\n{original_body[:500]}\n"  # Limit to first 500 chars to avoid very long quotes

        # Create the draft
        draft = service.users().drafts().create(
            userId='me',
            body={
                'message': {
                    'raw': create_message_with_reply(reply_subject, reply_body)
                }
            }
        ).execute()

        print(f'Draft created successfully with ID: {draft["id"]}')
        return draft

    except HttpError as error:
        print(f'An error occurred while creating draft: {error}')
        return None


def extract_message_body(message):
    """
    Extract the text body from a Gmail message, handling both simple and multipart messages.

    Args:
        message (dict): Gmail message object

    Returns:
        str: The text content of the message body
    """
    import base64

    body_text = ""

    # If the message has a simple body
    if 'payload' in message and 'body' in message['payload']:
        body = message['payload']['body']
        if 'data' in body:
            # Decode the body data
            decoded_data = base64.urlsafe_b64decode(body['data'].encode('ASCII')).decode('utf-8')
            return decoded_data

    # If the message has parts (multipart)
    if 'payload' in message and 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                if 'body' in part and 'data' in part['body']:
                    try:
                        decoded_data = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
                        body_text += decoded_data
                    except:
                        continue

    return body_text


def create_message_with_reply(subject, body, to_email=None):
    """
    Create a raw message string for the draft, properly encoded for Gmail API.

    Args:
        subject (str): The subject of the message
        body (str): The body of the message
        to_email (str): The recipient email (optional)

    Returns:
        str: Base64url encoded raw message string
    """
    import base64
    import email.mime.text
    import email.mime.multipart

    # Create a MIME text object
    msg = email.mime.text.MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject

    if to_email:
        msg['To'] = to_email

    # Convert to string and properly encode for Gmail API
    raw_message = msg.as_string()
    raw_bytes = raw_message.encode('utf-8')
    raw_message_b64 = base64.urlsafe_b64encode(raw_bytes).decode('utf-8')

    return raw_message_b64

def main():
    """
    Main function to fetch and save unread emails
    """
    print('Fetching unread emails...')

    # Fetch the latest unread emails
    emails = fetch_latest_unread_emails(max_results=10)

    if emails:
        print(f'Found {len(emails)} unread email(s)')

        # Save emails to inbox folder
        save_emails_to_inbox(emails)

        # Optionally mark emails as read after saving
        for email in emails:
            mark_as_read(email['id'])

        print('Emails processed and saved to inbox folder.')
    else:
        print('No unread emails found.')

if __name__ == '__main__':
    main()