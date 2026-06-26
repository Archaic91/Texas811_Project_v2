import re


def extract_contractor_code(body):

    lines = body.splitlines()

    if not lines:
        return "UNKNOWN"

    full_text = body.upper()

    # =================================================
    # STRATEGY 1: HEADER MATCH
    # =================================================
    first_line = lines[0].upper().strip()
    prefix = "TEXAS811 LOCATE REQUEST FOR"

    if prefix in first_line:
        result = first_line.split(prefix)[-1].strip().replace(" ", "")

        if result == "COWBY01":
            result = "COWBOY01"

        return result

    # =================================================
    # STRATEGY 2: REGEX FALLBACK
    # =================================================
    match = re.search(r"LOCATE REQUEST FOR\s*([A-Z0-9\- ]+)", full_text)

    if match:
        result = match.group(1).replace(" ", "").replace("-", "").strip()

        if result == "COWBY01":
            result = "COWBOY01"

        return result

    # =================================================
    # STRATEGY 3: FUZZY KEYWORD MATCH
    # =================================================
    if "COWBOY" in full_text or "COWBY" in full_text:
        return "COWBOY01"

    if "POTX" in full_text:
        return "POTX01"

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
# =====================================================

def extract_ticket_type(body):

    lines = body.splitlines()

    if len(lines) > 4:
        line = lines[4]

        if "Type:" in line and "Date:" in line:
            ticket_type = (
                line
                .split("Type:")[1]
                .split("Date:")[0]
                .strip()
            )
            return ticket_type

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