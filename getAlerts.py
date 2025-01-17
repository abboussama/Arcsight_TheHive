from datetime import datetime
import re
import json
import time


def parse_alerts(text):
    lines = text.splitlines()

    current_severity = "Unknown"
    collecting_block = False
    block_lines = []
    alerts = []

    for line in lines:
        # Clean up punctuation, etc.
        line_clean = line.strip('",: \t')

        # Check for severity
        if line_clean.lower() in ("high", "medium", "low", "critical", "severe", "very high"):
            if line_clean.lower() == "very high":
                current_severity = "Very High"
            else:
                current_severity = line_clean.capitalize()

        # Start collecting a SecurityEvent block
        if "SecurityEvent=[" in line:
            collecting_block = True
            block_lines = [line]
            continue

        # If we're in a block, keep collecting until we see a "]"
        if collecting_block:
            block_lines.append(line)
            if "]" in line:
                collecting_block = False
                block_text = "\n".join(block_lines)

                alert_data = parse_single_block(block_text)
                alert_data["severity"] = current_severity
                alerts.append(alert_data)
                block_lines = []

    return alerts

def parse_single_block(block_text):
    id_match = re.search(r'id\s*=\s*(\d+)', block_text)
    event_id = id_match.group(1) if id_match else "Unknown"

    mrt_match = re.search(r'MRT\s*=\s*(.+)', block_text)
    mrt = mrt_match.group(1).strip() if mrt_match else "Unknown"

    et_match = re.search(r'ET\s*=\s*(.+)', block_text)
    et_ = et_match.group(1).strip() if et_match else "Unknown"

    st_match = re.search(r'ST\s*=\s*(.+)', block_text)
    st_ = st_match.group(1).strip() if st_match else "Unknown"

    type_match = re.search(r'type\s*=\s*(\d+)', block_text)
    typ = type_match.group(1) if type_match else "Unknown"

    name_match = re.search(r'name\s*=\s*(.+)', block_text)
    name_ = name_match.group(1).strip() if name_match else "Unknown"

    return {
        "id": event_id,
        "MRT": mrt,
        "ET": et_,
        "ST": st_,
        "type": typ,
        "name": name_,
        "severity": "Unknown",  # Overridden by parse_alerts
    }
# Example usage
def normalize(alerts):
    """
    Given a list of alert dictionaries, normalize:
      - severity -> numeric (1=Low, 2=Medium, 3=High, 4=Critical)
      - ET -> Unix time
    """
    severity_map = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
        "severe": 4,
        "very high": 4
    }

    for alert in alerts:
        # 1) Normalize severity
        sev_lower = alert["severity"].lower()
        numeric_sev = severity_map.get(sev_lower, 0)  # 0 if not matched
        alert["severity_numeric"] = numeric_sev
        EVENT_ID = alert["id"]
        alert["description"] = f"Please verify in ESM using the event ID: eventId = \"{EVENT_ID}\""
        original_et = alert["ET"]
        if original_et and original_et != "Unknown":
            # remove trailing "WEST" or any timezone block if present
            cleaned_et = re.sub(r"\s+WEST\s+", " ", original_et)
            try:
                dt = datetime.strptime(cleaned_et, "%a %b %d %H:%M:%S %Y")
                unix_ts = int(time.mktime(dt.timetuple()))
                alert["ET_unix"] = unix_ts
            except ValueError:
                alert["ET_unix"] = None
        else:
            alert["ET_unix"] = None

    return alerts

def get_alerts(response_text):
    response_text = response_text.replace('\\u003D', '=')
    response_text = response_text.replace('\\n', '\n')
    #print(f'\n\n\n\nResponse after being passed and after replacing \\u003D with = : {response_text}')
    result = response_text.replace('","', '\n')

    # Debug
    #print("After decode:\n", result)
    alerts = parse_alerts(result)
    alerts = normalize(alerts)
    print(json.dumps(alerts, indent=4))
    return alerts