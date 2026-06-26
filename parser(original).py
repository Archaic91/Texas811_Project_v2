def extract_contractor_code(body):

    lines = body.splitlines()

    if not lines:
        return "UNKNOWN"

    first_line = lines[0].upper().strip()

    prefix = "TEXAS811 LOCATE REQUEST FOR"

    if prefix in first_line:
        return first_line.split(prefix)[-1].strip().replace(" ", "")

    return "UNKNOWN"


def extract_fields(body):

    lines = body.splitlines()

    contractor = extract_contractor_code(body)

    return {
        "Contractor Code": contractor,
        "Ticket Number": lines[2][18:36].strip() if len(lines) > 2 else "",
        "Date": lines[4].split("Date:")[-1].strip() if len(lines) > 4 else "",
        "County": lines[22][18:36].strip() if len(lines) > 22 else "",
        "City": lines[23][18:].strip() if len(lines) > 23 else "",
        "Street": lines[24][18:].strip() if len(lines) > 24 else "",
        "Intersection": lines[25][18:].strip() if len(lines) > 25 else ""
    }
