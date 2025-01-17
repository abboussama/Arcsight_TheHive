import json
import os
from datetime import datetime
from uuid import uuid4
import requests

# Define TheHive instance details
thehive_url = "{THEHIVE_URL}"
thehive_api_key = "{THE_HIVE_API}"
tenant_name = ""  # Specify the tenant name here
client_name = ""
source_name = ""
tags = []
type_name = ""
useSSL = False
# File to store alert metadata
alert_metadata_file = "alerts_metadata.json"

# Load existing alert metadata from file
def load_alert_metadata():
    if os.path.exists(alert_metadata_file):
        with open(alert_metadata_file, "r") as f:
            return json.load(f)
    return []


# Save alert metadata to file
def save_alert_metadata(metadata):
    with open(alert_metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)


# Generate a new unique alert ID
def generate_alert_id(existing_metadata):
    if not existing_metadata:
        return 1
    return max(alert["id"] for alert in existing_metadata) + 1


# Check for duplicate alerts
def is_duplicate_alert(metadata, id, description):
    for alert in metadata:
        if alert["id"] == id and alert["description"] == description:
            return True
    return False


# Create a new alert
def create_alert(id, title, description, severity, ct):
    metadata = load_alert_metadata()

    # Check for duplicates
    if is_duplicate_alert(metadata, id , description):
        print("An alert with the same title and description already exists.")
        return False

    # Generate a new alert ID and unique sourceRef
    new_id = id
    new_source_ref = str(uuid4())

    alert = {
        "id": new_id,
        "title": title,
        "type": type_name,
        "source": source_name,
        "sourceRef": new_source_ref,
        "description": description,
        "severity": severity,
        "tags": tags,
        "occurDate": ct,
        "date": int(datetime.now().timestamp() * 1000)
    }

    try:
        # Send the POST redquest to create the alert
        response = requests.post(
            f"{thehive_url}/api/alert",  # Adjusted endpoint for TheHive v5
            json=alert,
            headers={
                "Authorization": f"Bearer {thehive_api_key}",
                "X-TheHive-Tenant": tenant_name,
            },
            verify=useSSL
        )

        # Raise an error if the response indicates failure
        response.raise_for_status()

        # Parse the JSON response
        created_alert = response.json()

        # Save alert details to metadata
        metadata.append({
            "id": new_id,
            "title": title,
            "sourceRef": new_source_ref,
            "description": description,
            "alert_id": created_alert.get("id"),
        })
        save_alert_metadata(metadata)

        print("Alert successfully created!")
        print("Alert details:", json.dumps(created_alert, indent=4))
        return True

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.text}")
        return False
    except Exception as err:
        print(f"An error occurred: {err}")
        return False

def create_bulk(alerts):
    for alert in alerts:
        id = alert["id"]
        title = alert['name']
        ct = alert["ET_unix"]
        severity = alert["severity_numeric"]
        description = alert["description"]
        create_alert(id, title, description, severity, ct)


# if __name__ == "__main__":
#     title = "this is a test 9"
#     description = "testing 9"
#     id = 12529
#     severity = 4
#     ct = 1737101947
#     create_alert(id, title, description, severity, ct)
