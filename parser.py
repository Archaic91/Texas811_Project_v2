import re


def extract_contractor_code(body):

    lines = body.splitlines()

    print("\n--- CONTRACTOR DEBUG START ---")

    # Print first few lines so we can SEE structure
    for i in range(min(5, len(lines))):
        print(f"LINE {i}: {lines[i]}")

    if not lines:
        print("NO LINES FOUND")
        return "UNKNOWN"

    # Normalize full body for safety matching
    full_text = body.upper()

    # =================================================
    # STRATEGY 1: HEADER MATCH (YOUR ORIGINAL LOGIC)
    # =================================================
    first_line = lines[0].upper().strip()

    prefix = "TEXAS811 LOCATE REQUEST FOR"

    if prefix in first_line:
        result = first_line.split(prefix)[-1].strip().replace(" ", "")

        # =================================================
        # FIX: NORMALIZE KNOWN CONTRACTOR VARIANTS
        # =================================================
        if result == "COWBY01":
            result = "COWBOY01"

        print(f"HEADER MATCH RESULT: {result}")
        return result

    # =================================================
    # STRATEGY 2: REGEX FALLBACK
    # =================================================
    match = re.search(r"LOCATE REQUEST FOR\s*([A-Z0-9\- ]+)", full_text)

    if match:
        result = match.group(1).replace(" ", "").replace("-", "").strip()

        # FIX AGAIN FOR REGEX PATH
        if result == "COWBY01":
            result = "COWBOY01"

        print(f"REGEX MATCH RESULT: {result}")
        return result

    # =================================================
    # STRATEGY 3: FUZZY KEYWORD MATCH
    # =================================================
    if "COWBOY" in full_text or "COWBY" in full_text:
        print("FUZZY MATCH HIT: COWBOY FOUND IN TEXT")
        return "COWBOY01"

    if "POTX" in full_text:
        print("FUZZY MATCH HIT: POTX FOUND IN TEXT")
        return "POTX01"

    print("NO MATCH FOUND → UNKNOWN")

    return "UNKNOWN"


# =====================================================
# SAFE HELPERS
# =====================================================

def safe_get(lines, index):
    return lines[index].strip() if len(lines) > index and lines[index] else ""


def safe_slice(line, start, end=None):
    if not line:
        return ""

    line = line.strip()

    if len(line) < start:
        return ""

    return line[start:end].strip() if end else line[start:].strip()

# =====================================================
# TICKET TYPE EXTRACTOR
# ADD THIS HERE
# =====================================================

def extract_ticket_type(body):

    lines = body.splitlines()

    if len(lines) > 4:

        line = lines[4]

        print(f"TICKET TYPE LINE: {line}")

        if "Type:" in line and "Date:" in line:

            ticket_type = (
                line
                .split("Type:")[1]
                .split("Date:")[0]
                .strip()
            )

            print(f"TICKET TYPE FOUND: {ticket_type}")

            return ticket_type

    print("TICKET TYPE NOT FOUND")

    return "Unknown"


# =====================================================
# MAIN FIELD EXTRACTOR
# =====================================================

def extract_fields(body):

    lines = body.splitlines()

    contractor = extract_contractor_code(body)
    ticket_type = extract_ticket_type(body)

    if not lines:
        return {
            "Contractor Code": contractor,
            "Ticket Number": "",
            "Ticket Type": "",
            "Date": "",
            "County": "",
            "City": "",
            "Street": "",
            "Intersection": ""
        }

    return {
        "Contractor Code": contractor,

        "Ticket Number":
            safe_slice(safe_get(lines, 2), 18, 36),

        "Ticket Type":
            ticket_type,

        "Date": (
            safe_get(lines, 4)
            .split("Date:")[-1]
            .strip()
            if "Date:" in safe_get(lines, 4)
            else ""
        ),

        "County":
            safe_slice(safe_get(lines, 22), 18, 36),

        "City":
            safe_slice(safe_get(lines, 23), 18),

        "Street":
            safe_slice(safe_get(lines, 24), 18),

        "Intersection":
            safe_slice(safe_get(lines, 25), 18),
    }
# =====================================================
# DEBUG TOOL
# =====================================================

def debug_parse(body):

    parsed = extract_fields(body)

    print("\n--- PARSER DEBUG ---")
    for k, v in parsed.items():
        print(f"{k}: {v}")

    return parsed
