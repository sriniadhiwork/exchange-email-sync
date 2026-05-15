"""Gmail OAuth authentication and email operations."""

import base64
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TOKEN_FILE = "google_token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_credentials(client_id: str, client_secret: str) -> Credentials:
    """Get Gmail credentials, prompting for login if needed."""
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Create OAuth flow from client credentials
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }

            print("Opening browser for Google login...")
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=8401)

        # Save token for next run
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def get_gmail_service(client_id: str, client_secret: str):
    """Get authenticated Gmail API service."""
    creds = get_gmail_credentials(client_id, client_secret)
    return build("gmail", "v1", credentials=creds)


def insert_email(service, raw_mime: bytes) -> str:
    """Insert an email into Gmail inbox as unread, preserving headers and timestamps.

    Uses 'import' endpoint which preserves original dates and headers.
    Returns the Gmail message ID.
    """
    # Base64 URL-safe encode the MIME content
    encoded = base64.urlsafe_b64encode(raw_mime).decode("utf-8")

    message = service.users().messages().import_(
        userId="me",
        body={
            "raw": encoded,
            "labelIds": ["INBOX", "UNREAD"],
        },
        neverMarkSpam=True,  # Don't filter as spam
    ).execute()

    return message["id"]
