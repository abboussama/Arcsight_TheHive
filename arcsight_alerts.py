import json
import random
import string
import requests
from getAlerts import get_alerts
from main import create_bulk
import warnings
warnings.filterwarnings("ignore")



#Enter the credentials of the ESM user in here =
user = ""
password = ""
esm_hostname = ""


# Generate a random string of 32 uppercase letters (RAN block)
def generate_random_string(length=32):
    return ''.join(random.choices(string.ascii_uppercase, k=length))

# Send an HTTP POST request with a session for cookie management
def send_http_request(session, url, method, headers, payload, timeout=10):
    try:
        response = session.request(method, url, headers=headers, data=payload, timeout=timeout, verify=False)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None

# Parse a value from a response using left and right delimiters
def parse_value(input_text, left_delim, right_delim):
    try:
        start = input_text.index(left_delim) + len(left_delim)
        end = input_text.index(right_delim, start)
        return input_text[start:end]
    except ValueError:
        print(f"Failed to parse value with delimiters '{left_delim}' and '{right_delim}'")
        return None

# Main execution
if __name__ == "__main__":
    # Create a session to manage cookies
    session = requests.Session()

    # Generate random string for RAN
    random_string = generate_random_string()
    #print(f"Generated Random String: {random_string}")

    # HTTP request to login
    url_login = f"https://{esm_hostname}/www/core-service/gwt/LoginService"
    headers_login = {
        "Host": f"{esm_hostname}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "*/*",
        "GWT-Method": "login",
        "ArcSight-Client": "ACC",
        "X-GWT-Permutation": random_string,
        "X-GWT-Module-Base": f"https://{esm_hostname}/www/ui-phoenix/com.arcsight.phoenix.PhoenixLauncher/",
        "Content-Length": "273",
        "Origin": f"{esm_hostname}",
        "Content-Type": "text/x-gwt-rpc; charset=utf-8"
    }
    payload_login = (
        f"7|0|7|https://{esm_hostname}/www/ui-phoenix/com.arcsight.phoenix.PhoenixLauncher/|4D0A049F53B67145A7E76738739AE51D|com.arcsight.product.core.service.v1.client.gwt.api.LoginService|login|java.lang.String/2004016611|{user}|{password}|1|2|3|4|3|5|5|5|0|6|7|"
    )
    response_login = send_http_request(session, url_login, "POST", headers_login, payload_login, timeout=15)

    # Parse the TOKEN from login response
    if response_login:
        token = parse_value(response_login.text, "//OK[1,[\"", "\"")
        #print(f"Parsed Token: {token}")

        # HTTP request for notifications
        url_notifications = f"{esm_hostname}/www/esmclient-service/gwt/NotificationDestinationService"
        headers_notifications = {
            "Host": f"{esm_hostname}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "*/*",
            "Content-Type": "text/x-gwt-rpc; charset=utf-8",
            "GWT-Method": "getUsersNotificationAlerts",
            "ArcSight-Client": "ACC",
            "X-GWT-Permutation": random_string,
            "X-GWT-Module-Base": f"{esm_hostname}/www/ui-phoenix/com.arcsight.phoenix.PhoenixLauncher/",
            "Content-Length": "791",
            "Origin": f"{esm_hostname}",
            "Referer": f"{esm_hostname}/www/ui-phoenix/com.arcsight.phoenix.PhoenixLauncher/"
        }
        payload_notifications_one = (
            f"7|0|14|{esm_hostname}/www/ui-phoenix/com.arcsight.phoenix.PhoenixLauncher/"
            "|B7BBAE1EDB98A61847D68F19600E4F1E|com.arcsight.product.esmclient.service.v1.client.gwt.api."
            "NotificationDestinationService|getUsersNotificationAlerts|java.lang.String/2004016611|com.arcsight.product."
            "esmclient.service.v1.model.paging.PagingListRequest/2455014551|java.util.List|"
            f"{token}|java.util.ArrayList/4159755760|com.arcsight.product.esmclient.service.v1.model.sorting.SortInfo/"
            "776413725|createTime|com.arcsight.product.esmclient.service.v1.model.sorting.SortOrder/1726127846|java.util."
            "Collections$SingletonList/1586180994|com.arcsight.product.esmclient.service.v1.model.notification."
            "NotificationState/482525281|1|2|3|4|3|5|6|7|8|6|50|9|1|10|11|12|1|0|13|14|5|"
        )
        response_notifications_one = send_http_request(session, url_notifications, "POST", headers_notifications, payload_notifications_one, timeout=30)

        # Parse Pending and Resolved from notifications response
        if response_notifications_one:
            response = str(response_notifications_one.text)
            #print(f'Raw response: {response}\n\n\n')
            alerts = get_alerts(response)
            result = json.dumps(alerts, indent=4)
            print(f'\n\n\nThese are the found alerts: {result}')
            create_bulk(alerts)
        else:
            print("Failed to get pending alerts.")

        payload_notifications_two = (
            f"7|0|14|{esm_hostname}/www/ui-phoenix/com.arcsight.phoenix.PhoenixLauncher/|B7BBAE1EDB98A61847D68F19600E4F1E|com.arcsight.product.esmclient.service.v1.client.gwt.api.NotificationDestinationService|getUsersNotificationAlerts|java.lang.String/2004016611|com.arcsight.product.esmclient.service.v1.model.paging.PagingListRequest/2455014551|java.util.List|{token}|java.util.ArrayList/4159755760|com.arcsight.product.esmclient.service.v1.model.sorting.SortInfo/776413725|createTime|com.arcsight.product.esmclient.service.v1.model.sorting.SortOrder/1726127846|java.util.Collections$SingletonList/1586180994|com.arcsight.product.esmclient.service.v1.model.notification.NotificationState/482525281|1|2|3|4|3|5|6|7|8|6|50|9|1|10|11|12|1|0|13|14|2|"
        )
        response_notifications_two = send_http_request(session, url_notifications, "POST", headers_notifications,
                                                       payload_notifications_two, timeout=20)

        # Parse Pending and Resolved from notifications response
        if response_notifications_two:
            response = str(response_notifications_two.text)
            print(f'Raw response: {response}\n\n\n')
            alerts = get_alerts(response)
            result = json.dumps(alerts, indent=4)
            print(f'\n\n\nThese are the found Undeliverable alerts: {result}')
            create_bulk(alerts)
        else:
            print("Failed to get Undeliverable alerts")

    else:
        print("Failed to get login response.")

















