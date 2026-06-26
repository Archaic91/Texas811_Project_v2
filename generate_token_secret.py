"""
generate_token_secret.py
========================
Run this ONCE on your local machine (after authenticating locally)
to produce the base64 string you paste into GitHub Secrets as GMAIL_TOKEN.

Usage:
    python generate_token_secret.py
"""

import base64

with open("token.pickle", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

print("\n=== Copy this value into GitHub Secrets as GMAIL_TOKEN ===\n")
print(encoded)
print("\n==========================================================\n")
