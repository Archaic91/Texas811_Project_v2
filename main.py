import datetime
import os
import pandas as pd

from gmail_client import authenticate_gmail, fetch_messages, get_email_body
from parser import extract_fields, extract_contractor_code
from orchestrator import run_reporting_pipeline


# =====================================================
# CONFIG
# =====================================================

SENDER = "texas811locates@texas811.org"

RECIPIENTS = [
    "randy@pipelineoperators.com",
    "john@pipelineoperators.com",
    "onecalls1948@gmail.com"
]


# =====================================================
# MAIN PIPELINE
# =====================================================

def main():

    today = datetime.date.today()
    year = today.year
    month = today.strftime("%m")

    start_date = today.replace(day=1)
    end_date = today

    query = (
        f'from:{SENDER} '
        f'after:{start_date.strftime("%Y/%m/%d")} '
        f'before:{end_date.strftime("%Y/%m/%d")} '
        '-subject:audit'
    )

    service = authenticate_gmail()
    messages = fetch_messages(service, query)

    print(f"Fetched: {len(messages)} emails")

    data_rows = []

    for msg in messages:
        body = get_email_body(service, msg["id"])

        parsed = extract_fields(body)
        parsed["Contractor Code"] = extract_contractor_code(body)

        data_rows.append(parsed)

    data = pd.DataFrame(data_rows)

    if data.empty:
        print("⚠ No data found")
        return

    # --------------------------------------------------
    # Read sensitive values from environment variables
    # --------------------------------------------------
    sender_email = os.environ.get("SENDER_EMAIL") or os.environ.get("EMAIL_ADDRESS")
    sender_password = os.environ.get("SENDER_PASSWORD") or os.environ.get("EMAIL_PASSWORD")

    # REPORT_RECIPIENTS can be a comma-separated string in the secret,
    # e.g. "randy@pipelineoperators.com,john@pipelineoperators.com"
    recipients_env = os.environ.get("REPORT_RECIPIENTS")
    recipients = (
        [r.strip() for r in recipients_env.split(",") if r.strip()]
        if recipients_env
        else RECIPIENTS
    )

    if not sender_email or not sender_password:
        raise RuntimeError(
            "Missing EMAIL_ADDRESS or EMAIL_PASSWORD environment variables. "
            "Set them as GitHub Secrets (or in your local .env)."
        )

    data_bundle = {
        "potx": data[data["Contractor Code"] == "POTX01"].copy(),
        "cowboy": data[data["Contractor Code"] == "COWBOY01"].copy(),
        "month": month,
        "year": year
    }

    result = run_reporting_pipeline(
        data_bundle,
        auto_email=True,
        recipients=recipients,
        sender_email=sender_email,
        sender_password=sender_password
    )

    print("✔ Pipeline Complete")


if __name__ == "__main__":
    main()
