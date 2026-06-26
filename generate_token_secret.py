import base64
import sys

with open("token.pickle", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

# Write to a file so there's no copy/paste issues
with open("token_secret.txt", "w") as out:
    out.write(encoded)

print(f"Written to token_secret.txt ({len(encoded)} chars, no newlines)")