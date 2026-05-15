#!/usr/bin/env python3
"""
Exchange to Gmail Sync

Syncs unread emails from Microsoft Outlook/Exchange to Gmail.
Emails are marked as read in Outlook after successful copy.
All headers and timestamps are preserved.
"""

import os
import sys
from dotenv import load_dotenv

from microsoft_auth import get_access_token, get_unread_emails, get_email_mime, mark_as_read
from gmail_auth import get_gmail_service, insert_email


def main():
    load_dotenv()

    # Load credentials from environment
    ms_client_id = os.getenv("MICROSOFT_CLIENT_ID")
    ms_client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not all([ms_client_id, ms_client_secret, google_client_id, google_client_secret]):
        print("Error: Missing credentials. Copy .env.example to .env and fill in your values.")
        sys.exit(1)

    # Authenticate with both services
    print("Authenticating with Microsoft...")
    ms_token = get_access_token(ms_client_id, ms_client_secret)
    print("✓ Microsoft authenticated")

    print("Authenticating with Gmail...")
    gmail_service = get_gmail_service(google_client_id, google_client_secret)
    print("✓ Gmail authenticated")

    # Fetch unread emails from Outlook
    print("\nFetching unread emails from Outlook...")
    unread_emails = get_unread_emails(ms_token)

    if not unread_emails:
        print("No unread emails to sync.")
        return

    print(f"Found {len(unread_emails)} unread email(s)")

    # Process each email
    synced = 0
    failed = 0

    for email in unread_emails:
        msg_id = email["id"]
        subject = email.get("subject", "(no subject)")

        try:
            # Get raw MIME content (preserves all headers)
            print(f"  Syncing: {subject[:50]}...")
            raw_mime = get_email_mime(ms_token, msg_id)

            # Insert into Gmail
            gmail_id = insert_email(gmail_service, raw_mime)

            # Mark as read in Outlook
            mark_as_read(ms_token, msg_id)

            print(f"    ✓ Synced (Gmail ID: {gmail_id})")
            synced += 1

        except Exception as e:
            print(f"    ✗ Failed: {e}")
            failed += 1

    # Summary
    print(f"\nSync complete: {synced} synced, {failed} failed")


if __name__ == "__main__":
    main()
