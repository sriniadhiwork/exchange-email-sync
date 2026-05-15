"""Microsoft OAuth authentication using MSAL with interactive browser login."""

import json
import os
import msal
import requests

TOKEN_CACHE_FILE = "ms_token_cache.json"
SCOPES = ["Mail.ReadWrite"]


def get_token_cache():
    """Load or create MSAL token cache."""
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    return cache


def save_token_cache(cache):
    """Persist token cache to disk."""
    if cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def get_microsoft_client(client_id: str, client_secret: str):
    """Create MSAL public client application."""
    cache = get_token_cache()

    # Use PublicClientApplication for interactive login with personal accounts
    app = msal.PublicClientApplication(
        client_id,
        authority="https://login.microsoftonline.com/consumers",  # Personal accounts
        token_cache=cache,
    )
    return app, cache


def get_access_token(client_id: str, client_secret: str) -> str:
    """Get Microsoft Graph access token, prompting for login if needed."""
    app, cache = get_microsoft_client(client_id, client_secret)

    # Try to get token silently from cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            save_token_cache(cache)
            return result["access_token"]

    # Interactive login required
    print("Opening browser for Microsoft login...")
    result = app.acquire_token_interactive(
        scopes=SCOPES,
        prompt="select_account",
    )

    if "access_token" in result:
        save_token_cache(cache)
        return result["access_token"]

    error = result.get("error_description", result.get("error", "Unknown error"))
    raise Exception(f"Failed to get Microsoft token: {error}")


def get_unread_emails(access_token: str) -> list:
    """Fetch all unread emails from Outlook inbox."""
    headers = {"Authorization": f"Bearer {access_token}"}

    # Get unread messages, ordered by received date
    url = "https://graph.microsoft.com/v1.0/me/messages"
    params = {
        "$filter": "isRead eq false",
        "$orderby": "receivedDateTime desc",
        "$top": 50,  # Batch size
    }

    all_messages = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        all_messages.extend(data.get("value", []))

        # Handle pagination
        url = data.get("@odata.nextLink")
        params = None  # nextLink includes params

    return all_messages


def get_email_mime(access_token: str, message_id: str) -> bytes:
    """Get raw MIME content of an email."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/$value"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.content


def mark_as_read(access_token: str, message_id: str):
    """Mark an email as read in Outlook."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"

    response = requests.patch(url, headers=headers, json={"isRead": True})
    response.raise_for_status()
