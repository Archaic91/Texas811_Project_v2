import os
import pandas as pd

from excel_builder import (
    build_potx_workbook,
    build_generic_workbook,
    build_client_pack,
    format_report_name
)

from email_sender import send_email_with_attachments


# =====================================================
# ORCHESTRATOR
# =====================================================

def run_reporting_pipeline(
    data_bundle,
    base_dir="Reports",
    auto_email=False,
    recipients=None,
    sender_email=None,
    sender_password=None
):

    potx_data = data_bundle["potx"]
    cowboy_data = data_bundle["cowboy"]
    month = data_bundle["month"]
    year = data_bundle["year"]

    month_folder = os.path.join(base_dir, str(year), f"{year}-{month}")
    os.makedirs(month_folder, exist_ok=True)

    potx_file = os.path.join(month_folder, format_report_name("POTX", month, year))
    cowboy_file = os.path.join(month_folder, format_report_name("Cowboy", month, year))

    client_file = None

    # -------------------------
    # POTX REPORT
    # -------------------------
    if not potx_data.empty:
        with pd.ExcelWriter(potx_file, engine="openpyxl") as writer:
            build_potx_workbook("POTX01", potx_data, writer, month, year)

    else:
        potx_file = None

    # -------------------------
    # COWBOY REPORT
    # -------------------------
    if not cowboy_data.empty:
        with pd.ExcelWriter(cowboy_file, engine="openpyxl") as writer:
            build_generic_workbook("COWBOY01", cowboy_data, writer, month, year)

    else:
        cowboy_file = None

    # -------------------------
    # CLIENT PACK
    # -------------------------
    if not potx_data.empty:
        client_file = build_client_pack(
            source_file=potx_file,
            base_dir=base_dir,
            contractor="POTX OxyChem",
            month=month,
            year=year
        )

    # -------------------------
    # EMAIL AUTOMATION
    # -------------------------
    if auto_email and recipients and sender_email and sender_password:

        attachments = list(filter(None, [
            potx_file,
            cowboy_file,
            client_file
        ]))

        send_email_with_attachments(
            recipients=recipients,
            subject=f"One Call Reports - {month}/{year}",
            body=f"Automated reports for {month}/{year}",
            file_paths=attachments,
            sender_email=sender_email,
            sender_password=sender_password
        )

        print("✔ Email Sent")

    return {
        "potx_file": potx_file,
        "cowboy_file": cowboy_file,
        "client_file": client_file,
        "month": month,
        "year": year
    }
