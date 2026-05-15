# Exchange to Gmail Sync - Setup Guide

This tool syncs unread emails from Microsoft Outlook/Exchange to Gmail, preserving all headers and timestamps.

## Prerequisites

- Python 3.8+
- A personal Microsoft account (Outlook.com, Hotmail, etc.)
- A Gmail account

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
```

---

## Step 1: Microsoft Azure App Registration

1. Go to [Azure Portal - App Registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)

2. Click **New registration**

3. Fill in the details:
   - **Name:** `email-sync` (or any name you prefer)
   - **Supported account types:** Select **Personal Microsoft accounts only**
   - **Redirect URI:**
     - Select **Mobile and desktop applications** from dropdown
     - Enter: `http://localhost`

4. Click **Register**

5. On the app overview page, copy the **Application (client) ID**
   - Save this as `MICROSOFT_CLIENT_ID` in your `.env` file

6. Go to **Certificates & secrets** (left sidebar)
   - Click **New client secret**
   - Add a description (e.g., "email-sync")
   - Choose an expiry period
   - Click **Add**
   - Copy the **Value** (not the Secret ID)
   - Save this as `MICROSOFT_CLIENT_SECRET` in your `.env` file

7. Go to **API permissions** (left sidebar)
   - Click **Add a permission**
   - Select **Microsoft Graph**
   - Select **Delegated permissions**
   - Search for `Mail.ReadWrite` and check it
   - Click **Add permissions**

> **Note:** You do NOT need to "Grant admin consent" for personal accounts. You'll consent when you first run the app.

---

## Step 2: Google Cloud OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)

2. Create a new project or select an existing one

3. **Enable the Gmail API:**
   - Go to [Gmail API Library](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
   - Click **Enable**

4. **Configure OAuth Consent Screen:**
   - Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
   - Select **External** and click **Create**
   - Fill in required fields:
     - **App name:** `email-sync`
     - **User support email:** Your email
     - **Developer contact email:** Your email
   - Click **Save and Continue**
   - Skip "Scopes" - click **Save and Continue**
   - Under **Test users**, click **Add Users**
   - Add your Gmail address (the one you'll sync to)
   - Click **Save and Continue**

5. **Create OAuth Credentials:**
   - Go to [Credentials](https://console.cloud.google.com/apis/credentials)
   - Click **Create Credentials** > **OAuth client ID**
   - **Application type:** Desktop app
   - **Name:** `email-sync`
   - Click **Create**
   - Copy the **Client ID** → save as `GOOGLE_CLIENT_ID` in `.env`
   - Copy the **Client Secret** → save as `GOOGLE_CLIENT_SECRET` in `.env`

---

## Step 3: Configure Environment

Edit your `.env` file with all four values:

```
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

## Step 4: First Run

```bash
python sync.py
```

On first run:
1. A browser window opens for Microsoft login - sign in and accept permissions
2. A browser window opens for Google login - sign in and accept permissions
3. Tokens are cached locally (`ms_token_cache.json` and `google_token.json`)

Future runs will be automatic with no browser interaction.

---

## Usage

```bash
# Sync all unread emails from Outlook to Gmail
python sync.py
```

The script will:
- Fetch all unread emails from your Outlook inbox
- Copy each email to Gmail (inbox, marked as unread)
- Mark the email as read in Outlook
- Preserve all original headers, timestamps, and threading

---

## Troubleshooting

### "Access blocked: app has not completed Google verification"
- Make sure you added your Gmail address as a test user in the OAuth consent screen
- The app must be in "Testing" status (not published)

### "AADSTS..." errors from Microsoft
- Verify your redirect URI is exactly `http://localhost`
- Make sure you selected "Personal Microsoft accounts only"

### Token expired
- Delete the token files and run again:
  ```bash
  rm ms_token_cache.json google_token.json
  python sync.py
  ```

---

## Security Notes

- Never commit your `.env` file or token files to version control
- The `.gitignore` file is configured to exclude these sensitive files
- Tokens are stored locally and grant access to your email - keep them secure
