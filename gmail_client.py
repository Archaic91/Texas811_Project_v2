import os
import json
import pickle
import base64
import tempfile
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# =====================================================
# CONFIG
# =====================================================

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# =====================================================
# AUTHENTICATION
# =====================================================

def authenticate_gmail():
    """
    Handles OAuth login + token refresh.

    In GitHub Actions (CI): reads token from GOOGLE_TOKEN_PICKLE env var
    (base64-encoded pickle) and credentials from GOOGLE_CREDENTIALS env var (JSON string).
    Locally: falls back to token.pickle file and credentials.json, runs browser flow if needed.
    """

    creds = None

    # --------------------------------------------------
    # CI PATH: load token from environment variable
    # --------------------------------------------------
    token_b64 = os.environ.get("GOOGLE_TOKEN_PICKLE")

    if token_b64:
        creds = pickle.loads(base64.b64decode(token_b64))

    # --------------------------------------------------
    # LOCAL PATH: load from file
    # --------------------------------------------------
    elif os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # --------------------------------------------------
    # Refresh if expired (works in both CI and local)
    # --------------------------------------------------
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

        # Persist refreshed token locally if running locally
        if not token_b64 and os.path.exists("token.pickle"):
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

    # --------------------------------------------------
    # Interactive browser flow (local only, never in CI)
    # --------------------------------------------------
    elif not creds or not creds.valid:
        if os.environ.get("CI"):
            raise RuntimeError(
                "No valid Gmail token found in CI environment. "
                "Set the GOOGLE_TOKEN_PICKLE secret. See README for setup steps."
            )

        # Write credentials.json from env var if provided, otherwise use file
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        if creds_json:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
                tmp.write(creds_json)
                creds_file = tmp.name
        else:
            creds_file = "credentials.json"

        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

        if creds_json:
            os.unlink(creds_file)

    return build("gmail", "v1", credentials=creds)


# =====================================================
# PAGINATED MESSAGE FETCH
# =====================================================

def fetch_messages(service, query, max_results=None):
    """
    Fetch ALL messages using pagination (fixes 100-limit issue)
    """

    messages = []
    page_token = None

    while True:

        response = service.users().messages().list(
            userId="me",
            q=query,
            pageToken=page_token,
            maxResults=500
        ).execute()

        batch = response.get("messages", [])
        messages.extend(batch)

        page_token = response.get("nextPageToken")

        print(f"Fetched: {len(messages)}")

        if not page_token:
            break

        if max_results and len(messages) >= max_results:
            break

        time.sleep(0.2)  # gentle rate limit

    return messages


# =====================================================
# EMAIL BODY EXTRACTION
# =====================================================

def get_email_body(service, msg_id):
    """
    Extract full email payload safely
    """

    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    payload = msg.get("payload", {})
    parts = payload.get("parts", [])

    # -------------------------------------------------
    # Try multipart first
    # -------------------------------------------------
    if parts:
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    # -------------------------------------------------
    # Fallback: raw body
    # -------------------------------------------------
    body = payload.get("body", {}).get("data")

    if body:
        return base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")

    return ""


# =====================================================
# OPTIONAL: SIMPLE QUERY BUILDER HELP
# =====================================================

def build_query(sender, start_date, end_date):
    return (
        f"from:{sender} "
        f"after:{start_date} "
        f"before:{end_date} "
        "-subject:audit"
    )
